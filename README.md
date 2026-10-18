# DaveBot 文档站

DaveBot 完整指令文档，域名 `https://docs.raivex.xyz`。由 GitHub Pages 托管，GitHub Actions 自动测试、构建和发布。

- `content/commands.json`：主要指令、别名、参数与示例；按模块分类。
- `content/pages.json`：快速开始、模块介绍、常见问题。
- `build.py`：Python 标准库生成静态页面、搜索索引与站点地图。
- `assets/`：自有样式、图标与搜索 / 复制 / 移动端导航交互。
- `.github/workflows/pages.yml`：推送 main 后自动发布。
- `server.py`：可选的本地预览服务。

```powershell
python build.py
python -m unittest discover -s tests
python server.py --root dist --port 8894
```

修改 `content/` 中对应功能的 JSON 文件并推送 main 即可更新网站，无需 VPS 或 Bot 重启。发布产物仅包含 `dist/`；仓库不保存游戏授权、账号数据或私有后端。

文档在 DaveBot 工作区按 Rust 指令解析器核对；测试检查指令覆盖、站内锚点和链接、所有文档指令的 `/d` 前缀，以及本地预览隔离。其他区服及未移植组件明确标注为不可用。

布局参考 HarukiBot NEO 文档站的分类导航、正文目录和检索方式。页面、配色、图标和文字独立制作，未使用该站代码、图片或品牌资产。
