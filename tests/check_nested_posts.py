"""Verify recursive discovery, stable URLs, and duplicate slug protection."""
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
    result = build(ok=False)
    assert 'Duplicate article filename' in result.stderr
    assert 'other/root-post.md' in result.stderr and 'different/root-post.md' in result.stderr
    # Failed duplicate validation preserves the previous valid output.
    assert (out / 'posts/root-post/index.html').read_text(encoding='utf-8') == before
    duplicate.unlink()
    build()
    (root / 'tests').mkdir()
    shutil.copyfile(SOURCE / 'tests/check_build.py', root / 'tests/check_build.py')
    subprocess.run([sys.executable, str(root / 'tests/check_build.py')], check=True)
print('PASS: recursive folders, Unicode folders, pagination, drafts, stable URLs and duplicate filenames')
