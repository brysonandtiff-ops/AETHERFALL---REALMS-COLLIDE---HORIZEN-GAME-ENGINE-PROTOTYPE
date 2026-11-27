import {test} from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import vm from "node:vm";

const code=await readFile(new URL("../docs/showcase/aetherfall-live-worker.js",import.meta.url),"utf8");
const worker=(await import("data:text/javascript;base64,"+Buffer.from(code).toString("base64"))).default;
const req=()=>new Request("https://showcase.invalid/api/state");
const goodTree={sha:"a".repeat(40),tree:[{type:"blob",path:"art/concepts/characters/CHR_Dreadhull/canon.webp",size:12}]};
const mock=async (tree,registry,run)=>{
  const original=globalThis.fetch;
  globalThis.fetch=async url=>String(url).includes("/git/trees/")?tree():registry();
  try{await run();}finally{globalThis.fetch=original;}
};
const json=value=>new Response(JSON.stringify(value),{headers:{"content-type":"application/json"}});

test("registry failure cannot look like a successful empty roster",async()=>{
  for(const failure of [()=>new Response("unavailable",{status:503}),()=>new Response("{broken"),()=>json({assets:null}),()=>json({assets:[null]}),()=>Promise.reject(Error("network"))]){
    await mock(()=>json(goodTree),failure,async()=>{
      const res=await worker.fetch(req());
      assert.equal(res.status,503);
      assert.match((await res.json()).error,/registry/i);
    });
  }
});
test("real empty roster is distinct from unavailable roster",async()=>{
  await mock(()=>json(goodTree),()=>json({assets:[]}),async()=>{
    const res=await worker.fetch(req());
    assert.equal(res.status,200);
    const state=await res.json();
    assert.deepEqual(state.registry,[]);
    assert.equal(state.media[0].character,"Dreadhull");
  });
});
test("truncated tree and upstream HTTP error are not successful syncs",async()=>{
  await mock(()=>json({...goodTree,truncated:true}),()=>json({assets:[]}),async()=>assert.equal((await worker.fetch(req())).status,502));
  await mock(()=>new Response("unavailable",{status:429}),()=>json({assets:[]}),async()=>assert.equal((await worker.fetch(req())).status,503));
});
test("Other includes characters without dedicated buttons",async()=>{
  const js=await (await worker.fetch(new Request("https://showcase.invalid/app.js"))).text();
  const fn=js.split("\n").find(line=>line.startsWith("function matchesCharacter("));
  assert.ok(fn,"actual served filter function is missing");
  const match=vm.runInNewContext("("+fn+")");
  const dedicated=new Set(["vellaris","thorndell","korvex"]);
  for(const id of ["Dreadhull","Morrigan","Pixi","Noxis","Orion","Other"])assert.equal(match(id,"other",dedicated),true,id);
  assert.equal(match("Vellaris","other",dedicated),false);
  assert.equal(match("Vellaris","vellaris",dedicated),true);
  assert.equal(match("Dreadhull","all",dedicated),true);
  assert.match(js,/filter\(a=>matchesCharacter\(a.character,filter,dedicated\)/);
});
