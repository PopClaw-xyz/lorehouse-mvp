"""Source-bundle membership rules; exclude only local build/dependency directories."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
IGNORED={'node_modules','target','dist','.venv','__pycache__','.git'}
# One exact filename, not a pattern and not a hidden-file exemption: a macOS
# file browser writes .DS_Store into any directory it displays, so a bundle
# nobody edited stops verifying. Every other unlisted file is still a
# membership mismatch, which is the whole point of the check.
IGNORED_NAMES={'.DS_Store'}

def member(relative):
    """True when this relative path is part of the sealed source set."""
    if any(part in IGNORED for part in relative.parts):return False
    if relative.name in IGNORED_NAMES:return False
    if relative.as_posix()=='CONTRACT-MANIFEST.json':return False
    return True

def paths():
    out=[]
    for p in ROOT.rglob('*'):
        relative=p.relative_to(ROOT)
        if not member(relative):continue
        if p.is_symlink():raise ValueError('source symlinks are not allowed: '+str(relative))
        if p.is_file():out.append(relative.as_posix())
    return sorted(out)

def entries():
    return [{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths()]

def digest(rows):
    text=''.join(r['sha256']+'  '+r['path']+'\n' for r in rows)
    return hashlib.sha256(text.encode()).hexdigest()
