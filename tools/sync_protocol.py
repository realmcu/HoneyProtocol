#!/usr/bin/env python3
"""Maintain generated protocol index/manifest; RST pages are edited in docs/protocol/."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs/protocol"
MANIFEST = OUTPUT_DIR / "source.json"

RST_SOURCED_DOCUMENTS = (
    ("0x02-settings.rst", "0x02 设置命令", "02"),
    ("0x03-bind.rst", "0x03 绑定命令", "03"),
    ("0x04-notification.rst", "0x04 通知命令", "04"),
    ("0x05-data.rst", "0x05 数据命令", "05"),
    ("0x0a-log.rst", "0x0A 日志命令", "0A"),
    ("0x11-measurement.rst", "0x11 点测命令", "11"),
    ("0x12-simulator.rst", "0x12 模拟数据命令", "12"),
    ("0x13-audio.rst", "0x13 音频命令", "13"),
)

MANUAL_DOCUMENTS = (
    ("0x01-firmware-upgrade.rst", "0x01 固件升级命令", "01"),
    ("0x06-factory-test.rst", "0x06 工厂测试命令", "06"),
    ("0x08-dump-stack.rst", "0x08 Dump Stack 命令", "08"),
    ("0x09-flash-read.rst", "0x09 测试 Flash 读取命令", "09"),
    ("0x0c-ble-conn-param.rst", "0x0C BLE 连接参数命令", "0C"),
    ("0x0d-wifi-provision.rst", "0x0D WiFi 配网命令", "0D"),
    ("0x10-file-transfer.rst", "0x10 文件传输命令", "10"),
)

APPENDIX_DOCUMENTS = (
    ("weather-types.rst", "天气类型"),
    ("language-codes.rst", "语言编码"),
)

RST_HEADING_CHARS = ("=", "-", "~", "^")
PACKET = re.compile(r"^(?:[0-9A-Fa-f]{2})(?:\s+[0-9A-Fa-f]{2}){4,}$")
PACKET_WITH_GAP = re.compile(
    r"^[0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})*(?:\s+(?:…|\.\.\.)(?:\s+[0-9A-Fa-f]{2})*)+$"
)
RELATED_DOCUMENTS = {
    "ws-protocol-notify.md": ("通知命令", "0x04-notification"),
    "ws-protocol-data.md": ("数据命令", "0x05-data"),
    "ws-protocol-measure.md": ("点测命令", "0x11-measurement"),
    "ws-protocol-settings-commands.md": ("设置命令", "0x02-settings"),
    "ws-protocol-bind.md": ("绑定命令", "0x03-bind"),
    "ws-protocol-mock.md": ("模拟数据命令", "0x12-simulator"),
    "ws-protocol-audio.md": ("音频命令", "0x13-audio"),
    "ws-protocol-log.md": ("日志命令", "0x0a-log"),
}
SHEET_DOCUMENTS = {
    "天气类型": ("天气类型", "weather-types"),
    "语音编码": ("语言编码", "language-codes"),
    "语言编码": ("语言编码", "language-codes"),
}


def inline_rst(value: str) -> str:
    value = " ".join(value.splitlines())
    value = re.sub(r"`([^`]+)`", r"``\1``", value)
    parts = re.split(r"(\*\*.*?\*\*)", value)
    value = "".join(
        part if part.startswith("**") and part.endswith("**") else part.replace("*", r"\*")
        for part in parts
    )
    if value and (PACKET.fullmatch(value) or PACKET_WITH_GAP.fullmatch(value)):
        value = f"``{value}``"
    for reference, (label, target) in RELATED_DOCUMENTS.items():
        value = value.replace(reference, f":doc:`{label} <{target}>`")
    for sheet, (label, target) in SHEET_DOCUMENTS.items():
        value = re.sub(
            rf'[“"]{sheet}[”"](?:工作表)?',
            lambda match: f":doc:`{label} <{target}>`",
            value,
        )
    return value


def heading(text: str, level: int = 1) -> str:
    char = RST_HEADING_CHARS[min(level, len(RST_HEADING_CHARS)) - 1]
    width = sum(2 if unicodedata.east_asian_width(letter) in "WF" else 1 for letter in text)
    return f"{text}\n{char * width}"


def render_text_lines(lines: list[str]) -> str:
    output = []
    previous_kind = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if output and output[-1]:
                output.append("")
            previous_kind = None
            continue
        bullet = line.startswith("·") or line.startswith("-")
        if bullet:
            line = inline_rst(line.lstrip("·-").strip())
            line = f"* {line}"
        else:
            line = inline_rst(line)
        if re.match(r"^\d+\.\s+", line):
            kind = "ordered-list"
        elif re.match(r"^(?:\*|-)\s+", line):
            kind = "unordered-list"
        else:
            kind = "text"
        if output and output[-1] and kind != previous_kind:
            output.append("")
        output.append(line)
        previous_kind = kind
    return "\n".join(output).strip()


def read_rst_doc_status(path: Path) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"\.\. container:: doc-status\s*\n\s*\n\s*\*\*(.+?)\*\*(?:　(.+))?",
        text,
    )
    if not match:
        return None
    label = match.group(1).strip()
    summary = (match.group(2) or "").strip()
    return f"{label}。{summary}" if summary else label


def command_summaries() -> list[dict]:
    summaries = []
    for filename, title, command in RST_SOURCED_DOCUMENTS:
        path = OUTPUT_DIR / filename
        summaries.append(
            {
                "filename": filename,
                "title": title,
                "command": command,
                "status": read_rst_doc_status(path),
                "source": "RST",
            }
        )
    for filename, title, command in MANUAL_DOCUMENTS:
        summaries.append(
            {
                "filename": filename,
                "title": title,
                "command": command,
                "status": None,
                "source": "手工维护",
            }
        )
    return summaries


def render_index(summaries: list[dict]) -> str:
    commands = [
        (
            item["command"],
            item["title"],
            item["filename"],
            item["status"],
            item["source"],
        )
        for item in summaries
        if item["command"] is not None
    ]
    commands.sort(key=lambda entry: int(entry[0], 16))
    rows = [
        ".. list-table:: Command 列表",
        "   :header-rows: 1",
        "   :widths: auto",
        "",
        "   * - Command ID",
        "     - 命令",
        "     - 规范状态",
        "     - 来源",
    ]
    for command, title, filename, status, source in commands:
        name = title.removeprefix(f"0x{command} ")
        rows.extend(
            [
                f"   * - ``0x{command}``",
                f"     - :doc:`{name} <{Path(filename).stem}>`",
                f"     - {(status or '未标注').split('。', 1)[0]}",
                f"     - {source}",
            ]
        )
    return "\n".join(
        [
            heading("L2 Command 详解"),
            "",
            *rows,
            "",
            ".. note::",
            "",
            "   ``0x07`` 与 ``0x0B`` 保留不用。``0x0E``\\ （视频流）与 ``0x0F``\\ （远程控制）已预留，规范待补。",
            "",
            ".. toctree::",
            "   :maxdepth: 1",
            "   :hidden:",
            "",
            *[f"   {Path(filename).stem}" for _, _, filename, _, _ in commands],
            "",
        ]
    )


def build_manifest(summaries: list[dict]) -> dict:
    return {
        "rst_sourced": [item["filename"] for item in summaries if item["source"] == "RST"],
        "appendix": [filename for filename, _ in APPENDIX_DOCUMENTS],
        "manual_commands": [item["filename"] for item in summaries if item["source"] == "手工维护"],
        "documents": summaries
        + [
            {
                "filename": filename,
                "title": title,
                "command": None,
                "status": None,
                "source": "附表",
            }
            for filename, title in APPENDIX_DOCUMENTS
        ],
    }


def build_outputs() -> tuple[dict[Path, str], dict]:
    summaries = command_summaries()
    manifest = build_manifest(summaries)
    outputs = {
        OUTPUT_DIR / "index.rst": render_index(summaries),
        MANIFEST: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    }
    return outputs, manifest


def compare(outputs: dict[Path, str]) -> list[str]:
    stale = []
    obsolete = [OUTPUT_DIR / "index.md"]
    stale.extend(str(path.relative_to(ROOT)) for path in obsolete if path.exists())
    for path, content in outputs.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(str(path.relative_to(ROOT)))
    return stale


def write(outputs: dict[Path, str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if generated index.rst or source.json are stale",
    )
    args = parser.parse_args()

    outputs, _manifest = build_outputs()
    if args.check:
        stale = compare(outputs)
        if stale:
            print("generated protocol metadata is stale:")
            for path in stale:
                print(f"  {path}")
            return 2
        print("protocol index and manifest are up to date")
    else:
        write(outputs)
        print(f"generated {len(outputs)} files under {OUTPUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
