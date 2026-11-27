/** Strict local geometry inspection, not a Blender/Godot asset verifier. */
const GLB_MAGIC=0x46546c67,JSON_CHUNK=0x4e4f534a,BIN_CHUNK=0x004e4942;
const MAX_SOURCE_BYTES=64*1024*1024,MAX_PREVIEW_TRIANGLES=180000;
const identity=()=>[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
function multiply(a,b){const m=new Array(16).fill(0);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)m[c*4+r]+=a[k*4+r]*b[c*4+k];return m;}
function transform(m,x,y,z){return [m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]];}
function nodeMatrix(n){if(n.matrix){if(n.matrix.length!==16)throw new Error('Invalid node matrix.');return n.matrix;}const [x,y,z,w]=n.rotation||[0,0,0,1],t=n.translation||[0,0,0],s=n.scale||[1,1,1];return [ (1-2*y*y-2*z*z)*s[0],(2*x*y+2*z*w)*s[0],(2*x*z-2*y*w)*s[0],0,(2*x*y-2*z*w)*s[1],(1-2*x*x-2*z*z)*s[1],(2*y*z+2*x*w)*s[1],0,(2*x*z+2*y*w)*s[2],(2*y*z-2*x*w)*s[2],(1-2*x*x-2*y*y)*s[2],0,t[0],t[1],t[2],1];}
function posAccessor(doc,bin,index){const a=doc.accessors?.[index],v=doc.bufferViews?.[a?.bufferView];if(!a||!v||a.type!=='VEC3'||a.componentType!==5126||a.sparse||v.buffer!==0)throw new Error('Unsupported position accessor (requires embedded FLOAT VEC3).');if(!Number.isInteger(a.count)||a.count<1||a.count>1500000)throw new Error('Invalid position count.');const start=(v.byteOffset||0)+(a.byteOffset||0),stride=v.byteStride||12;if(stride<12||stride>256||start<0||start+(a.count-1)*stride+12>bin.byteLength)throw new Error('Position accessor outside embedded data.');const dv=new DataView(bin.buffer,bin.byteOffset,bin.byteLength);const out=[];for(let i=0;i<a.count;i++){const o=start+i*stride;const x=dv.getFloat32(o,true),y=dv.getFloat32(o+4,true),z=dv.getFloat32(o+8,true);if(![x,y,z].every(Number.isFinite))throw new Error('Non-finite vertex position.');out.push([x,y,z]);}return out;}
function indexAccessor(doc,bin,index){const a=doc.accessors?.[index],v=doc.bufferViews?.[a?.bufferView];if(!a||!v||a.type!=='SCALAR'||a.sparse||v.buffer!==0)throw new Error('Unsupported indices accessor.');const sizes={5121:1,5123:2,5125:4},size=sizes[a.componentType];if(!size)throw new Error('Unsupported index component type.');const start=(v.byteOffset||0)+(a.byteOffset||0),stride=v.byteStride||size;if(!Number.isInteger(a.count)||a.count>5000000||stride<size||start+(a.count-1)*stride+size>bin.byteLength)throw new Error('Index accessor outside embedded data.');const dv=new DataView(bin.buffer,bin.byteOffset,bin.byteLength),out=[];for(let i=0;i<a.count;i++){const o=start+i*stride;out.push(size===1?dv.getUint8(o):size===2?dv.getUint16(o,true):dv.getUint32(o,true));}return out;}
export function inspectGLB(buffer){
  if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<20||buffer.byteLength>MAX_SOURCE_BYTES)throw new Error('GLB missing or exceeds 64 MiB browser inspection limit.');
  const d=new DataView(buffer);if(d.getUint32(0,true)!==GLB_MAGIC||d.getUint32(4,true)!==2||d.getUint32(8,true)!==buffer.byteLength)throw new Error('Invalid GLB v2 header or length.');
  let offset=12,doc=null,bin=null;while(offset+8<=buffer.byteLength){const size=d.getUint32(offset,true),kind=d.getUint32(offset+4,true);offset+=8;if(size%4||offset+size>buffer.byteLength)throw new Error('Malformed GLB chunk.');const bytes=new Uint8Array(buffer,offset,size);if(kind===JSON_CHUNK&&!doc){try{doc=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes).replace(/\0+$/g,''));}catch{throw new Error('Invalid GLB JSON chunk.');}}if(kind===BIN_CHUNK&&!bin)bin=bytes;offset+=size;}
  if(offset!==buffer.byteLength||!doc||!bin||doc.asset?.version!=='2.0')throw new Error('GLB must contain glTF 2.0 JSON and embedded BIN data.');
  const req=doc.extensionsRequired||[];if(req.length)throw new Error(`Required GLB extensions need dedicated decoder: ${req.slice(0,5).join(', ')}`);
  if((doc.buffers||[]).some(b=>b.uri))throw new Error('External buffers are not allowed for isolated local preview.');
  let sourceTriangles=0,primitiveCount=0,ignoredModes=0;const primitives=[];
  for(let mi=0;mi<(doc.meshes||[]).length;mi++)for(const p of(doc.meshes[mi].primitives||[])){
    primitiveCount++;if((p.mode??4)!==4){ignoredModes++;continue;}if(p.attributes?.POSITION===undefined)continue;
    const vertices=posAccessor(doc,bin,p.attributes.POSITION);const indices=p.indices===undefined?vertices.map((_,i)=>i):indexAccessor(doc,bin,p.indices);if(indices.length%3)throw new Error('Triangle indices must be grouped in threes.');for(const idx of indices)if(idx>=vertices.length)throw new Error('Triangle references missing vertex.');
    sourceTriangles+=indices.length/3;primitives.push({mesh:mi,vertices,indices});
  }
  const output=[],nodes=doc.nodes||[],scene=doc.scenes?.[doc.scene??0],draws=[],byMesh=new Map();
  for(const prim of primitives){if(!byMesh.has(prim.mesh))byMesh.set(prim.mesh,[]);byMesh.get(prim.mesh).push(prim);}
  let sceneTriangles=0,visits=0;
  function queuePrimitive(prim,mat){if(draws.length>=100000)throw new Error('GLB scene draw limit exceeded.');draws.push({prim,mat});sceneTriangles+=prim.indices.length/3;if(!Number.isSafeInteger(sceneTriangles))throw new Error('GLB scene triangle count overflow.');}
  function walk(id,parent,ancestors){if(++visits>100000||ancestors.size>=256)throw new Error('GLB scene graph inspection limit exceeded.');if(!Number.isInteger(id)||!nodes[id]||ancestors.has(id))throw new Error('Invalid or cyclic GLB node graph.');const n=nodes[id],mat=multiply(parent,nodeMatrix(n));if(n.mesh!==undefined)for(const prim of byMesh.get(n.mesh)||[])queuePrimitive(prim,mat);const next=new Set([...ancestors,id]);for(const c of(n.children||[]))walk(c,mat,next);}
  if(scene?.nodes?.length){for(const id of scene.nodes)walk(id,identity(),new Set());}
  else {for(const prim of primitives)queuePrimitive(prim,identity());}
  // Sample across the whole instanced scene before expansion, never per instance.
  const step=Math.max(1,Math.ceil(sceneTriangles/MAX_PREVIEW_TRIANGLES));let first=0;
  for(const {prim,mat} of draws){const count=prim.indices.length/3;const offset=(step-first%step)%step;for(let t=offset;t<count&&output.length/9<MAX_PREVIEW_TRIANGLES;t+=step){const arr=[];for(let k=0;k<3;k++)arr.push(...transform(mat,...prim.vertices[prim.indices[t*3+k]]));if(arr.every(Number.isFinite))output.push(...arr);}first+=count;}
  if(!sourceTriangles)throw new Error('GLB has no supported triangle mesh primitive.');
  return {format:'GLB',vertices:Float32Array.from(output),stats:{meshes:(doc.meshes||[]).length,primitives:primitiveCount,sourceTriangles,sceneTriangles,previewTriangles:output.length/9,materials:(doc.materials||[]).length,animations:(doc.animations||[]).length,skins:(doc.skins||[]).length,ignoredModes,extensions:doc.extensionsUsed||[],note:'Actual embedded triangle geometry; untextured WebGL preview only. No rig, texture, engine import or visual canon verification.'}};
}
export function inspectOBJ(text){
  if(typeof text!=='string'||text.length>MAX_SOURCE_BYTES)throw new Error('Invalid or oversize OBJ.');
  const points=[],faces=[];let sourceTriangles=0;for(const raw of text.split(/\r?\n/)){const l=raw.trim();if(l.startsWith('v ')){const p=l.split(/\s+/).slice(1,4).map(Number);if(p.length===3&&p.every(Number.isFinite))points.push(p);}
    else if(l.startsWith('f ')){const face=l.split(/\s+/).slice(1).map(s=>Number(s.split('/')[0]));if(face.length<3||face.some(n=>!Number.isInteger(n)||n===0))throw new Error('Invalid OBJ polygon.');const absolute=face.map(n=>n<0?points.length+n+1:n);if(absolute.some(n=>n<=0))throw new Error('OBJ face references missing vertex.');faces.push(absolute);sourceTriangles+=face.length-2;}}
  if(!points.length||!faces.length)throw new Error('OBJ has no vertex faces.');if(sourceTriangles>1000000)throw new Error('OBJ polygon count exceeds local inspection limit.');
  const out=[],step=Math.max(1,Math.ceil(sourceTriangles/MAX_PREVIEW_TRIANGLES));let seen=0;
  const resolved=n=>{const i=n-1;if(i<0||i>=points.length)throw new Error('OBJ face references missing vertex.');return points[i];};
  for(const f of faces)for(const n of f)resolved(n);
  for(const f of faces)for(let t=1;t<f.length-1;t++){if((seen++%step)!==0)continue;out.push(...resolved(f[0]),...resolved(f[t]),...resolved(f[t+1]));}
  return {format:'OBJ',vertices:Float32Array.from(out),stats:{meshes:1,sourceVertices:points.length,sourceTriangles,previewTriangles:out.length/9,materials:0,animations:0,skins:0,note:'Actual OBJ triangles; untextured WebGL preview only. No animation, PBR, engine import or visual-canon verification.'}};
}
export async function inspectSource(file){
  if(!file||!file.name)throw new Error('Select a local source file.');if(file.size>MAX_SOURCE_BYTES)throw new Error('Source over 64 MiB. Store larger assets in the controlled source repository.');const type=file.name.toLowerCase().split('.').pop();
  if(type==='glb')return inspectGLB(await file.arrayBuffer());
  if(type==='obj')return inspectOBJ(await file.text());
  if(type==='fbx')return {format:'FBX',vertices:null,stats:{note:'FBX bytes can be hashed, but this browser does not decode FBX. Validate in native Blender before staging.'}};
  throw new Error('Only GLB, OBJ and FBX sources are accepted.');
}
