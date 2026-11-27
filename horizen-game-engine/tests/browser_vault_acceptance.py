"""Full HTTP/SW Chromium vault acceptance; disposable synthetic OBJ files only."""
import functools
import hashlib
import json
import os
import subprocess
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "vault-acceptance"
DB = """async () => {const v=await import('./model-vault.js');return v;}"""
A = b"v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
B = b"v 0 0 0\nv 2 0 0\nv 0 2 0\nf 1 2 3\n"
def run():
    OUT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM", "/usr/bin/chromium"), args=["--no-sandbox"])
            ctx = browser.new_context(record_video_dir=str(OUT))
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            ctx.tracing.start(screenshots=True, snapshots=True)
            def upload(name, data, retain):
                page.locator("#asset-id").fill(name)
                page.locator("#asset-file").set_input_files({"name":name+".obj","mimeType":"text/plain","buffer":data})
                page.locator("#asset-retain").set_checked(retain)
                page.locator("#asset-form button[type=submit]").click()
                expect(page.locator("#asset-form button[type=submit]")).to_be_enabled()
                expect(page.locator("#selected-asset-label")).to_have_text(name)
                expect(page.locator("#preview-state")).to_have_text("REAL LOCAL SOURCE")
            def select(name, status):
                page.locator(".asset-item").filter(has=page.get_by_text(name, exact=True)).click()
                expect(page.locator("#selected-asset-label")).to_have_text(name)
                expect(page.locator("#preview-state")).to_have_text(status)
            def records():
                return page.evaluate("""async () => {const db=await new Promise((ok,no)=>{const r=indexedDB.open('horizen-model-vault-v1',1);r.onsuccess=()=>ok(r.result);r.onerror=()=>no(r.error);});try{const rows=await new Promise((ok,no)=>{const r=db.transaction('originals').objectStore('originals').getAll();r.onsuccess=()=>ok(r.result);r.onerror=()=>no(r.error);});return await Promise.all(rows.map(async r=>({id:r.id,name:r.name,hash:r.sha256,actual:Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await r.file.arrayBuffer())),b=>b.toString(16).padStart(2,'0')).join('')})));}finally{db.close();}}""")
            def reload():
                page.reload(wait_until="load")
                expect(page.locator("#asset-form")).to_be_visible()
            try:
                page.goto(f"http://127.0.0.1:{server.server_port}/#forge")
                page.wait_for_function("!!navigator.serviceWorker.controller")
                upload("SESSION_ONLY", A, False)
                upload("RETAIN_A", A, True)
                upload("RETAIN_B", B, True)
                rows = records()
                assert {r["name"]:r["actual"] for r in rows} == {"RETAIN_A.obj":hashlib.sha256(A).hexdigest(),"RETAIN_B.obj":hashlib.sha256(B).hexdigest()}
                assert all(r["hash"]==r["actual"] for r in rows)
                results.append("upload_opt_in_hash")
                ctx.set_offline(True)
                reload()
                assert page.evaluate("navigator.onLine") is False
                select("SESSION_ONLY","NO SOURCE LOADED")
                select("RETAIN_A","REAL LOCAL SOURCE")
                page.screenshot(path=str(OUT/"offline-restored.png"))
                results.append("offline_reload")
                # Delay actual IndexedDB get success delivery, not the stored bytes.
                page.evaluate("""() => {const orig=IDBObjectStore.prototype.get;IDBObjectStore.prototype.get=function(...args){const r=orig.apply(this,args);const d=Object.getOwnPropertyDescriptor(IDBRequest.prototype,'onsuccess');if(args[0]===window.slowId)Object.defineProperty(r,'onsuccess',{set(fn){d.set.call(r,e=>setTimeout(()=>fn.call(r,e),500));}});return r;};}""")
                page.evaluate("(id)=>window.slowId=id",next(r["id"] for r in rows if r["name"]=="RETAIN_B.obj"))
                page.locator(".asset-item").filter(has=page.get_by_text("RETAIN_B",exact=True)).click()
                select("RETAIN_A","REAL LOCAL SOURCE")
                page.wait_for_timeout(800)
                expect(page.locator("#selected-asset-label")).to_have_text("RETAIN_A")
                expect(page.locator("#preview-state")).to_have_text("REAL LOCAL SOURCE")
                results.append("delayed_switch")
                reload()
                select("RETAIN_A","REAL LOCAL SOURCE")
                page.locator("#forget-local-model").click()
                expect(page.locator("#toast")).to_contain_text("Stored original removed for RETAIN_A")
                assert [r["name"] for r in records()]==["RETAIN_B.obj"]
                reload()
                select("RETAIN_A","NO SOURCE LOADED")
                select("RETAIN_B","REAL LOCAL SOURCE")
                results.append("correct_file_removal")
                page.evaluate("""() => {IDBObjectStore.prototype.put=function(){throw new DOMException('Injected quota failure','QuotaExceededError');};}""")
                upload("FAIL_STORAGE", A, True)
                expect(page.locator("#toast")).to_contain_text("Local original retention failed")
                assert [r["name"] for r in records()]==["RETAIN_B.obj"]
                reload()
                select("FAIL_STORAGE","NO SOURCE LOADED")
                results.append("injected_storage_failure")
                assert not errors, errors
            finally:
                ctx.tracing.stop(path=str(OUT/"trace.zip"))
                ctx.close()
                browser.close()
                (OUT/"results.json").write_text(json.dumps({"source":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"passed":results,"page_errors":errors,"native_tests":"NOT RUN"},indent=2))
    finally:
        server.shutdown()
        server.server_close()
if __name__ == "__main__":
    run()
