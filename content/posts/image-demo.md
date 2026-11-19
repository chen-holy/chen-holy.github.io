---
{"title":"图片插入示例：给文章配一张图","date":"2026-11-19","tags":["博客","使用教程"],"summary":"通过一张本地示例图片，演示 Markdown 图片、图片链接与尺寸设置的写法。"}
---

## 最简单的图片插入

下面是一张保存在博客仓库里的示例图片。图片会随文章一起发布，不依赖外部图床。

![绿色山峦、湖水与日出的示例插画](/assets/images/image-demo/landscape.svg)

上面的实际效果对应下面这段 Markdown。复制到其他文章中也能使用：

```markdown
![绿色山峦、湖水与日出的示例插画](/assets/images/image-demo/landscape.svg)
```

方括号里填写图片说明，圆括号里填写图片路径。说明文字有助于读屏器理解图片，图片加载失败时也能提供提示。

## 图片文件放在哪里

本示例的图片实际位于：

```text
/home/chen-holy.github.io/assets/images/image-demo/landscape.svg
```

文章实际位于：

```text
/home/chen-holy.github.io/content/posts/image-demo.md
```

网页引用时只需从 `/assets/` 开始，不要填写 Docker 内的 `/home/chen-holy.github.io` 路径，也不要写 `_site`。

建议每篇文章建立一个图片子目录。PNG、JPG、WebP 等图片也可以用同样的方式插入，只需替换路径和扩展名。

## 点击图片查看原图

如果想让读者点击图片打开图片文件，可以把图片放进链接中：

[![点击查看山间日出原图](/assets/images/image-demo/landscape.svg)](/assets/images/image-demo/landscape.svg)

对应写法：

```markdown
[![点击查看山间日出原图](/assets/images/image-demo/landscape.svg)](/assets/images/image-demo/landscape.svg)
```

## 设置图片宽度和图注

普通 Markdown 图片会根据文章宽度自动缩放。如果需要指定宽度并添加图注，也可以直接写 HTML：

<figure style="margin:24px 0">
  <img src="/assets/images/image-demo/landscape.svg" alt="山间日出示例插画" width="420" loading="lazy">
  <figcaption>图：山间日出。这张图的显示宽度为 420 像素，小屏幕上会自动缩小。</figcaption>
</figure>

对应写法：

```html
<figure style="margin:24px 0">
  <img src="/assets/images/image-demo/landscape.svg" alt="山间日出示例插画" width="420" loading="lazy">
  <figcaption>图：山间日出。这张图的显示宽度为 420 像素，小屏幕上会自动缩小。</figcaption>
</figure>
```

## 换成自己的图片

1. 将图片复制到 `assets/images/你的文章名/`。
2. 把本文示例中的图片路径替换成你的路径。
3. 修改图片说明。
4. 将文章和图片一起 `git add`、`git commit`、`git push`。

GitHub Actions 会自动构建并发布，图片也会一起上线。

> 本文和插画都是演示素材。学会后可以直接修改，也可以删除文章和对应图片目录。
