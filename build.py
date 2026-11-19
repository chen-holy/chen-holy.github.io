"""Build a portable Markdown blog. Run: python3 build.py."""
import datetime
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote
import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
config = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
e = lambda value: html.escape(str(value), quote=True)

def render(source):
    md = markdown.Markdown(extensions=["fenced_code", "tables", "toc", "sane_lists"], extension_configs={"toc": {"permalink": False}})
    body = md.convert(source)
    return body, md.toc

def tag_url(tag):
    return "/tags/" + quote(tag, safe="") + "/"

def tags_html(tags):
    return '<div class="tags">' + ''.join(f'<a class="tag" href="{tag_url(t)}">{e(t)}</a>' for t in tags) + '</div>'

def page(path, title, content, active="", description=None):
    url = config['url'].rstrip('/') + path
    document = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · {e(config['title'])}</title><meta name="description" content="{e(description or config['description'])}">
<link rel="canonical" href="{e(url)}"><link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="stylesheet" href="/assets/style.css"><script src="/assets/app.js" defer></script></head>
<body><a class="skip" href="#main">跳到正文</a><header class="header"><a class="brand" href="/">{e(config['title'])}<span> / 博客</span></a>
<nav aria-label="主导航">{''.join(f'<a href="{href}" '+ ('aria-current="page"' if active == key else '') + f'>{label}</a>' for key,href,label in [('home','/','文章'),('tags','/tags/','标签'),('about','/about/','关于')])}</nav></header>
<main id="main">{content}</main><footer><span>© {datetime.date.today().year} {e(config['title'])}</span><span>文字有迹，思考有声。 <a href="https://github.com/{e(config['repo'])}">GitHub</a></span></footer></body></html>'''
    target = OUT / unquote(path).lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")

posts = []
for source in (ROOT / 'content/posts').glob('*.md'):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', source.stem):
        raise ValueError(f'Use a lowercase ASCII slug: {source.name}')
    parts = source.read_text(encoding='utf-8').split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f'Missing JSON front matter: {source}')
    data = json.loads(parts[1])
    if not isinstance(data, dict):
        raise ValueError(f'Front matter must be a JSON object: {source}')
    if 'draft' in data and type(data['draft']) is not bool:
        raise ValueError(f'draft must be true or false (without quotes): {source}')
    if data.get('draft', False):
        continue
    for key in ['title', 'date', 'tags', 'summary']:
        if key not in data:
            raise ValueError(f'Missing {key}: {source}')
    datetime.date.fromisoformat(data['date'])
    if not isinstance(data['tags'], list) or any(not isinstance(t, str) or not t.strip() or t in ['.', '..'] or '/' in t or "\\" in t for t in data['tags']):
        raise ValueError(f'Invalid tags: {source}')
    data['tags'] = list(dict.fromkeys(data['tags']))
    data['slug'] = source.stem
    data['body'], data['toc'] = render(parts[2])
    posts.append(data)
posts.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
# Rebuild output so removed posts and tags disappear.
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / 'assets', OUT / 'assets')
(OUT / '.nojekyll').touch()

def cards(items):
    return '<div class="post-list">' + ''.join(f'''<article class="post-card"><time datetime="{p['date']}">{p['date'].replace('-', '.')}</time><div><h2><a href="/posts/{p['slug']}/">{e(p['title'])}</a></h2><p>{e(p['summary'])}</p>{tags_html(p['tags'])}</div></article>''' for p in items) + '</div>'

page('/', '文章', f'''<section class="hero"><p class="eyebrow">CHEN HOLY / PERSONAL JOURNAL</p><h1>把思考写下来。<br><span>让成长有迹可循。</span></h1><p>{e(config['subtitle'])}</p><a class="text-link" href="/about/">认识一下我</a></section><section><div class="section-title"><h2>最近的文字</h2><span>{len(posts):02d} 篇文章</span></div>{cards(posts) if posts else '<p>第一篇文章，正在酝酿中。</p>'}</section>''', 'home')
all_tags = sorted({t for p in posts for t in p['tags']})
page('/tags/', '标签', '<div class="page-intro"><p class="eyebrow">EXPLORE BY TOPIC</p><h1>循着兴趣，继续阅读。</h1><p>每一个标签，都是一条探索的线索。</p></div><div class="tag-grid">' + ''.join(f'<a href="{tag_url(t)}"><strong>{e(t)}</strong><span>{sum(t in p["tags"] for p in posts)} 篇文章</span></a>' for t in all_tags) + '</div>', 'tags')
for tag in all_tags:
    page(tag_url(tag), tag, f'<div class="page-intro"><a class="text-link" href="/tags/">全部标签</a><h1>{e(tag)}</h1><p>关于这个主题的文字</p></div>' + cards([p for p in posts if tag in p['tags']]), 'tags')
about, toc = render((ROOT / 'content/about.md').read_text(encoding='utf-8'))
page('/about/', '关于我', '<div class="about-layout"><div class="avatar" aria-hidden="true">C.</div><article class="prose">' + about + '</article></div>', 'about')
for p in posts:
    issue = 'https://github.com/' + config['repo'] + '/issues/new?title=' + quote('[评论] /posts/' + p['slug'] + '/')
    page('/posts/' + p['slug'] + '/', p['title'], f'''<div class="reading-progress" aria-hidden="true"></div><header class="article-header"><a class="text-link" href="/">全部文章</a><p class="eyebrow"><time datetime="{p['date']}">{p['date']}</time> / {max(1, len(p['body']) // 700)} 分钟阅读</p><h1>{e(p['title'])}</h1><p>{e(p['summary'])}</p>{tags_html(p['tags'])}</header><div class="article-layout"><article class="prose" id="article-body">{p['body']}</article><aside class="article-toc"><details open><summary>本文目录</summary><nav aria-label="文章目录">{p['toc']}</nav></details></aside></div><section class="comments"><h2>聊一聊</h2><p>使用 GitHub 账号参与讨论。评论由免费的 Utterances 提供。</p><div id="comments-widget" data-repo="{e(config['repo'])}"></div><p class="comment-fallback">若评论区未加载，可<a href="{e(issue)}">在 GitHub 留言</a>，也可<a href="https://github.com/{e(config['repo'])}/issues">查看已有讨论</a>。</p></section>''', description=p['summary'])
page('/404/', '页面未找到', '<div class="page-intro"><p class="eyebrow">404</p><h1>这一页还没有写下。</h1><p>链接可能已变更，去看看其他文章吧。</p><a class="text-link" href="/">回到首页</a></div>')
shutil.copyfile(OUT / '404/index.html', OUT / '404.html')
print(f'Built {len(posts)} posts and {len(all_tags)} tags into {OUT}')
