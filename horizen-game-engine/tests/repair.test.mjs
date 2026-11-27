import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectOBJ,inspectGLB} from '../model-inspect.js';
import {isEngineShellUrl,findExistingSourceAsset,persistenceMessage} from '../core.js';

test('OBJ negative indices resolve at each face declaration',()=>{
  const d=inspectOBJ('v 0 0 0\nv 1 0 0\nv 0 1 0\nf -3 -2 -1\nv 10 0 0\nv 11 0 0\nv 10 1 0\nf -3 -2 -1');
  assert.deepEqual([...d.vertices],[0,0,0,1,0,0,0,1,0,10,0,0,11,0,0,10,1,0]);
  assert.throws(()=>inspectOBJ('v 0 0 0\nf -3 -2 -1\nv 1 0 0\nv 0 1 0'),/missing vertex/);
});
function instancedGLB(){
  const triangles=30000,positions=new Float32Array(triangles*9);
  for(let i=0;i<triangles;i++){positions[i*9+3]=1;positions[i*9+7]=1;}
  const bin=Buffer.from(positions.buffer);
  const nodes=Array.from({length:64},(_,i)=>({mesh:0,translation:[i*10,0,0]}));
  const doc={asset:{version:'2.0'},buffers:[{byteLength:bin.length}],bufferViews:[{buffer:0,byteLength:bin.length}],accessors:[{bufferView:0,componentType:5126,count:triangles*3,type:'VEC3'}],meshes:[{primitives:[{attributes:{POSITION:0}}]}],nodes,scenes:[{nodes:nodes.map((_,i)=>i)}],scene:0};
  const raw=Buffer.from(JSON.stringify(doc)),j=Buffer.alloc(Math.ceil(raw.length/4)*4,32);raw.copy(j);
  const out=Buffer.alloc(28+j.length+bin.length);out.writeUInt32LE(0x46546c67,0);out.writeUInt32LE(2,4);out.writeUInt32LE(out.length,8);out.writeUInt32LE(j.length,12);out.writeUInt32LE(0x4e4f534a,16);j.copy(out,20);out.writeUInt32LE(bin.length,20+j.length);out.writeUInt32LE(0x004e4942,24+j.length);bin.copy(out,28+j.length);
  return out.buffer.slice(out.byteOffset,out.byteOffset+out.byteLength);
}
test('global GLB budget includes all instances without exceeding 180000 triangles',()=>{
  const d=inspectGLB(instancedGLB());
  assert.equal(d.stats.sourceTriangles,30000);
  assert.equal(d.stats.sceneTriangles,1920000);
  assert.ok(d.stats.previewTriangles>0&&d.stats.previewTriangles<=180000);
  assert.equal(d.vertices.length,d.stats.previewTriangles*9);
  let furthest=-Infinity;for(let i=0;i<d.vertices.length;i+=3)furthest=Math.max(furthest,d.vertices[i]);
  assert.ok(furthest>=630,'late scene instances must not be omitted by first-come budget');
});
test('shell directory and index aliases are not launchable worlds',()=>{
  for(const shell of ['http://localhost:8080/','http://localhost:8080/index.html','http://localhost:8080/engine/','http://localhost:8080/engine/index.html']){
    assert.equal(isEngineShellUrl('./',shell),true);
    assert.equal(isEngineShellUrl('./index.html?x=1',shell),true);
    assert.equal(isEngineShellUrl('./%69ndex.html',shell),true);
    assert.equal(isEngineShellUrl('./game/index.html',shell),false);
  }
});
test('reattachment preserves original ID and evidence and rejects ambiguous duplicates',()=>{
  const original={id:'abc',name:'CHR_Test',sha256:'a'.repeat(64),bytes:12,format:'OBJ',worldId:'w1',evidence:[{sha256:'b'.repeat(64)}]};
  const query={name:original.name,hash:original.sha256,bytes:12,format:'OBJ',worldId:'w1'};
  assert.equal(findExistingSourceAsset([original],query),original);
  assert.equal(findExistingSourceAsset([original],{...query,hash:'c'.repeat(64)}),null);
  assert.throws(()=>findExistingSourceAsset([original,{...original,id:'def'}],query),/Multiple matching/);
  assert.equal(findExistingSourceAsset([original,{...original,id:'def'}],{...query,selectedId:'abc'}),original);
  assert.equal(original.evidence.length,1);
});
test('failed storage is explicitly session-only and directs to export',()=>{
  assert.match(persistenceMessage(false,'Evidence attached.'),/SESSION ONLY.*Export staging JSON/);
  assert.equal(persistenceMessage(true,'Evidence attached.'),'Evidence attached.');
});
