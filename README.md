# 智能手环蓝牙私有通信协议文档

在线阅读：<https://realmcu.github.io/HoneyProtocol/>

文档源文件位于 `docs/`（reStructuredText），由 [Sphinx](https://www.sphinx-doc.org/) 生成静态站点，
推送到 `main` 分支后由 GitHub Actions 构建并发布到 GitHub Pages。

## 命令页来源

第 3 章 L2 Command 详解的页面都在 `docs/protocol/`。**在线 HTML 为对外规范**。

- **L2 命令页**（`0x02`～`0x05`、`0x0A`、`0x11`～`0x13` 等）：在 `docs/protocol/*.rst` 直接维护；可选从 HoneyBox `ws-protocol-*.md` 运行 `python tools/import_ws_protocol_md.py` 生成初稿后再审。
- **附表**（天气类型、语言编码）：`docs/protocol/weather-types.rst`、`language-codes.rst` 手工维护。
- **索引**：`docs/protocol/index.rst` 与 `source.json` 由 `python tools/sync_protocol.py` 根据各命令页状态生成。

```bash
python tools/import_ws_protocol_md.py   # 可选：从 HoneyBox md 刷新 L2 页
python tools/sync_protocol.py           # 刷新 index.rst / source.json
python tools/sync_protocol.py --check   # CI 使用
```

## 本地预览

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/sphinx-build -W --keep-going -b html docs site
python3 -m http.server -d site 8000  # 浏览器打开 http://127.0.0.1:8000
```

## 编写约定

- 每个 L2 命令一页，二级标题为 **命令格式 / 规则 / 具体命令**；`:tocdepth: 2` 放在页面标题之前，侧栏只显示章节。
- 字节布局、帧结构等使用 `.. code-block:: text`；时序图使用 `.. mermaid::`。
- 与设备端实现不一致之处使用 Sphinx admonition：

  ```rst
  .. warning:: 实现差异

     设备端尚未实现……
  ```

- 提交前执行 `sphinx-build -W --keep-going -b html docs site`，并确保 `python tools/sync_protocol.py --check` 通过。
