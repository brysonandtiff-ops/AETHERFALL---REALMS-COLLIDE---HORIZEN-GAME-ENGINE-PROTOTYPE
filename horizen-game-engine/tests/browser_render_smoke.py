#!/usr/bin/env python3
"""Real Chromium DOM rendering via set_content. NO HTTP/SW/engine/browser-build proof."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'evidence'
OUT.mkdir(exist_ok=True)
html=(ROOT/'index.html').read_text()
html=re.sub(r'<link[^>]+(?:manifest|stylesheet|icon)[^>]+>','',html)
html=re.sub(r'<script type="module"[^>]+></script>','',html)
css=(ROOT/'styles.css').read_text()
modules=[]
for path in ('core.js','model-inspect.js','viewer.js','app.js'):
    text=(ROOT/path).read_text()
    text=re.sub(r'^import .*? from .*?;\s*','',text,flags=re.M)
    text=re.sub(r'\bexport (?=(?:const|let|class|function|async)\b)','',text)
    modules.append(text)
script='(()=>{\n'+ '\n'.join(modules) +'\nwindow.__horizenSmoke={inspectOBJ,mountPreview};\n})()'
with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':1440,'height':900},device_scale_factor=1,
      record_video_dir=str(OUT),record_video_size={'width':1440,'height':900})
  page=context.new_page()
  errors=[]
  page.on('pageerror',lambda exc:errors.append(str(exc)))
  page.set_content(html)
  page.add_style_tag(content=css)
  page.add_script_tag(content=script)
  page.locator('.world-card').first.wait_for()
  assert page.locator('.world-card').count()==4
  page.screenshot(path=str(OUT/'01_library_CHROMIUM_DOM.png'),full_page=True)
  page.locator('#world-search').fill('aetherfall')
  assert page.locator('.world-card').count()==1
  page.locator('#world-search').fill('')
  page.locator('#new-world').click()
  page.locator('#world-name').fill('RUNTIME INTERACTION TEST')
  page.locator('#world-form button[type=submit]').click()
  assert page.locator('.world-card').count()==5
  page.locator('[data-nav="status"]').click()
  assert page.locator('.gate').count()==10
  page.screenshot(path=str(OUT/'02_status_CHROMIUM_DOM.png'),full_page=True)
  page.locator('[data-nav="forge"]').click()
  assert page.locator('.step').count()==8
  page.screenshot(path=str(OUT/'03_forge_CHROMIUM_DOM.png'),full_page=True)
  # Genuine browser canvas rendering from an explicit synthetic OBJ triangle fixture; no WebGL or engine claim.
  fixture=(ROOT/'tests/fixtures/triangle.obj').read_text()
  check=page.evaluate('''(fixture) => {const m=window.__horizenSmoke.inspectOBJ(fixture);const c=document.querySelector('#model-canvas');c.hidden=false;document.querySelector('#preview-empty').hidden=true;window.__horizenSmoke.mountPreview(c,m.vertices);document.querySelector('#preview-state').textContent='SYNTHETIC OBJ TEST';document.querySelector('#inspection-details').textContent=m.stats.note;return {triangles:m.stats.previewTriangles,canvas2d:c.dataset.renderer||null}}''',fixture)
  assert check['triangles']==1 and check['canvas2d'],check
  page.screenshot(path=str(OUT/'03b_synthetic_OBJ_Canvas2D_CHROMIUM.png'),full_page=True)
  page.locator('[data-nav="library"]').click()
  page.screenshot(path=str(OUT/'04_library_interacted_CHROMIUM_DOM.png'),full_page=True)
  assert not errors,errors
  video=page.video
  context.close()
  Path(video.path()).rename(OUT/'REAL_CHROMIUM_DOM_INTERACTIONS.webm')
  browser.close()
files={f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
       for f in OUT.iterdir() if f.is_file() and f.name not in ('renderer-test.png','browser_render_manifest.json')}
(OUT/'browser_render_manifest.json').write_text(json.dumps({
 'schema':'sire.horizen.browser_render_v1','recordedAt':datetime.now(timezone.utc).isoformat(),
 'runtime':'Chromium headless + Playwright real DOM + real click interactions',
 'method':'Real app HTML+CSS+JS in-memory; ES module imports flattened solely to run in an administrator URL-blocked browser',
 'notTested':['HTTP navigation','service worker','offline reload','GLB renderer','WebGL2 renderer','user-file-upload journey','real Android','Blender','Godot','GAISLINK'],
 'sourcePaths':['index.html','styles.css','core.js','model-inspect.js','viewer.js','app.js'],
 'errors':errors,'result':'PASS_FOR_DOM_RENDER_ONLY','files':files},indent=2)+'\n')
print('PASS: real Chromium DOM rendered three views, navigated, filtered, registered world, and displayed 10 + 8 gates. HTTP/SW/native tests NOT RUN.')
