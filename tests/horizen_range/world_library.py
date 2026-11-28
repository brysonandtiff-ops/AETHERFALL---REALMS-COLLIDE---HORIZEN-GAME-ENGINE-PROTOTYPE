"""Real Chrome. Register in unmodified HORIZEN, verify HTML, launch Godot and send inputs."""
from pathlib import Path
import json
import sys
import time
from playwright.sync_api import sync_playwright


def main(dest):
    dest.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        ctx = browser.new_context(viewport={'width':1280,'height':720}, accept_downloads=False)
        page = ctx.new_page()
        page.goto('http://127.0.0.1:8080/')
        page.locator('#new-world').click()
        page.locator('#world-name').fill('AETHERFALL | The Unbound Reach')
        page.locator('#world-url').fill('./builds/unbound-reach/index.html')
        page.locator('#world-form button[type=submit]').click()
        card = page.locator('.world-card').filter(has_text='AETHERFALL | The Unbound Reach')
        card.get_by_text('VERIFY ENTRY',exact=True).click()
        launch = card.get_by_role('button',name='LAUNCH')
        launch.wait_for()
        page.screenshot(path=str(dest/'horizen-library.png'))
        with ctx.expect_page() as popup:
            launch.click()
        game = popup.value
        game.wait_for_load_state()
        game.wait_for_selector('#canvas',state='visible',timeout=90000)
        game.wait_for_function("() => {let s=document.querySelector('#status'); return !s || getComputedStyle(s).visibility==='hidden'||getComputedStyle(s).display==='none'}",timeout=120000)
        game.wait_for_timeout(800)
        game.locator('#canvas').click(position={'x':500,'y':310})
        game.screenshot(path=str(dest/'web-arrival.png'))
        game.keyboard.press('f')
        game.keyboard.down('e')
        game.keyboard.down('w')
        game.wait_for_timeout(1100)
        game.keyboard.up('w')
        game.wait_for_timeout(500)
        game.screenshot(path=str(dest/'web-interaction.png'))
        game.keyboard.up('e')
        if (dest/'web-arrival.png').read_bytes() == (dest/'web-interaction.png').read_bytes():
            raise AssertionError('No observable viewport delta')
        kinds = game.evaluate("performance.getEntriesByType('resource').map(r=>r.name.split('?')[0].split('/').pop())")
        if not {'index.pck','index.wasm'}.issubset(kinds):
            raise AssertionError(kinds)
        print('AF_HORIZEN_BROWSER_PASS: actual World Library register / verify / launch; Godot PCK and WASM loaded; input sent; changed viewport captured')
        (dest/'browser-report.json').write_text(json.dumps({'chrome':browser.version,'landed_url':game.url,'resources':kinds,'scope':'desktop software WebGL; native test independently asserts trial outcomes; not phone acceptance'},indent=2))
        browser.close()


if __name__ == '__main__':
    main(Path(sys.argv[1]))
