import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectSource,inspectGLB} from '../model-inspect.js';
import {inspectSTL,embeddedGLTFtoGLB} from '../model-extra.js';
import {retainSource,getRetainedSource} from '../model-vault.js';

const asBuffer=array=>array.buffer.slice(array.byteOffset,array.byteOffset+array.byteLength);
function sampleSTL(){
 const b=new ArrayBuffer(134),v=new DataView(b);v.setUint32(80,1,true);
 const tri=[0,0,0,1,0,0,0,1,0];
 for(let i=0;i<9;i++)v.setFloat32(84+12+i*4,tri[i],true);
 return b;
}
function sampleGLTF(external=false){
 const points=new Float32Array([0,0,0,1,0,0,0,1,0]);
 const bin=Buffer.from(points.buffer);
 return JSON.stringify({
  asset:{version:'2.0'},buffers:[{byteLength:bin.length,uri:external?'https://example.invalid/mesh.bin':'data:application/octet-stream;base64,'+bin.toString('base64')}],
  bufferViews:[{buffer:0,byteLength:bin.length}],
  accessors:[{bufferView:0,componentType:5126,count:3,type:'VEC3'}],
  meshes:[{primitives:[{attributes:{POSITION:0},mode:4}]}],nodes:[{mesh:0}],scenes:[{nodes:[0]}],scene:0
 });
}
test('binary STL preview renders only actual source triangles',()=>{
 const result=inspectSTL(sampleSTL());assert.equal(result.stats.sourceTriangles,1);assert.equal(result.vertices.length,9);assert.equal(result.stats.mode,'binary');
});
test('ASCII STL is real geometry rather than a placeholder',()=>{
 const text='solid triangle\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid triangle\n';
 const encoded=new TextEncoder().encode(text);const result=inspectSTL(asBuffer(encoded));assert.equal(result.stats.mode,'ASCII');assert.equal(result.stats.sourceTriangles,1);
});
test('malformed binary STL and nonfinite vertices fail closed',()=>{
 const short=sampleSTL();new DataView(short).setUint32(80,5,true);assert.throws(()=>inspectSTL(short));
 const nonfinite=sampleSTL();new DataView(nonfinite).setFloat32(84+12,Infinity,true);assert.throws(()=>inspectSTL(nonfinite));
});
test('embedded glTF yields actual GLB mesh geometry and dispatches by extension',async()=>{
 const text=sampleGLTF();const converted=inspectGLB(embeddedGLTFtoGLB(text));assert.equal(converted.stats.sourceTriangles,1);
 const result=await inspectSource({name:'hero.gltf',size:text.length,text:async()=>text});assert.equal(result.format,'GLTF');assert.equal(result.stats.previewTriangles,1);
 const stl=sampleSTL();const dispatch=await inspectSource({name:'hero.stl',size:stl.byteLength,arrayBuffer:async()=>stl});assert.equal(dispatch.format,'STL');
});
test('external glTF URLs are not fetched or silently accepted',()=>{
 assert.throws(()=>embeddedGLTFtoGLB(sampleGLTF(true)),/External glTF/);
});
test('no IndexedDB fails honestly, and unsafe source IDs are rejected',async()=>{
 await assert.rejects(()=>getRetainedSource('CHR_Test'),/IndexedDB is unavailable/);
 await assert.rejects(()=>retainSource('../oops',new Blob(['some content']),'a'.repeat(64)),/Invalid file/);
});
