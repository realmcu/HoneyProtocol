# 智能手环蓝牙私有通信协议文档

在线阅读：<https://realmcu.github.io/HoneyProtocol/>

文档源文件位于 `docs/`（Markdown），由 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) 生成站点，
推送到 `main` 分支后由 GitHub Actions 自动发布到 GitHub Pages。

## 本地预览

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p docs/javascripts && curl -fsSL -o docs/javascripts/mermaid.min.js \
  https://cdn.jsdelivr.net/npm/mermaid@11.17.2/dist/mermaid.min.js   # 时序图渲染脚本，不入库
.venv/bin/mkdocs serve        # 浏览器打开 http://127.0.0.1:8000 ，保存即刷新
```

## 编写约定

- 每个 L2 命令一页，放在 `docs/commands/`，新增页面需同时加入 `mkdocs.yml` 的 `nav`。
- 字节布局、帧结构等用 ```` ```text ```` 代码块；时序图可用 ```` ```mermaid ````。
- 与设备端实现不一致之处用提示块标注：

  ```markdown
  !!! warning "实现差异"
      设备端尚未实现……
  ```

- 提交前执行 `mkdocs build --strict`，确保没有断链。
