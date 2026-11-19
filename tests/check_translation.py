"""Check per-page translation URLs and protected code markup."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
ROOT = Path(__file__).resolve().parents[1] / '_site'
class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = self.translation = self.original = None
    def handle_starttag(self, tag, attrs):
        names = [key for key, value in attrs]
        assert len(names) == len(set(names)), f'Duplicate HTML attributes: {tag}'
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs['href']
        if tag == 'a' and attrs.get('class') == 'language-english':
            self.translation = attrs['href']
            assert attrs.get('target') == '_blank'
            assert 'noopener' in attrs.get('rel', '')
        if tag == 'a' and attrs.get('class') == 'language-original':
            self.original = attrs['href']
        if tag in ('pre', 'code'):
            assert attrs.get('translate') == 'no', 'Code is not protected from translation'
count = 0
for path in ROOT.rglob('*.html'):
    parser = Page()
    parser.feed(path.read_text(encoding='utf-8'))
    assert parser.canonical and parser.original == parser.canonical
    url = urlsplit(parser.translation)
    assert url.scheme == 'https' and url.netloc == 'translate.google.com'
    params = parse_qs(url.query)
    assert params['tl'] == ['en'] and params['sl'] == ['auto']
    assert params['u'] == [parser.canonical], f'Wrong translation target: {path}'
    count += 1
assert count
print(f'PASS: translation links point to each original page; code markup checked across {count} pages')
