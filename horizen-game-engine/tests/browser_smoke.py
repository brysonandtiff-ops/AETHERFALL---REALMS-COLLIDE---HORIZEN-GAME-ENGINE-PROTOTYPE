#!/usr/bin/env python3
"""Genuine Chromium smoke evidence; NEVER a Godot, Blender or Android verification."""
import hashlib
import json
import pathlib
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
PORT = 18081
SERVER = subprocess.Popen([sys.executable, str(ROOT / 'serve.py'), '--port', str(PORT)],
                          cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ERRORS = []
try:
    for _ in range(40):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/', timeout=.25) as response:
                assert response.headers.get('Cache-Control') == 'no-store, no-cache, must-revalidate'
                break
        except OSError:
            time.sleep(.1)
    else:
        raise AssertionError('Local HORIZEN server did not start')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        context = browser.new_context(viewport={'width':1440,'height':900},device_scale_factor=1,
                                      accept_downloads=True,record_video_dir=str(EVIDENCE),
                                      record_video_size={'width':1440,'height':900})
        page=context.new_page()
        page.on('pageerror', lambda err: ERRORS.append(str(err)))
        url=f'http://127.0.0.1:{PORT}/'
        page.goto(url,wait_until='networkidle')
        assert page.title().startswith('HORIZEN GAME ENGINE')
        assert page.locator('.world-card').count()==4
        assert page.locator('#metric-worlds').inner_text()=='04'
        page.screenshot(path=str(EVIDENCE/'01_library_chromium_1440x900.png'),full_page=True)
        page.locator('#world-search').fill('aetherfall')
        assert page.locator('.world-card').count()==1
        page.locator('#world-search').fill('')
        page.locator('#new-world').click()
        page.locator('#world-name').fill('LOCAL TEST WORLD')
        page.locator('#world-url').fill('./tests/fixtures/builds/verified-entry/index.html')
        page.locator('#world-form button[type=submit]').click()
        assert page.locator('.world-card').count()==5
        card=page.locator('.world-card').filter(has_text='LOCAL TEST WORLD')
        card.get_by_role('button',name='VERIFY ENTRY').click()
        page.get_by_text('BROWSER ENTRY VERIFIED').first.wait_for()
        assert card.get_by_role('button',name='LAUNCH').count()==1
        page.get_by_role('button',name='03 Model Forge').click()
        page.locator('#asset-id').fill('CHR_TestTriangle')
        page.locator('#asset-file').set_input_files(str(ROOT/'tests/fixtures/triangle.obj'))
        page.locator('#asset-form button[type=submit]').click()
        page.get_by_text('CHR_TestTriangle',exact=True).first.wait_for()
        page.locator('#preview-state').get_by_text('REAL LOCAL SOURCE').wait_for()
        assert not page.locator('#model-canvas').is_hidden()
        assert page.locator('#pipeline-summary').inner_text().startswith('0 / 8')
        page.screenshot(path=str(EVIDENCE/'02_forge_real_obj_chromium_1440x900.png'),full_page=True)
        page.locator('.step').first.get_by_role('button').click()
        page.locator('#evidence-file').set_input_files(str(ROOT/'tests/fixtures/evidence.txt'))
        assert page.locator('#pipeline-summary').inner_text().startswith('1 / 8')
        page.locator('#doctor-run').click()
        page.get_by_text('Local storage writable').wait_for()
        assert 'NOT VERIFIED' in page.locator('#doctor-note').inner_text().upper()
        with page.expect_download() as event:
            page.locator('#manifest-export').click()
        downloaded=event.value
        receipt_path=EVIDENCE/'smoke_staging_receipt.json'
        downloaded.save_as(str(receipt_path))
        receipt=json.loads(receipt_path.read_text())
        assert receipt['release']['certification']=='HOLD_NOT_VERIFIED'
        assert receipt['assets'][0]['evidence'][0]['review']=='PENDING_INDEPENDENT_REVIEW'
        page.get_by_role('button',name='02 System Status').click()
        assert page.locator('.gate').count()==10
        page.screenshot(path=str(EVIDENCE/'03_status_chromium_1440x900.png'),full_page=True)
        reg=page.evaluate('''async () => {const r=await navigator.serviceWorker.ready; return {active:!!r.active,scope:r.scope};}''')
        assert reg['active']
        page.wait_for_function('!!navigator.serviceWorker.controller')
        context.set_offline(True)
        page.reload(wait_until='domcontentloaded')
        assert page.locator('.world-card').count()==5
        assert page.locator('#metric-worlds').inner_text()=='05'
        assert page.locator('#metric-ready').inner_text()=='00'  # session verification not persisted
        context.set_offline(False)
        assert not ERRORS, ERRORS
        page.screenshot(path=str(EVIDENCE/'04_offline_reload_chromium_1440x900.png'),full_page=True)
        video=page.video
        context.close()
        video_path=pathlib.Path(video.path())
        video_dest=EVIDENCE/'HORIZEN_PWA_REAL_CHROMIUM_INTERACTION.webm'
        video_path.rename(video_dest)
        browser.close()
    manifest={'schema':'sire.horizen.browser_smoke.v1','observedAt':datetime.now(timezone.utc).isoformat(),
              'system':'headless Chromium via Playwright on Linux container; NOT an Android device',
              'url':url,'nativeGodot':False,'nativeBlender':False,'realPhone':False,
              'browserSmoke':'PASS','unitTestFixture':True,'pageErrors':ERRORS,
              'files':{f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
                       for f in EVIDENCE.iterdir() if f.is_file() and f.name!='browser_smoke_manifest.json'}}
    (EVIDENCE/'browser_smoke_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('PASS: 4 seed worlds, search, registration, HTTP verification, actual OBJ WebGL preview, staged evidence, doctor, receipt, 10 gates, service worker offline reload; browser console errors: 0')
    print('Screenshot + genuine browser interaction video:', EVIDENCE)
finally:
    SERVER.terminate()
    try: SERVER.wait(timeout=3)
    except subprocess.TimeoutExpired: SERVER.kill()
