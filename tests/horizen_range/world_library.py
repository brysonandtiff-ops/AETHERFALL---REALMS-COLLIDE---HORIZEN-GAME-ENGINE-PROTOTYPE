"""Real unmodified Chrome security policy. Register -> verify -> launch -> play -> reset."""
from pathlib import Path
import json
import sys
from playwright.sync_api import sync_playwright


def main(dest):
    dest.mkdir(parents=True,exist_ok=True)
    entry='http://127.0.0.1:8080/builds/unbound-reach/index.html'
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        ctx=browser.new_context(viewport={'width':1280,'height':720})
        messages=[]; errors=[]; resources=[]
        ctx.on('console',lambda msg: messages.append(msg.text))
        ctx.on('page',lambda pg: pg.on('pageerror',lambda err:errors.append(str(err))))
        ctx.on('response',lambda r: resources.append((r.url,r.status)))
        try:
            page=ctx.new_page(); home=page.goto('http://127.0.0.1:8080/')
            assert 'wasm-unsafe-eval' not in home.headers['content-security-policy']
            policy=ctx.request.get(entry).headers['content-security-policy']
            assert "'wasm-unsafe-eval'" in policy and "'unsafe-eval'" not in policy and "'unsafe-inline'" not in policy
            page.locator('#new-world').click();page.locator('#world-name').fill('AETHERFALL | The Unbound Reach')
            page.locator('#world-url').fill('./builds/unbound-reach/index.html');page.locator('#world-form button[type=submit]').click()
            card=page.locator('.world-card').filter(has_text='AETHERFALL | The Unbound Reach')
            card.get_by_text('VERIFY ENTRY',exact=True).click();launch=card.get_by_role('button',name='LAUNCH');launch.wait_for()
            page.screenshot(path=str(dest/'horizen-library.png'))
            with ctx.expect_page() as popup: launch.click()
            game=popup.value; game.wait_for_url(entry);game.locator('#canvas').wait_for(state='visible')
            def observed(fragment,limit=100):
                for _ in range(limit):
                    if any(fragment in line for line in messages):return
                    game.wait_for_timeout(250)
                raise AssertionError('Missing game event '+fragment+'; '+str(messages[-9:]))
            observed('AF_RANGE_STATE READY',300)
            game.locator('#canvas').click(position={'x':550,'y':310})
            game.screenshot(path=str(dest/'web-arrival.png'))
            game.keyboard.press('f',delay=100);observed('AF_RANGE_STATE RUNNING')
            game.keyboard.down('w');game.wait_for_timeout(800);game.keyboard.up('w')
            game.keyboard.down('e');game.wait_for_timeout(850);game.screenshot(path=str(dest/'web-interaction.png'));game.keyboard.up('e')
            game.keyboard.press('r',delay=100)
            for _ in range(100):
                if sum('AF_RANGE_STATE READY' in x for x in messages)>=2:break
                game.wait_for_timeout(100)
            assert sum('AF_RANGE_STATE READY' in x for x in messages)>=2
            received={u.split('?')[0].split('/')[-1] for u,code in resources if 200<=code<400}
            assert {'index.pck','index.wasm','range-boot.js','range.css'}.issubset(received),received
            assert not errors,errors
            print('AF_HORIZEN_BROWSER_PASS: real HORIZEN register/verify/launch, Godot scene ready, F starts trial, R resets, security headers intact')
        finally:
            (dest/'browser-report.json').write_text(json.dumps({'chrome':browser.version,'game_events':[m for m in messages if 'AF_RANGE_STATE' in m],'errors':errors,'console':messages[-25:],'scope':'desktop Chrome software WebGL, not Android'},indent=2))
            browser.close()


if __name__=='__main__':main(Path(sys.argv[1]))
