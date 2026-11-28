"""Use the official Godot web template and copy of the actual level. No JS remaking of the game."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
VERSION = '4.7.2-stable'
ORIGIN = f'https://github.com/godotengine/godot-builds/releases/download/{VERSION}/'
ENGINE = 'Godot_v4.7.2-stable_linux.x86_64'
ENGINE_SHA = 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4'
TEMPLATES = 'Godot_v4.7.2-stable_export_templates.tpz'


def download(name, target):
    subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error', '--retry', '3', ORIGIN + name, '-o', str(target)], check=True)


def run(work: Path, shell: Path):
    work.mkdir(parents=True, exist_ok=True)
    zipped = work / 'engine.zip'
    download(ENGINE + '.zip', zipped)
    with zipped.open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != ENGINE_SHA:
            raise ValueError('Godot checksum mismatch')
    with zipfile.ZipFile(zipped) as z:
        (work / 'godot').write_bytes(z.read(ENGINE))
    binary = work / 'godot'
    binary.chmod(0o755)
    version = subprocess.check_output([str(binary), '--version'], text=True).strip()
    if not version.startswith('4.7.2.stable'):
        raise ValueError(version)
    sums = work / 'SHA512-SUMS.txt'
    download('SHA512-SUMS.txt', sums)
    expected = next(line.split()[0] for line in sums.read_text().splitlines() if line.split()[-1].lstrip('*') == TEMPLATES)
    tpz = work / 'templates.tpz'
    download(TEMPLATES, tpz)
    with tpz.open('rb') as f:
        if hashlib.file_digest(f, 'sha512').hexdigest() != expected:
            raise ValueError('Template checksum mismatch')
    template_dir = Path.home() / '.local/share/godot/export_templates/4.7.2.stable'
    template_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(tpz) as z:
        for member in z.namelist():
            name = Path(member).name
            if name.startswith('web_') and name.endswith('.zip'):
                with z.open(member) as source, (template_dir / name).open('wb') as dest:
                    shutil.copyfileobj(source, dest)
    tpz.unlink()
    stage = work / 'game'
    shutil.copytree(ROOT / 'game', stage, ignore=shutil.ignore_patterns('.godot'))
    p = stage / 'project.godot'
    text = p.read_text()
    original = 'run/main_scene="res://scenes/bootstrap/main.tscn"'
    if text.count(original) != 1:
        raise ValueError('Unexpected bootstrap; not altering project')
    p.write_text(text.replace(original, 'run/main_scene="res://scenes/levels/arenas/unbound_reach.tscn"'))
    (stage / 'export_presets.cfg').write_text('[preset.0]\nname="Reach Web"\nplatform="Web"\nrunnable=true\nexport_filter="all_resources"\nexport_path=""\n[preset.0.options]\nvariant/extensions_support=false\nvariant/thread_support=false\nhtml/canvas_resize_policy=2\nprogressive_web_app/enabled=false\n')
    dest = shell / 'builds/unbound-reach'
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(binary), '--headless', '--path', str(stage), '--editor', '--import', '--quit'], check=True)
    subprocess.run([str(binary), '--headless', '--path', str(stage), '--export-release', 'Reach Web', str(dest / 'index.html')], check=True)
    for name in ('index.html', 'index.js', 'index.pck', 'index.wasm'):
        if not (dest / name).stat().st_size:
            raise ValueError('Empty web export: ' + name)
    (shell / 'BUILD_INFO.json').write_text(json.dumps({'game_sha': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(), 'shell_sha':'f92ef7c74d2106ac8c16bcfd50e6e47a17d0fb6e','engine':version,'template_sha512':expected,'world_entry':'./builds/unbound-reach/index.html'}, indent=2))


if __name__ == '__main__':
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
