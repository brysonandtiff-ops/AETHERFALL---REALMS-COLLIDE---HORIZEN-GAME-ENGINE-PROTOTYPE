/* HORIZEN GAME ENGINE. Cache only own shell resources, never unverified builds. */
const VERSION='horizen-shell-v0.1.0';
const ASSETS=['./','./index.html','./styles.css','./app.js','./core.js','./model-inspect.js','./viewer.js','./manifest.webmanifest','./icons/icon.svg','./icons/icon-192.png','./icons/icon-512.png'];
const LOCAL_ASSETS=new Set(ASSETS.map(path=>new URL(path,self.registration.scope).pathname));
self.addEventListener('install',evt=>{evt.waitUntil((async()=>{const cache=await caches.open(VERSION);await cache.addAll(ASSETS.map(p=>new Request(p,{cache:'reload'})));await self.skipWaiting();})());});
self.addEventListener('activate',evt=>{evt.waitUntil((async()=>{await Promise.all((await caches.keys()).filter(k=>k.startsWith('horizen-shell-')&&k!==VERSION).map(k=>caches.delete(k)));await self.clients.claim();})());});
self.addEventListener('fetch',evt=>{
 const request=evt.request;if(request.method!=='GET')return;
 const url=new URL(request.url);if(url.origin!==self.location.origin||!LOCAL_ASSETS.has(url.pathname))return;
 evt.respondWith((async()=>{const cache=await caches.open(VERSION);
  try{const fresh=await fetch(new Request(request,{cache:'no-store'}));if(fresh.ok&&fresh.type==='basic')await cache.put(request,fresh.clone());return fresh;}
  catch{const saved=await cache.match(request,{ignoreSearch:true});if(saved)return saved;throw new Error('Offline shell resource unavailable');}
 })());
});
