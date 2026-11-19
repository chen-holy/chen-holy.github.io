"""Validate generated pagination and archives using temporary articles."""
import json
import re
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
    def post(index, date='2026-11-19', draft=False):
        meta = dict(title=f'Article {index}', date=date, tags=['shared'], summary='Example', draft=draft)
        (content / f'article-{index:03d}.md').write_text('---\n' + json.dumps(meta) + '\n---\n## Heading\nText', encoding='utf-8')
    def build():
        subprocess.run([sys.executable, str(root / 'build.py')], check=True, capture_output=True)
    def text(path):
        return (root / '_site' / path / 'index.html').read_text(encoding='utf-8')
    def slugs(path):
        return re.findall(r'<h2><a href="/posts/([^/]+)/">', text(path))
    def check_list(base, count):
        found = []
        total = max(1, (count + 8) // 9)
        for number in range(1, total + 1):
            path = base if number == 1 else f'{base}page/{number}/'
            entries = slugs(path)
            assert len(entries) == min(9, max(0, count - 9 * (number - 1)))
            found.extend(entries)
            if number > 1:
                previous = '/' + (base if number == 2 else f'{base}page/{number-1}/')
                assert f'href="{previous}">上一页' in text(path)
            if number < total:
                assert f'href="/{base}page/{number+1}/">下一页' in text(path)
        assert len(found) == len(set(found)) == count
        assert not (root / '_site' / base / f'page/{total+1}').exists()
        return found
    for count in [0, 1, 9, 10, 18, 19]:
        for path in content.glob('*.md'):
            path.unlink()
        for index in range(count):
            post(index)
        post(999, '2020-01-01', draft=True)
        build()
        expected = [f'article-{i:03d}' for i in reversed(range(count))]
        assert check_list('', count) == expected
        if count:
            for base in ['tags/shared/', 'archives/2026/', 'archives/2026/11/']:
                assert check_list(base, count) == expected
        else:
            assert not (root / '_site/archives/2026').exists()
        assert not (root / '_site/archives/2020').exists()
        assert not (root / '_site/posts/article-999').exists()
    # A second year and another month are independently grouped and counted.
    post(100, '2025-12-31')
    post(101, '2026-10-01')
    build()
    assert check_list('archives/2025/', 1) == ['article-100']
    assert check_list('archives/2025/12/', 1) == ['article-100']
    assert check_list('archives/2026/10/', 1) == ['article-101']
    assert len(check_list('archives/2026/', 20)) == 20
    index = text('archives/')
    assert index.index('/archives/2026/') < index.index('/archives/2025/')
    assert index.index('/archives/2026/11/') < index.index('/archives/2026/10/')
    # Run the real link/anchor checker against this generated fixture.
    (root / 'tests').mkdir()
    shutil.copyfile(SOURCE / 'tests/check_build.py', root / 'tests/check_build.py')
    subprocess.run([sys.executable, str(root / 'tests/check_build.py')], check=True)
    for path in content.glob('*.md'):
        path.unlink()
    build()
    assert not (root / '_site/page/2').exists()
    assert not (root / '_site/archives/2026').exists()
    assert not (root / '_site/tags/shared').exists()
print('PASS: 0/1/9/10/18/19 posts, all list types, ordering, month/year grouping, drafts and stale page cleanup')
