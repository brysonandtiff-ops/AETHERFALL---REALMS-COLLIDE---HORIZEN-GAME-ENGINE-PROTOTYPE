/** Explicit opt-in browser-local originals; no remote upload or silent scanning. */
const DB='horizen-model-vault-v1',STORE='originals',MAX_BYTES=64*1024*1024;
function validId(id){return typeof id==='string'&&id.length>=3&&id.length<=128&&/^[A-Za-z0-9_-]+$/.test(id);}
function openVault(){
  if(typeof indexedDB==='undefined')return Promise.reject(new Error('IndexedDB is unavailable; reselect the original file after reload.'));
  return new Promise((resolve,reject)=>{
    const req=indexedDB.open(DB,1);
    req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains(STORE))db.createObjectStore(STORE,{keyPath:'id'});};
    req.onsuccess=()=>resolve(req.result);
    req.onerror=()=>reject(req.error||new Error('Could not open local source vault'));
    req.onblocked=()=>reject(new Error('Source vault upgrade blocked by another tab'));
  });
}
async function execute(mode,operation){
  const db=await openVault();try{return await new Promise((resolve,reject)=>{
    const tx=db.transaction(STORE,mode),request=operation(tx.objectStore(STORE));let result;
    request.onsuccess=()=>{result=request.result;};
    request.onerror=()=>reject(request.error||new Error('Local source storage request failed'));
    tx.oncomplete=()=>resolve(result);
    tx.onerror=()=>reject(tx.error||new Error('Local source storage transaction failed'));
    tx.onabort=()=>reject(tx.error||new Error('Local source storage transaction aborted'));
  });}finally{db.close();}
}
export async function retainSource(id,file,sha256){
  if(!validId(id)||!(file instanceof Blob)||file.size<1||file.size>MAX_BYTES||!/^[a-f0-9]{64}$/.test(sha256))throw new Error('Invalid file, record ID or checksum for offline source retention');
  return execute('readwrite',store=>store.put({id,file,sha256,retainedAt:new Date().toISOString(),name:file.name||'selected-source'}));
}
export async function getRetainedSource(id){
  if(!validId(id))throw new Error('Invalid source identifier');
  const record=await execute('readonly',store=>store.get(id));
  if(!record)return null;
  if(!(record.file instanceof Blob)||record.file.size<1||record.file.size>MAX_BYTES||!/^[a-f0-9]{64}$/.test(record.sha256))throw new Error('Stored source record failed local integrity metadata checks');
  return record;
}
export async function forgetRetainedSource(id){
  if(!validId(id))throw new Error('Invalid source identifier');
  return execute('readwrite',store=>store.delete(id));
}
