/** Extra real-source geometry inspectors for HORIZEN. No simulated preview. */
const MAX_BYTES=64*1024*1024,MAX_PREVIEW=180000;

function inspectFiniteTriangle(values){
  if(values.length!==9||values.some(v=>!Number.isFinite(v)))throw new Error('STL has non-finite or missing triangle coordinates.');
}

export function inspectSTL(buffer){
  if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<84||buffer.byteLength>MAX_BYTES)throw new Error('STL missing or exceeds 64 MiB.');
  const bytes=new Uint8Array(buffer),view=new DataView(buffer),count=view.getUint32(80,true);
  const binary=count>0&&count<=1_000_000&&84+count*50===buffer.byteLength;
  let triangles=0,vertices=[],mode='';
  if(binary){
    mode='binary';const step=Math.max(1,Math.ceil(count/MAX_PREVIEW));
    for(let t=0;t<count;t++){
      const start=84+t*50+12,tri=[];
      for(let j=0;j<9;j++)tri.push(view.getFloat32(start+j*4,true));
      inspectFiniteTriangle(tri);
      if(t%step===0)vertices.push(...tri);
    }
    triangles=count;
  }else{
    if(!new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(0,Math.min(80,bytes.length))).trimStart().toLowerCase().startsWith('solid'))throw new Error('Invalid binary STL triangle count/length.');
    const source=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
    if(source.includes('\0')||!/^\s*solid\b/i.test(source)||!/^\s*endsolid\b/im.test(source))throw new Error('Malformed ASCII STL.');
    mode='ASCII';let pending=[];
    for(const line of source.split(/\r?\n/)){
      if(!/^\s*vertex\b/i.test(line))continue;
      const fields=line.trim().split(/\s+/);
      if(fields.length!==4)throw new Error('Invalid ASCII STL vertex.');
      const values=fields.slice(1).map(Number);
      if(values.some(v=>!Number.isFinite(v)))throw new Error('Non-finite ASCII STL vertex.');
      pending.push(...values);
      if(pending.length===9){inspectFiniteTriangle(pending);vertices.push(...pending);pending=[];triangles++;if(triangles>1_000_000)throw new Error('STL has too many triangles.');}
    }
    if(pending.length||!triangles)throw new Error('ASCII STL does not contain complete triangles.');
    if(triangles>MAX_PREVIEW){const step=Math.ceil(triangles/MAX_PREVIEW),reduced=[];for(let t=0;t<triangles;t+=step)reduced.push(...vertices.slice(t*9,t*9+9));vertices=reduced;}
  }
  return {format:'STL',vertices:Float32Array.from(vertices),stats:{meshes:1,sourceTriangles:triangles,previewTriangles:vertices.length/9,materials:0,animations:0,skins:0,mode,note:'Real local STL triangles, untextured browser preview. No units, print-quality, thickness, Blender, Godot or gameplay verification.'}};
}

export function embeddedGLTFtoGLB(text){
  if(typeof text!=='string'||!text.length||text.length>MAX_BYTES)throw new Error('Invalid or oversized glTF JSON.');
  let doc;try{doc=JSON.parse(text);}catch{throw new Error('Invalid glTF JSON.');}
  if(doc?.asset?.version!=='2.0'||!Array.isArray(doc.buffers)||doc.buffers.length!==1)throw new Error('Only glTF 2.0 with one embedded binary buffer is supported.');
  const entry=doc.buffers[0],uri=entry?.uri;
  if(typeof uri!=='string'||!/^data:application\/(?:octet-stream|gltf-buffer);base64,/i.test(uri))throw new Error('External glTF .bin/texture URIs are not loaded; select a self-contained GLB or embedded glTF.');
  const encoded=uri.slice(uri.indexOf(',')+1);
  if(encoded.length>MAX_BYTES*4/3||!/^[A-Za-z0-9+/]*={0,2}$/.test(encoded)||encoded.length%4!==0)throw new Error('Malformed or oversized embedded glTF buffer.');
  let decoded;try{decoded=atob(encoded);}catch{throw new Error('Invalid embedded glTF base64 data.');}
  const bin=new Uint8Array(decoded.length);for(let i=0;i<decoded.length;i++)bin[i]=decoded.charCodeAt(i);
  if(!Number.isInteger(entry.byteLength)||entry.byteLength<1||entry.byteLength>bin.length||bin.length-entry.byteLength>3)throw new Error('glTF binary byte length mismatch.');
  const newDoc={...doc,buffers:[{...entry,byteLength:entry.byteLength}]};delete newDoc.buffers[0].uri;
  const jsonData=new TextEncoder().encode(JSON.stringify(newDoc));const jsonLen=Math.ceil(jsonData.length/4)*4,binLen=Math.ceil(bin.length/4)*4;
  const total=12+8+jsonLen+8+binLen;if(total>MAX_BYTES)throw new Error('Expanded glTF exceeds 64 MiB.');
  const result=new ArrayBuffer(total),v=new DataView(result),target=new Uint8Array(result);v.setUint32(0,0x46546c67,true);v.setUint32(4,2,true);v.setUint32(8,total,true);v.setUint32(12,jsonLen,true);v.setUint32(16,0x4e4f534a,true);target.fill(32,20,20+jsonLen);target.set(jsonData,20);v.setUint32(20+jsonLen,binLen,true);v.setUint32(24+jsonLen,0x004e4942,true);target.set(bin,28+jsonLen);
  return result;
}
