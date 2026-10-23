# 智能手环蓝牙私有通信协议文档

在线阅读：<https://realmcu.github.io/HoneyProtocol/>

文档源文件位于 `docs/`（reStructuredText），由 [Sphinx](https://www.sphinx-doc.org/) 生成静态站点，
推送到 `main` 分支后由 GitHub Actions 构建并发布到 GitHub Pages。

## 命令页来源

第 3 章 L2 Command 详解的页面都在 `docs/protocol/`。**在线 HTML 为对外规范**；工作簿 Excel 仅辅助未迁移命令的编辑，不必与 RST 同步。

- **HoneyBox MD → RST**（`0x02`～`0x05`、`0x0A`、`0x11`～`0x13`）：在 `HoneyBox/docs/ws-protocol-*.md` 定稿后运行 `python tools/import_ws_protocol_md.py`，生成 `docs/protocol/*.rst`（登记在 `RST_SOURCED_DOCUMENTS`）。
- **工作簿源**：天气类型、语言编码等附录表，改 `docs/assets/protocol/cavo-realtek-watch-protocol.xlsx` 后由 `sync_protocol.py` 生成。
- **仅手写**：登记在 `MANUAL_DOCUMENTS` 中。

索引页 `docs/protocol/index.rst` 由同步脚本生成。更新 HoneyBox 协议 md 或 Excel 后执行：

```bash
python tools/import_ws_protocol_md.py
python tools/sync_protocol.py
python tools/sync_protocol.py --check
```

导入工具会校验完整命令示例的 `Length`、Excel 公式错误和引用缺口，并生成 `docs/protocol/source.json`。CI 会执行 `--check`，防止 Excel 与生成页面不一致。

## 本地预览

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/sphinx-build -W --keep-going -b html docs site
python3 -m http.server -d site 8000  # 浏览器打开 http://127.0.0.1:8000
```

## 编写约定

- 每个 L2 命令一页，放在 `docs/protocol/`；手写的新命令页需登记到 `MANUAL_DOCUMENTS`，再重新生成索引页。
- 命令页以二级标题组织章节，单条 Key 用三级标题放在“具体命令”下；`:tocdepth: 2` 放在页面标题之前，侧栏只显示章节。Excel 页的标题由同步脚本维护。
- 字节布局、帧结构等使用 `.. code-block:: text`；时序图使用 `.. mermaid::`。
- 与设备端实现不一致之处使用 Sphinx admonition：

  ```rst
  .. warning:: 实现差异

     设备端尚未实现……
  ```

- 提交前执行 `sphinx-build -W --keep-going -b html docs site`，确保没有断链和格式警告。
