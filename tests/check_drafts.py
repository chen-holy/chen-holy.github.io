"""Exercise draft publishing transitions in an isolated temporary site."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    shutil.copyfile(SOURCE / 'build.py', root / 'build.py')
    shutil.copyfile(SOURCE / 'site.json', root / 'site.json')
    shutil.copytree(SOURCE / 'assets', root / 'assets')
    (root / 'content/posts').mkdir(parents=True)
    (root / 'content/about.md').write_text('# About', encoding='utf-8')
    article = root / 'content/posts/draft-test.md'
    meta = {'title': 'Draft title marker', 'date': '2026-11-19', 'tags': ['draft-only-tag'], 'summary': 'Example'}
    def write():
        article.write_text('---\n' + json.dumps(meta) + '\n---\n## Body\nDraft body marker', encoding='utf-8')
    def build():
        subprocess.run([sys.executable, str(root / 'build.py')], check=True, capture_output=True)
    def published():
        assert (root / '_site/posts/draft-test/index.html').exists()
        assert (root / '_site/tags/draft-only-tag/index.html').exists()
        assert 'Draft title marker' in (root / '_site/index.html').read_text(encoding='utf-8')
    write(); build(); published()  # Omitted draft remains backwards compatible.
    meta['draft'] = True
    write(); build()
    assert not (root / '_site/posts/draft-test').exists()
    assert not (root / '_site/tags/draft-only-tag').exists()
    for page in (root / '_site').rglob('*.html'):
        text = page.read_text(encoding='utf-8')
        assert 'Draft title marker' not in text and 'Draft body marker' not in text
        assert 'draft-only-tag' not in text
    assert '00 篇文章' in (root / '_site/index.html').read_text(encoding='utf-8')
    meta['draft'] = False
    write(); build(); published()
    meta['draft'] = 'true'
    write()
    result = subprocess.run([sys.executable, str(root / 'build.py')], capture_output=True, text=True)
    assert result.returncode != 0 and 'draft must be true or false' in result.stderr
print('PASS: default publication, draft exclusion, stale page/tag cleanup, republication and invalid flag')
