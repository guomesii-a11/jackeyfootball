---
name: hero-gradient-and-logo-size
overview: Hero 标题改回红黄渐变（from-forward to-gold），顶部导航 logo 字体加大更显眼。
todos:
  - id: hero-gradient
    content: HomeView.vue hero 渐变改为红黄 from-forward via-orange-400 to-gold
    status: completed
  - id: logo-size
    content: App.vue logo 字号加大到 text-2xl，header py-3 到 py-4
    status: completed
---

## 用户需求

1. HomeView 大标题从浅蓝渐变改回原来的红黄渐变色。
2. 顶部 "JackeyFootball" 标志加大、更显眼。

## 修改内容

- HomeView hero h1 将渐变 class 由 `from-sky-300 via-sky-400 to-cyan-300` 改为 `from-forward via-orange-400 to-gold`（forward=#FF5A36, gold=#FFC53D），恢复红黄渐变。
- App.vue logo 字号由 `text-lg`/`text-xl` 分别提升为 `text-2xl`/`text-2xl`，顶部 header 内边距 `py-3` 升至 `py-4`，使整体导航区更显眼。