"""Build the actual Godot web game and integrate it into an isolated HORIZEN shell copy."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
ORIGIN = 'https://github.com/godotengine/godot-builds/releases/download/4.7.2-stable/'
ENGINE = 'Godot_v4.7.2-stable_linux.x86_64'
ENGINE_SHA = 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4'
TEMPLATES = 'Godot_v4.7.2-stable_export_templates.tpz'


def download(name, dest):
    subprocess.run(['curl','-fsSL','--retry','3',ORIGIN+name,'-o',str(dest)],check=True)


def digest(p, alg):
    with p.open('rb') as f:
        return hashlib.file_digest(f,alg).hexdigest()


def engine_run(args):
    result = subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    print(result.stdout,flush=True)
    if result.returncode or re.search(r'(?:^|\s)(?:SCRIPT ERROR|ERROR|FATAL):',result.stdout):
        raise RuntimeError('Godot import/export returned an error')


def csp_entry(dest, shell):
    # Generated HTML contains inline bootstrap and CSS. Extract only the two known blocks.
    html=(dest/'index.html').read_text()
    for tag,filename,replacement in [('style','range.css','<link rel="stylesheet" href="range.css">'),('script','range-boot.js','<script src="range-boot.js"></script>')]:
        pattern=rf'<{tag}>(.*?)</{tag}>'
        blocks=re.findall(pattern,html,flags=re.S)
        if len(blocks)!=1:
            raise ValueError('Unexpected Godot export template: '+tag)
        (dest/filename).write_text(blocks[0])
        html=re.sub(pattern,lambda _:replacement,html,count=1,flags=re.S)
    (dest/'index.html').write_text(html)
    # Only the exact exported game page can compile WASM. Preserve all shell directives.
    server=shell/'serve.py'
    code=server.read_text()
    anchor='    def guess_type(self, path):'
    if code.count(anchor)!=1:
        raise ValueError('HORIZEN server changed; review staging patch')
    method='''    def send_header(self, keyword, value):
        if (keyword.lower() == 'content-security-policy' and
                self.path.partition('?')[0] == '/builds/unbound-reach/index.html'):
            value = value.replace("script-src 'self';", "script-src 'self' 'wasm-unsafe-eval';")
        super().send_header(keyword, value)

'''
    server.write_text(code.replace(anchor,method+anchor))


def run(work, shell):
    work.mkdir(parents=True,exist_ok=True)
    zipped=work/'engine.zip'; download(ENGINE+'.zip',zipped)
    if digest(zipped,'sha256')!=ENGINE_SHA: raise ValueError('Engine digest mismatch')
    binary=work/'godot'
    with ZipFile(zipped) as z: binary.write_bytes(z.read(ENGINE))
    binary.chmod(0o755)
    version=subprocess.check_output([str(binary),'--version'],text=True).strip()
    if not version.startswith('4.7.2.stable'): raise ValueError(version)
    sums=work/'SHA512-SUMS.txt'; download(sums.name,sums)
    expected=next(line.split()[0] for line in sums.read_text().splitlines() if line.split()[-1].lstrip('*')==TEMPLATES)
    tpz=work/'templates.tpz'; download(TEMPLATES,tpz)
    if digest(tpz,'sha512')!=expected: raise ValueError('Template digest mismatch')
    templates=Path.home()/'.local/share/godot/export_templates/4.7.2.stable'; templates.mkdir(parents=True,exist_ok=True)
    with ZipFile(tpz) as z:
        for member in z.namelist():
            name=Path(member).name
            if name.startswith('web_') and name.endswith('.zip'):
                with z.open(member) as source,(templates/name).open('wb') as output:
                    shutil.copyfileobj(source,output)
    tpz.unlink()
    stage=work/'game'; shutil.copytree(ROOT/'game',stage,ignore=shutil.ignore_patterns('.godot'))
    p=stage/'project.godot'; project=p.read_text(); old='run/main_scene="res://scenes/bootstrap/main.tscn"'
    if project.count(old)!=1: raise ValueError('Unexpected bootstrap')
    p.write_text(project.replace(old,'run/main_scene="res://scenes/levels/arenas/unbound_reach.tscn"'))
    (stage/'export_presets.cfg').write_text('[preset.0]\nname="Reach Web"\nplatform="Web"\nrunnable=true\nexport_filter="all_resources"\ninclude_filter=""\nexclude_filter=""\nexport_path=""\n[preset.0.options]\nvariant/extensions_support=false\nvariant/thread_support=false\nhtml/canvas_resize_policy=2\nprogressive_web_app/enabled=false\n')
    dest=shell/'builds/unbound-reach';dest.mkdir(parents=True,exist_ok=True)
    cmd=[str(binary),'--headless','--path',str(stage)]
    engine_run(cmd+['--editor','--import','--quit'])
    engine_run(cmd+['--export-release','Reach Web',str(dest/'index.html')])
    for name in ('index.html','index.js','index.pck','index.wasm'):
        if not (dest/name).stat().st_size: raise ValueError('Empty export '+name)
    csp_entry(dest,shell)
    record={'game_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'horizen_base':'f92ef7c74d2106ac8c16bcfd50e6e47a17d0fb6e','staged_server':'WASM compilation enabled for exact game document only; no unsafe-inline or JS eval','engine':version,'template_sha512':expected,'world_entry':'./builds/unbound-reach/index.html'}
    (shell/'BUILD_INFO.json').write_text(json.dumps(record,indent=2))


if __name__=='__main__': run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
