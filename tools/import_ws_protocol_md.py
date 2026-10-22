#!/usr/bin/env python3
"""Import HoneyBox ws-protocol-*.md into docs/protocol/*.rst (L2 command pages)."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HONEYBOX_DOCS = ROOT.parent / "HoneyBox" / "docs"
OUTPUT_DIR = ROOT / "docs" / "protocol"

sys.path.insert(0, str(ROOT / "tools"))
from sync_protocol import inline_rst, heading  # noqa: E402

RST_HEADING_CHARS = ("=", "-", "~", "^", '"')

HEX_CMD = re.compile(r"^([0-9A-Fa-f]{2})\s+([0-9A-Fa-f]{2})")


@dataclass(frozen=True)
class PageSpec:
    md: str
    rst: str
    title: str
    command: str
    status: str
    status_note: str = ""


PAGES = (
    PageSpec(
        "ws-protocol-data.md",
        "0x05-data.rst",
        "0x05 数据命令",
        "05",
        "第一版本",
        "历史数据（含运动结束后的运动记录）与今日数据；即时测量见 :doc:`点测命令 <0x11-measurement>`。",
    ),
    PageSpec(
        "ws-protocol-settings-commands.md",
        "0x02-settings.rst",
        "0x02 设置命令",
        "02",
        "第一版本",
        "各 Key 的操作码、规则与具体命令示例。",
    ),
    PageSpec(
        "ws-protocol-bind.md",
        "0x03-bind.rst",
        "0x03 绑定命令",
        "03",
        "第一版本",
        "登录、绑定与解绑。",
    ),
    PageSpec(
        "ws-protocol-notify.md",
        "0x04-notification.rst",
        "0x04 通知命令",
        "04",
        "第一版本",
        "来电、消息、音乐、查找、拍照、电量等实时通知。",
    ),
    PageSpec(
        "ws-protocol-measure.md",
        "0x11-measurement.rst",
        "0x11 点测命令",
        "11",
        "第一版本",
        "即时点测、运动过程与心电预留；历史/今日见 :doc:`数据命令 <0x05-data>`。",
    ),
    PageSpec(
        "ws-protocol-mock.md",
        "0x12-simulator.rst",
        "0x12 模拟数据命令",
        "12",
        "第一版本",
        "调试用历史数据生成与清除，结果走 :doc:`数据命令 <0x05-data>` 同步。",
    ),
    PageSpec(
        "ws-protocol-audio.md",
        "0x13-audio.rst",
        "0x13 音频命令",
        "13",
        "第一版本",
        "经典蓝牙音频状态与配对控制。",
    ),
    PageSpec(
        "ws-protocol-log.md",
        "0x0a-log.rst",
        "0x0A 日志命令",
        "0A",
        "第一版本",
        "联调实时日志；崩溃栈见 :doc:`Dump Stack 命令 <0x08-dump-stack>`。",
    ),
)


def slug_command(command: str) -> str:
    return command.lower().lstrip("0") or "0"


def parse_sections(text: str) -> tuple[str, dict[str, str]]:
    title_match = re.match(r"^#\s+(.+)$", text.strip().splitlines()[0])
    title = title_match.group(1).strip() if title_match else ""
    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in text.splitlines()[1:]:
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
            continue
        buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return title, sections


def parse_subsections(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    current = "_preamble"
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^###\s+(.+)$", line)
        if m:
            out[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
            continue
        buf.append(line)
    out[current] = "\n".join(buf).strip()
    return out


def parse_md_table(block: str) -> list[list[str]] | None:
    rows: list[list[str]] = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if rows:
                break
            continue
        if re.match(r"^\|\s*---", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows if len(rows) >= 2 else None


def split_table_and_text(block: str) -> tuple[str, list[list[str]] | None]:
    lines = block.splitlines()
    table_lines: list[str] = []
    text_lines: list[str] = []
    in_table = False
    for line in lines:
        if line.strip().startswith("|"):
            in_table = True
            table_lines.append(line)
        elif in_table and not line.strip():
            in_table = False
            text_lines.append(line)
        elif not in_table:
            text_lines.append(line)
    table = parse_md_table("\n".join(table_lines)) if table_lines else None
    return "\n".join(text_lines).strip(), table


def render_bullets(block: str) -> str:
    from sync_protocol import render_text_lines

    return render_text_lines(block.splitlines())


def is_l2_format_table(headers: list[str]) -> bool:
    return headers[:3] == ["字段", "长度", "说明"] or headers == ["字段", "长度", "取值", "说明"]


def is_command_detail_table(headers: list[str]) -> bool:
    if headers[:2] in (["Key", "名称"], ["KeyID", "功能名称"]):
        return "具体的命令" in headers
    return False


def render_list_table(
    rows: list[list[str]],
    extra_classes: list[str] | None = None,
    widths: str | None = None,
) -> str:
    headers = rows[0]
    classes = ["protocol-table", f"columns-{len(headers)}"]
    if extra_classes:
        classes.extend(extra_classes)
    if is_l2_format_table(headers):
        classes.insert(1, "command-format")
        widths = widths or "18 10 18 54"
    elif is_command_detail_table(headers):
        classes.insert(1, "command-detail")
        widths = widths or "5 8 16 9 14 48"
    lines = [
        ".. list-table::",
        "   :header-rows: 1",
        f"   :widths: {widths or 'auto'}",
        f"   :class: {' '.join(classes)}",
        "",
    ]
    for row in rows:
        padded = row + [""] * (len(headers) - len(row))
        cells = [inline_rst(cell) for cell in padded[: len(headers)]]
        lines.append("   * - " + "\n     - ".join(cells))
    return "\n".join(lines)


def l2_header_from_table(table: list[list[str]]) -> tuple[str, str] | None:
    for row in table:
        if len(row) >= 3 and row[0] == "Header":
            hex_part = row[2].strip().split()[0]
            if HEX_CMD.match(hex_part.replace("`", "")):
                return hex_part.replace("`", "").split()[0], row[2]
    return None


def render_command_format(sub: dict[str, str], cmd_slug: str) -> str:
    l2 = sub.get("1.1 L2 帧（不含 L1）", sub.get("1.1 L2 帧", ""))
    text, table = split_table_and_text(l2)
    parts = [
        f".. _cmd-{cmd_slug}-section-1:",
        "",
        heading("命令格式", 2),
        "",
        "以下为 L2 层命令格式，不含 L1 帧头。",
        "",
    ]
    if table:
        # Normalize to 4-column workbook style for CSS
        norm_rows = [["字段", "长度", "取值", "说明"]]
        hdr = table[0]
        for row in table[1:]:
            if len(row) >= 3:
                field, length, desc = row[0], row[1], row[2]
                value = ""
                if "Header" in field or field == "Header":
                    m = re.search(r"`([^`]+)`", desc)
                    value = m.group(1).split("=")[0].strip() if m else desc.split("=")[0].strip()
                norm_rows.append([field, length, value or "—", desc])
        parts.append(render_list_table(norm_rows))
        parts.append("")
    if text:
        parts.append(render_bullets(text))
        parts.append("")
    return "\n".join(parts)


def render_rules_block(sub: dict[str, str], cmd_slug: str, section_index: int = 2) -> str:
    rules_key = next((k for k in sub if k.endswith("规则") or k == "1.2 规则"), None)
    opcode_key = next((k for k in sub if "操作码" in k), None)
    parts = []
    if opcode_key:
        parts.extend(
            [
                f".. _cmd-{cmd_slug}-section-{section_index}:",
                "",
                heading("操作码", 2),
                "",
            ]
        )
        text, table = split_table_and_text(sub[opcode_key])
        if table:
            parts.append(render_list_table(table))
            parts.append("")
        if text:
            parts.append(render_bullets(text))
            parts.append("")
        section_index += 1

    if rules_key:
        parts.extend(
            [
                f".. _cmd-{cmd_slug}-section-{section_index}:",
                "",
                heading("规则", 2),
                "",
            ]
        )
        body = sub[rules_key]
        # Key layout table inside rules (notify, measure)
        text, table = split_table_and_text(body)
        if table and not is_command_detail_table(table[0]):
            parts.append(render_list_table(table, extra_classes=["key-interaction"]))
            parts.append("")
        if text:
            parts.append(render_bullets(text))
            parts.append("")
        section_index += 1
    return "\n".join(parts), section_index


def render_section_table(
    section_body: str,
    cmd_slug: str,
    section_num: int,
    section_title: str,
) -> str:
    text, table = split_table_and_text(section_body)
    parts = [
        f".. _cmd-{cmd_slug}-section-{section_num}:",
        "",
        heading(section_title, 2),
        "",
    ]
    if text and not table:
        parts.append(render_bullets(text))
        parts.append("")
    if table:
        parts.append(render_list_table(table))
        parts.append("")
    if text and table:
        parts.append(render_bullets(text))
        parts.append("")
    return "\n".join(parts)


def convert_page(spec: PageSpec) -> str:
    md_path = HONEYBOX_DOCS / spec.md
    if not md_path.exists():
        raise FileNotFoundError(md_path)
    text = md_path.read_text(encoding="utf-8")
    _, sections = parse_sections(text)
    overview = sections.get("1. 概览", "")
    subs = parse_subsections(overview)
    cmd_slug = slug_command(spec.command)

    out: list[str] = [
        ":tocdepth: 2",
        "",
        heading(spec.title, 1),
        "",
        ".. container:: doc-status",
        "",
        f"   **{spec.status}**　{spec.status_note}",
        "",
    ]

    out.append(render_command_format(subs, cmd_slug))

    next_sec = 2
    rules_rst, next_sec = render_rules_block(subs, cmd_slug, section_index=next_sec)
    out.append(rules_rst)

    for key, body in subs.items():
        if key.startswith("_") or key.startswith("1.1"):
            continue
        if "规则" in key or "操作码" in key:
            continue
        if "生成参数" in key:
            out.append(render_section_table(body, cmd_slug, next_sec, "生成参数（Key 0x01）"))
            next_sec += 1

    for sec_title, sec_body in sections.items():
        if sec_title.startswith("1."):
            continue
        m = re.match(r"^(\d+)\.\s+(.+)$", sec_title)
        if not m or int(m.group(1)) < 2:
            continue
        title = m.group(2).strip()
        out.append(render_section_table(sec_body, cmd_slug, next_sec, title))
        next_sec += 1

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    stale: list[str] = []
    for spec in PAGES:
        content = convert_page(spec)
        path = OUTPUT_DIR / spec.rst
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")

    if args.check:
        if stale:
            print("HoneyBox MD import is stale:")
            for item in stale:
                print(f"  {item}")
            return 2
        print("HoneyBox MD import is up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
