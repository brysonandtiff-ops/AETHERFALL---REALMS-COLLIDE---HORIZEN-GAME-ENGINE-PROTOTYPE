/** HORIZEN local governance contracts. No remote services are inferred. */
export const SCHEMA = 'sire.horizen.staging.v1';
export const STORAGE_KEY = 'sire.horizen.workspace.v1';
export const DEFAULT_WORLDS = Object.freeze([
  {id:'world-aetherfall',name:'AETHERFALL: REALMS COLLIDE',status:'staged',url:'',notes:'Godot 4 source project; native engine and gameplay not verified.',kind:'HERO SHOOTER'},
  {id:'world-cryptid',name:'CRYPTID RESERVE',status:'staged',url:'',notes:'Catalog entry only. No browser build connected.',kind:'WORLD'},
  {id:'world-fossil',name:'FOSSIL.OS',status:'staged',url:'',notes:'Catalog entry only. No browser build connected.',kind:'SIMULATION'},
  {id:'world-portfolio',name:'PORTFOLIO BUILDS',status:'staged',url:'',notes:'Register local browser-ready builds when their files exist.',kind:'COLLECTION'},
]);
export const PIPELINE = Object.freeze([
  ['Source intake & canon','Hash source bytes and confirm exact approved reference; owner approval remains separate.'],
  ['Import, scale & base removal','Metric units, real height, separate pedestal and equipment, applied transforms.'],
  ['Mesh repair & symmetry','Non-manifold review, outward normals, symmetry only where design allows.'],
  ['Quad retopology & LODs','Preserve high-poly; joint loops, 3P/1P budgets and measured triangles.'],
  ['UVs & PBR baking','Clean UV islands, padding, normal/AO/albedo/metallic/roughness/emission.'],
  ['Rigging & socket export','A-pose or species stance, weights, twist bones, weapon/VFX sockets.'],
  ['1P + 3P motion & combat','Locomotion, telegraphs, attacks, passive/ultimate, hitboxes separate from VFX.'],
  ['Native engine & evidence','Real Godot import, animation/play test, runtime capture, provenance and approval.'],
]);
export const GATES = Object.freeze([
  ['Source identity','Exact-file hashes & provenance'],['Visual canon','Owner-approved side-by-side comparison'],
  ['Topology & LOD','Native mesh and triangle audit'],['UV & PBR','Baked textures and material import'],
  ['Skeleton & sockets','Native rig deformation evidence'],['1P / 3P animation','Real clips and viewmodel tests'],
  ['Combat & AI','Authoritative hit tests and state rules'],['Godot import','Exact-version native engine load'],
  ['Runtime evidence','Genuine video and screenshots'],['Device & release','Real phone, recovery and external gates'],
]);
export const SUBSYSTEMS = Object.freeze([
  ['Recovery','Rollback/checkpoint services require a connected operator.','NOT CONNECTED'],
  ['Hereditary Immunity','Security ancestry and trust scan not connected.','NOT CONNECTED'],
  ['Mutation Authority','No autonomous code mutation or approvals granted.','LOCKED'],
  ['Fleet Defense','Remote workers and devices are not polled.','NOT CONNECTED'],
  ['Evidence Vault','Local staging receipts are stored in this browser only.','LOCAL ONLY'],
  ['10-Gate Matrix','All native/game/release gates are on hold.','HOLD'],
  ['System Health','Browser capability checks are available in GAISLINK Doctor.','LOCAL DIAGNOSTICS'],
]);
export const cleanText = (v, max = 100) => String(v ?? '').trim().slice(0,max);
export const validId = id => /^[A-Za-z0-9_-]{3,80}$/.test(id);
export function safeSameOriginUrl(raw, currentUrl) {
  if (!raw || !cleanText(raw,500)) throw new Error('Enter a local build entry path.');
  let u; try { u = new URL(raw, currentUrl); } catch { throw new Error('Invalid URL.'); }
  const base = new URL(currentUrl);
  if (u.origin !== base.origin || !/^https?:$/.test(u.protocol) || u.username || u.password) throw new Error('Only a same-origin HTTP build is allowed.');
  if (u.hash) throw new Error('Entry URLs must not include fragments.');
  return u;
}
export function createWorld({name,url='',notes='',status='staged'}, id) {
  const n = cleanText(name,80), s = ['active','staged','archived'].includes(status) ? status : 'staged';
  if (!n) throw new Error('A world name is required.');
  return {id:cleanText(id,100),name:n,status:s,url:cleanText(url,500),notes:cleanText(notes,600),kind:'LOCAL WORLD'};
}
export function filterWorlds(worlds, query, status, ready = new Set()) {
  const needle=cleanText(query,200).toLocaleLowerCase();
  return worlds.filter(w => (status==='all'||(status==='ready'?ready.has(w.id):w.status===status)) &&
    [w.name,w.kind,w.notes].some(v=>String(v??'').toLocaleLowerCase().includes(needle)));
}
export function makeEmptyState() {return {worlds:DEFAULT_WORLDS.map(w=>({...w})),assets:[]};}
const hashOK = s => typeof s==='string' && /^[0-9a-f]{64}$/i.test(s);
export function normalizeState(state) {
  if (!state || typeof state!=='object') throw new Error('Invalid manifest root.');
  const worlds = Array.isArray(state.worlds) ? state.worlds.slice(0,200) : [];
  const assets = Array.isArray(state.assets) ? state.assets.slice(0,100) : [];
  const uniqueWorlds=new Set(),uniqueAssets=new Set();
  return {
    worlds:worlds.map((w,i)=>{
      const id=cleanText(w?.id,100)||`import-world-${i}`;
      if(uniqueWorlds.has(id)) throw new Error('Duplicate world identity.'); uniqueWorlds.add(id);
      return {...createWorld(w,id),kind:cleanText(w?.kind||'LOCAL WORLD',60)};
    }),
    assets:assets.map((a,i)=>{
      const id=cleanText(a?.id,100),name=cleanText(a?.name,80),sha256=cleanText(a?.sha256,64).toLowerCase();
      if (!id || !validId(name) || !hashOK(sha256) || uniqueAssets.has(id)) throw new Error(`Invalid asset entry ${i+1}.`);
      uniqueAssets.add(id);
      const evidence = Array.from({length:8},(_,j)=>{
        const e=Array.isArray(a.evidence)?a.evidence[j]:null;
        return e && hashOK(e.sha256) ? {name:cleanText(e.name,180),sha256:cleanText(e.sha256,64).toLowerCase(),bytes:Number.isSafeInteger(e.bytes)&&e.bytes>=0?e.bytes:0,submittedAt:cleanText(e.submittedAt,40),review:'PENDING_INDEPENDENT_REVIEW'} : null;
      });
      return {id,name,worldId:cleanText(a.worldId,100),fileName:cleanText(a.fileName,180),format:cleanText(a.format,10).toUpperCase(),sha256,bytes:Number.isSafeInteger(a.bytes)&&a.bytes>=0?a.bytes:0,inspection:cleanText(a.inspection,180),createdAt:cleanText(a.createdAt,40),evidence};
    }),
  };
}
export async function sha256(blob) {
  if (!globalThis.crypto?.subtle) throw new Error('Web Crypto unavailable: cannot register unverified bytes.');
  const buf = await blob.arrayBuffer();
  const digest = await crypto.subtle.digest('SHA-256',buf);
  return Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');
}
export function stagingReceipt(state,{origin,doctor={},appVersion='0.1.0'}={}) {
  const clean=normalizeState(state);
  return {
    schema:SCHEMA,product:'HORIZEN GAME ENGINE',governor:'S.I.R.E.',project:'AETHERFALL: REALMS COLLIDE',
    generatedAt:new Date().toISOString(),appVersion,sourceOrigin:origin||null,
    release:{authority:'S.I.R.E. staging; distributor controls final publication',certification:'HOLD_NOT_VERIFIED',nativeBlender:false,nativeGodot:false,physicalDevice:false,realRuntimeCapture:false,remoteConnectionVerified:false},
    worlds:clean.worlds,assets:clean.assets,doctor,
    notice:'File hashes are computed locally. Uploaded evidence is owner-supplied and pending independent validation. Session-local viewport rendering is not native engine proof.'
  };
}
export function importReceipt(json) {
  if (!json || json.schema!==SCHEMA) throw new Error('Unsupported manifest schema.');
  if (!Array.isArray(json.worlds)||!Array.isArray(json.assets)||json.worlds.length>200||json.assets.length>100) throw new Error('Invalid manifest structure.');
  return normalizeState(json);
}

/** Distinguish the engine's directory/index aliases from genuine world entries. */
export function isEngineShellUrl(candidate,currentUrl){
  const page=new URL(currentUrl),target=new URL(candidate,page);
  if(page.origin!==target.origin)return false;
  const key=u=>decodeURIComponent(u.pathname).replace(/\/+/g,'/').replace(/\/index\.html$/i,'/');
  return key(target)===key(page)||key(target)===key(new URL('./',page));
}
/** Reattach only an exact original. Existing receipts/IDs are never overwritten. */
export function findExistingSourceAsset(assets,{name,hash,bytes,format,worldId,selectedId}){
  const matches=assets.filter(a=>a.name===name&&a.sha256===hash&&a.bytes===bytes&&a.format===format);
  const selected=matches.find(a=>a.id===selectedId);if(selected)return selected;
  const sameWorld=matches.filter(a=>a.worldId===worldId);
  if(sameWorld.length===1)return sameWorld[0];
  if(matches.length===1)return matches[0];
  if(matches.length>1)throw new Error('Multiple matching originals; select the existing asset before reattaching.');
  return null;
}
export function persistenceMessage(saved,message){
  return saved?message:'SESSION ONLY — browser storage failed. Export staging JSON before reloading. '+message;
}
