"""Run actual Godot WASM on mobile-sized Chrome viewports; hardware touch is emulated, not an Android device."""
from pathlib import Path
import json
import sys
from playwright.sync_api import sync_playwright

ENTRY = "http://127.0.0.1:8080/builds/unbound-reach/index.html"

def exercise(browser, size, dest):
    w,h = size
    ctx = browser.new_context(viewport={"width":w,"height":h},has_touch=True,is_mobile=True,device_scale_factor=1)
    page = ctx.new_page()
    messages = []
    errors = []
    page.on("console",lambda msg: messages.append(msg.text))
    page.on("pageerror",lambda err: errors.append(str(err)))
    try:
        page.goto(ENTRY,wait_until="domcontentloaded",timeout=45000)
        page.locator("#canvas").wait_for(state="visible",timeout=45000)
        def poll(needle,timeout_steps=260):
            for _ in range(timeout_steps):
                if any(needle in m for m in messages):return
                page.wait_for_timeout(250)
            raise AssertionError(f"Missing {needle} for {size}: {messages[-15:]} errors={errors}")
        poll("AF_RANGE_STATE READY")
        poll("AF_TOUCH_LAYOUT")
        layout = json.loads(next(m.split("AF_TOUCH_LAYOUT ",1)[1] for m in messages if "AF_TOUCH_LAYOUT " in m))
        assert layout["viewport"][0] >= 320 and layout["viewport"][1] >= 320,layout
        canvas = page.locator("#canvas").bounding_box()
        assert canvas and canvas["width"]>0 and canvas["height"]>0
        def tap(name):
            target=layout[name]
            px=canvas["x"]+(target[0]+layout["size"][0]/2)*canvas["width"]/layout["viewport"][0]
            py=canvas["y"]+(target[1]+layout["size"][1]/2)*canvas["height"]/layout["viewport"][1]
            assert 0 <= px <= w and 0 <= py <= h,(name,px,py,layout,canvas)
            page.touchscreen.tap(px,py)
        page.screenshot(path=str(dest/f"mobile-{w}x{h}-ready.png"))
        tap("begin")
        poll("AF_RANGE_STATE RUNNING")
        page.screenshot(path=str(dest/f"mobile-{w}x{h}-running.png"))
        tap("reset")
        for _ in range(100):
            if sum("AF_RANGE_STATE READY" in m for m in messages)>=2:break
            page.wait_for_timeout(100)
        assert sum("AF_RANGE_STATE READY" in m for m in messages)>=2,(size,messages[-16:])
        assert not errors,errors
        return {"size":size,"layout":layout,"events":[m for m in messages if "AF_RANGE_STATE" in m],"browser_version":browser.version}
    finally:
        ctx.close()

def main(dest):
    dest.mkdir(parents=True,exist_ok=True)
    reports = []
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel="chrome",headless=True,args=["--no-sandbox","--enable-unsafe-swiftshader","--use-gl=angle","--use-angle=swiftshader"])
        try:
            for size in [(844,390),(390,844),(1024,768)]:
                reports.append(exercise(browser,size,dest))
                print("AF_MOBILE_BROWSER_PASS",size,flush=True)
        finally:
            (dest/"mobile-browser-report.json").write_text(json.dumps(reports,indent=2))
            browser.close()

if __name__=="__main__":
    main(Path(sys.argv[1]))
