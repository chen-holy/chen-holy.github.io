# Chen Holy 的个人博客

简洁、响应式的 Markdown 静态博客，部署至 https://chen-holy.github.io 。

## 文件位置

- `site.json`：站点名称、描述、网址、GitHub 仓库。
- `assets/favicon.svg`：浏览器标签页 / 博客 URL 的小图标，直接替换此文件即可；使用 PNG 时还需修改 `build.py` 中的 favicon 链接及 MIME 类型。
- `content/posts/`：博客文章，每篇一个 `.md` 文件。
- `content/about.md`：个人介绍；当前是可自行修改的初始文案。
- `assets/style.css`：颜色、字体、响应式样式。
- `assets/app.js`：目录高亮、阅读进度和评论加载。
- `build.py`：生成页面与标签归档。
- `.github/workflows/pages.yml`：推送 main 后自动构建与部署。
- `_site/`：生成结果，不提交，切勿直接编辑。

## 1. 新增文章

在 `content/posts/` 新建例如 `my-first-post.md`。文件名仅使用小写英文字母、数字、连字符；它决定永久链接 `/posts/my-first-post/`，发布后建议不要改名，以免影响外链及评论关联。

文件内容如下。开头两条 `---` 之间是 **JSON，不是 YAML**，字符串需使用双引号，不可有尾逗号：

```markdown
---
{"title":"我的第一篇文章","date":"2026-11-19","tags":["Python","学习"],"summary":"简短介绍这篇文章。"}
---

## 第一个章节

正文使用 Markdown，可插入图片、链接、表格、列表与代码块。

### 子章节

二级及以下标题自动进入目录，滚动时高亮当前位置。
```

日期使用 `YYYY-MM-DD`，文章按日期倒序排列。这里不做预约发布，未来日期也会显示。建议正文从二级标题开始，文章标题会自动生成。

图片存入 `assets/images/` 后使用 `![说明](/assets/images/example.png)` 引用。

## 2. 标签增删与文章删除

直接修改文章 JSON 的 `tags` 数组，可同时设置多个标签，或使用空数组 `[]`。无须维护单独的标签配置。新增标签自动生成归档，删除最后一篇关联文章中的标签后，对应归档自动消失。点击首页、文章页上的标签即可分类浏览。

删除对应 `.md` 文件即删除文章。每次构建会重新生成 `_site`，不会残留已删除的页面。GitHub Issues 中的历史评论不会自动删除。

## 3. 修改个人介绍与外观

编辑 `content/about.md` 修改个人介绍。编辑 `site.json` 修改名称、副标题、描述。`url` 是站点的完整域名，不带结尾斜杠；本项目针对根域名部署，如迁移到带子路径的项目站点，需要同步调整页面中的根路径链接。

修改主色请搜索 `assets/style.css` 中的 `#26735b`。头像目前为纯文字 `C.`，在 `build.py` 的 `about-layout` 中修改。

## 4. 免费评论启用（需要仓库所有者完成一次安装）

采用 Utterances：官方说明开源、无广告、无跟踪、永久免费。数据保存于 GitHub Issues，不需要付费服务器、数据库或 API Key。评论者需要 GitHub 账号。

1. 确保仓库为公开仓库，Settings → General → Features 启用 Issues。
2. 打开 https://github.com/apps/utterances ，安装并只授权 `chen-holy.github.io` 仓库。
3. 页面已通过 `site.json` 的 `repo` 设置为 `chen-holy/chen-holy.github.io`，无须填写 ID。
4. 上线后进入文章，用 GitHub 登录发出第一条评论，系统会自动建立关联 Issue。

评论按文章路径 `pathname` 关联，改标题不影响评论，改文件名则会改变关联路径。脚本无法加载或 App 未安装时，可用评论区下方的 GitHub 留言链接；该链接是手动发 Issue 的备用入口，已有讨论可以在 Issues 中查看。

参考：https://utteranc.es/ 。对比方案 giscus 也免费，但需要启用 Discussions、安装 App 并配置 repository/category ID。这里采用配置更简单的 Utterances。未引入任何收费评论服务。

## 5. Docker 本地构建与预览

```bash
docker exec -it ubuntu20 /bin/bash
cd /home/chen-holy.github.io
python3 -m pip install -r requirements.txt
python3 build.py
python3 -m http.server 8000 --directory _site --bind 0.0.0.0
```

需要 Docker 将 8000 端口映射到主机才能通过主机浏览器访问；已有容器未映射时，也可把 `_site` 拷贝至主机并运行静态 HTTP 服务。不要直接双击 HTML，因为页面使用根路径链接。

若出现连接旧代理 `192.168.31.162` 超时，先检查当前环境；允许直连时可在当前 shell 临时执行 `unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy` 后重试。不要把代理凭据提交到 Git。

## 6. 发布更新

```bash
cd /home/chen-holy.github.io
python3 build.py
python3 tests/check_build.py
git add .
git commit -m "Update blog"
git push origin main
```

GitHub 仓库 Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。工作流也尝试通过 `configure-pages` 自动启用 Pages，若仓库权限或策略不允许，需所有者手动设置。到 Actions 中查看 Deploy blog 是否成功。不要把“push 成功”等同于“站点已上线”；以部署工作流成功和实际 URL 可访问为准。

工作流使用 Python 3.12 安装固定版本 Markdown，将 `_site` 上传为 Pages artifact 后部署，无需提交构建产物。

GitHub 官方教程：
- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## 7. 校验

`python3 tests/check_build.py` 验证生成页面的站内链接、资源路径、文章目录锚点与基本页面结构。新增和删除文章之后先运行构建再执行校验。示例文章可以自行删除或替换。


## 8. 草稿：先 push，暂不发布

在文章顶部 JSON 中添加 `"draft": true`：

```markdown
---
{"title":"还没写完的文章","date":"2026-11-19","tags":["学习"],"summary":"写作中","draft":true}
---

这里可以先写一部分正文。
```

`draft` 必须使用 JSON 布尔值 `true` 或 `false`，不能写成字符串 `"true"`。

- `true`：不生成文章网页，不出现在首页、标签归档和文章计数中。
- `false` 或省略 `draft`：正常发布。
- 写完后将 `true` 改为 `false`，再 push 即可发布。
- 已发布的文章改为草稿后，下次成功部署将移除网页，原文章链接会返回 404；GitHub Issues 评论仍保留。

草稿仅跳过网站生成，并不是私密存储：公开 GitHub 仓库中的 Markdown 和提交历史仍可被查看，`assets/` 中的图片也会随网站发布。

测试：`python3 tests/check_drafts.py` 在临时目录验证发布、转为草稿、归档清理和重新发布，不修改真实文章。


## 9. 年月归档与分页

首页保留最近文章，增加“按年月归档”入口；顶部导航也可进入归档。
归档根据文章 JSON 中的 `date` 自动生成，点击年份查看全年，点击月份查看当月。

- 年月索引：`/archives/`
- 年份示例：`/archives/2026/`
- 月份示例：`/archives/2026/11/`
- 首页、标签、年份、月份文章列表均每页最多 9 篇，按日期倒序排列。
- 第二页路径分别为 `/page/2/`、`/tags/标签/page/2/`、`/archives/2026/page/2/`、`/archives/2026/11/page/2/`。
- 草稿不参与归档、文章计数和分页。删除文章后重建会清理无效分页及空归档。
- 每页数量由 `build.py` 中的 `PAGE_SIZE = 9` 控制。

执行 `python3 tests/check_pagination.py` 可在临时目录生成多篇测试文章，验证分页边界、年月分组和草稿排除；不会向线上发布测试文章。
