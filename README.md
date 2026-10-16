# 智能手环蓝牙私有通信协议文档

在线阅读：<https://realmcu.github.io/HoneyProtocol/>

文档源文件位于 `docs/`（reStructuredText），由 [Sphinx](https://www.sphinx-doc.org/) 生成静态站点，
推送到 `main` 分支后由 GitHub Actions 构建并发布到 GitHub Pages。

## 协议内容分层

- `docs/protocol/`：由 `docs/assets/protocol/cavo-realtek-watch-protocol.xlsx` 自动生成的新协议规范，Excel 是这一层的事实来源。
- `docs/commands/`：设备端当前实现状态、历史命令格式和实现差异，不等同于 Excel 中的目标协议。

生成页面请勿直接修改。更新 Excel 后执行：

```bash
python tools/sync_protocol.py
python tools/sync_protocol.py --check
```

导入工具会校验完整命令示例的 `v-length`、Excel 公式错误和引用缺口，并生成 `docs/protocol/source.json`。CI 会执行 `--check`，防止 Excel 与生成页面不一致。

## 本地预览

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/sphinx-build -W --keep-going -b html docs site
python3 -m http.server -d site 8000  # 浏览器打开 http://127.0.0.1:8000
```

## 编写约定

- 每个 L2 命令一页，放在 `docs/commands/`；新增页面需加入对应索引页的 `toctree`。
- 字节布局、帧结构等使用 `.. code-block:: text`；时序图使用 `.. mermaid::`。
- 与设备端实现不一致之处使用 Sphinx admonition：

  ```rst
  .. warning:: 实现差异

     设备端尚未实现……
  ```

- 提交前执行 `sphinx-build -W --keep-going -b html docs site`，确保没有断链和格式警告。
