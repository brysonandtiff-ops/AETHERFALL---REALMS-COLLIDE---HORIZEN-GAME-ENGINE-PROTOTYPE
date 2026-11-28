"""Package only the opt-in range and source. Never change the main bootstrap."""
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
SCENE = 'res://scenes/levels/arenas/unbound_reach.tscn'


def package(dest: Path) -> None:
    project = (GAME / 'project.godot').read_text()
    marker = 'run/main_scene="res://scenes/bootstrap/main.tscn"'
    if project.count(marker) != 1:
        raise ValueError('Bootstrap changed: review standalone export before building')
    files = list((GAME / 'scripts/levels/reach').glob('*.gd'))
    files.append(GAME / SCENE.removeprefix('res://'))
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    with zipfile.ZipFile(dest / 'Unbound-Reach-Godot.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('project.godot', project.replace(marker, f'run/main_scene="{SCENE}"'))
        for path in sorted(files):
            archive.write(path, path.relative_to(GAME).as_posix())
        archive.write(ROOT / 'docs/development/AF_RANGE_001.md', 'README.md')
        archive.writestr('SOURCE_COMMIT.txt', sha + '\n')
    print('Packaged native range', sha)


if __name__ == '__main__':
    package(Path(sys.argv[1]).resolve())
