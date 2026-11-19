"""Check actual generated links and TOC targets, without network dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
ROOT = Path(__file__).resolve().parents[1] / '_site'
class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, 'Duplicate ID'
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if name in attrs:
                self.urls.append(attrs[name])
pages = {}
for path in ROOT.rglob('*.html'):
    parsed = Page()
    text = path.read_text(encoding='utf-8')
    assert '<html lang="zh-CN">' in text and '<main id="main">' in text
    parsed.feed(text)
    pages[path.resolve()] = parsed
assert (ROOT / 'index.html').resolve() in pages
for path, page in pages.items():
    for url in page.urls:
        parts = urlsplit(url)
        if parts.scheme or parts.netloc:
            continue
        target = (ROOT / unquote(parts.path).lstrip('/')) if parts.path.startswith('/') else path.parent / unquote(parts.path)
        if not parts.path:
            target = path
        if target.is_dir():
            target = target / 'index.html'
        target = target.resolve()
        assert target.exists(), f'{path}: broken link {url}'
        if parts.fragment and target in pages:
            assert unquote(parts.fragment) in pages[target].ids, f'{path}: missing anchor {url}'
print(f'PASS: {len(pages)} pages; all local links, resources and anchors resolve')
