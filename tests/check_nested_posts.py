"""Verify recursive discovery, stable URLs, and automatic unique slugs."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    for filename in ['build.py', 'site.json']:
        shutil.copyfile(SOURCE / filename, root / filename)
    shutil.copytree(SOURCE / 'assets', root / 'assets')
    content = root / 'content/posts'
    content.mkdir(parents=True)
    (root / 'content/about.md').write_text('# About', encoding='utf-8')
    def write(path, draft=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        meta = dict(title=path.stem, date='2026-11-19', tags=['nested'], summary='Example', draft=draft)
        path.write_text('---\n' + json.dumps(meta) + '\n---\n## Heading\nBody', encoding='utf-8')
    def build(ok=True):
        result = subprocess.run([sys.executable, str(root / 'build.py')], capture_output=True, text=True)
        assert (result.returncode == 0) == ok, result.stderr
        return result
    write(content / 'root-post.md')
    for index in range(10):
        write(content / '技术 笔记/Python/2026' / f'nested-{index}.md')
    write(content / 'drafts/unpublished.md', draft=True)
    build()
    out = root / '_site'
    assert (out / 'posts/root-post/index.html').exists()
    assert (out / 'posts/nested-0/index.html').exists()
    assert not (out / 'posts/unpublished').exists()
    assert (out / 'page/2/index.html').exists()
    assert (out / 'tags/nested/page/2/index.html').exists()
    assert (out / 'archives/2026/11/page/2/index.html').exists()
    before = (out / 'posts/root-post/index.html').read_text(encoding='utf-8')
    (content / 'other').mkdir()
    (content / 'root-post.md').rename(content / 'other/root-post.md')
    build()
    assert (out / 'posts/root-post/index.html').read_text(encoding='utf-8') == before
    # A duplicate draft is unpublished and cannot overwrite the published page.
    duplicate = content / 'different/root-post.md'
    write(duplicate, draft=True)
    build()
    write(duplicate)
    result = build()
    assert 'Duplicate filename:' in result.stdout
    assert (out / 'posts/root-post-2/index.html').exists()
    assert (out / 'posts/root-post/index.html').exists()
    # Existing numbered filenames are reserved before assigning generated suffixes.
    write(content / 'root-post-2.md')
    write(content / 'third/root-post.md')
    write(content / 'fourth/root-post.md')
    build()
    for slug in ['root-post', 'root-post-2', 'root-post-3', 'root-post-4', 'root-post-5']:
        assert (out / 'posts' / slug / 'index.html').exists()
    reserved = (out / 'posts/root-post-2/index.html').read_text(encoding='utf-8')
    assert '<title>root-post-2' in reserved
    snapshot = {p.relative_to(out): p.read_bytes() for p in out.rglob('*.html')}
    build()
    assert snapshot == {p.relative_to(out): p.read_bytes() for p in out.rglob('*.html')}
    # Further collisions with numbered bases also get unique destinations.
    write(content / 'extra/root-post-2.md')
    build()
    assert (out / 'posts/root-post-2-2/index.html').exists()
    for path in [content / 'root-post-2.md', content / 'third/root-post.md',
                 content / 'fourth/root-post.md', content / 'extra/root-post-2.md']:
        path.unlink()
    duplicate.unlink()
    build()
    (root / 'tests').mkdir()
    shutil.copyfile(SOURCE / 'tests/check_build.py', root / 'tests/check_build.py')
    subprocess.run([sys.executable, str(root / 'tests/check_build.py')], check=True)
print('PASS: recursive folders, Unicode folders, pagination, drafts, stable URLs and duplicate filenames')
