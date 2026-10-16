#!/usr/bin/env python3
"""Generate the normative protocol pages from the reviewed Excel workbook."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from openpyxl import load_workbook
from openpyxl.cell.cell import Cell


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/assets/protocol/cavo-realtek-watch-protocol.xlsx"
OUTPUT_DIR = ROOT / "docs/protocol"
MANIFEST = OUTPUT_DIR / "source.json"

HEADER_FILLS = {"FFD9E1F2", "FFBDD7EE"}
HEADER_TITLES = {
    "字段",
    "长度",
    "取值",
    "说明",
    "操作码",
    "方向",
    "操作数据",
    "Key",
    "KeyID",
    "Key 范围",
    "名称",
    "分组",
    "场景",
    "具体的命令",
    "数据说明",
    "Value",
    "编号",
    "事项",
    "想要",
    "类型",
    "index",
    "筛选条件",
    "偏移",
    "改动",
    "处理",
    "错误码",
    "状态码",
    "Data type",
}
HEX_PAIR = re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{2}(?![0-9A-Fa-f])")
PACKET = re.compile(r"^(?:[0-9A-Fa-f]{2})(?:\s+[0-9A-Fa-f]{2}){4,}$")
PACKET_WITH_GAP = re.compile(
    r"^[0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})*(?:\s+(?:…|\.\.\.)(?:\s+[0-9A-Fa-f]{2})*)+$"
)


@dataclass(frozen=True)
class Document:
    sheet: str
    filename: str
    title: str
    command: str | None = None


DOCUMENTS = (
    Document("设置模块(CMD 02)", "0x02-settings.rst", "0x02 设置命令", "02"),
    Document("绑定模块(CMD 03)", "0x03-bind.rst", "0x03 绑定命令", "03"),
    Document("通知模块(CMD 04)", "0x04-notification.rst", "0x04 通知命令", "04"),
    Document("数据模块(CMD 05)", "0x05-data.rst", "0x05 数据命令", "05"),
    Document("点测模块(CMD 11)", "0x11-measurement.rst", "0x11 点测命令", "11"),
    Document("模拟模块(CMD 12)", "0x12-simulator.rst", "0x12 模拟数据命令", "12"),
    Document("音频模块(CMD 13)", "0x13-audio.rst", "0x13 音频命令", "13"),
    Document("日志模块(CMD 0A)", "0x0a-log.rst", "0x0A 日志命令", "0A"),
    Document("天气类型", "weather-types.rst", "天气类型"),
    Document("语音编码", "language-codes.rst", "语音编码"),
)

RST_HEADING_CHARS = ("=", "-", "~", "^")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cell_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def fill_rgb(cell: Cell) -> str | None:
    fill = cell.fill
    if not fill.fill_type:
        return None
    color = fill.start_color
    if isinstance(color.rgb, str):
        return color.rgb
    return None


def is_table_header(ws, row_number: int) -> bool:
    marked = []
    nonempty = []
    for column in range(1, ws.max_column + 1):
        cell = ws.cell(row_number, column)
        if cell_text(cell.value):
            nonempty.append(cell)
            if fill_rgb(cell) in HEADER_FILLS:
                marked.append(cell)
    if len(marked) < 2 or len(nonempty) < 2:
        marked_titles = sum(cell_text(cell.value) in HEADER_TITLES for cell in nonempty)
        return marked_titles >= 2 and all(
            len(cell_text(cell.value)) <= 32 for cell in nonempty
        )
    return all(len(cell_text(cell.value)) <= 32 for cell in nonempty)


def is_blank_header_spacer(ws, row_number: int) -> bool:
    return not any(cell_text(ws.cell(row_number, column).value) for column in range(1, ws.max_column + 1)) and sum(
        fill_rgb(ws.cell(row_number, column)) in HEADER_FILLS
        for column in range(1, ws.max_column + 1)
    ) >= 2


def read_grid(ws) -> list[list[str]]:
    grid = [
        [cell_text(ws.cell(row, column).value) for column in range(1, ws.max_column + 1)]
        for row in range(1, ws.max_row + 1)
    ]
    for merged in ws.merged_cells.ranges:
        if merged.min_col != merged.max_col or merged.min_row == merged.max_row:
            continue
        value = grid[merged.min_row - 1][merged.min_col - 1]
        if not value:
            continue
        for row in range(merged.min_row + 1, merged.max_row + 1):
            grid[row - 1][merged.min_col - 1] = value
    return grid


def table_end(ws, start: int, grid: list[list[str]]) -> int:
    row = start + 1
    while row <= len(grid):
        if is_table_header(ws, row):
            break
        if is_blank_header_spacer(ws, row):
            row += 1
            continue
        if sum(bool(value) for value in grid[row - 1]) < 2:
            break
        row += 1
    return row - 1


def inline_rst(value: str) -> str:
    value = " ".join(value.splitlines())
    value = re.sub(r"`([^`]+)`", r"``\1``", value)
    parts = re.split(r"(\*\*.*?\*\*)", value)
    value = "".join(part if part.startswith("**") and part.endswith("**") else part.replace("*", r"\*") for part in parts)
    if value and (PACKET.fullmatch(value) or PACKET_WITH_GAP.fullmatch(value)):
        value = f"``{value}``"
    return value


def heading(text: str, level: int = 1) -> str:
    char = RST_HEADING_CHARS[min(level, len(RST_HEADING_CHARS)) - 1]
    return f"{text}\n{char * 120}"


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


def render_table(ws, start: int, end: int, grid: list[list[str]]) -> str:
    rows = grid[start - 1 : end]
    used_columns = [
        column
        for column in range(len(grid[0]))
        if any(row[column] for row in rows)
    ]
    output = [".. list-table::", "   :header-rows: 1", "   :widths: auto", ""]
    for row in rows:
        values = [inline_rst(row[column]) or r"\ " for column in used_columns]
        output.append(f"   * - {values[0]}")
        output.extend(f"     - {value}" for value in values[1:])
    return "\n".join(output)


def narrative_heading(text: str) -> bool:
    first_line = text.splitlines()[0].strip()
    return bool(
        re.match(
            r"^(?:[一二三四五六七八九十]+、|\d+(?:\.\d+)+\s+|\d+\.\s+|第\d+节\s+)",
            first_line,
        )
    ) and len(first_line) <= 80


def render_narrative(values: Iterable[str]) -> str:
    text = "\n".join(value for value in values if value).strip()
    if not text:
        return ""
    lines = [line.rstrip() for line in text.splitlines()]
    if lines and all(line.startswith(("·", "-")) for line in lines if line.strip()):
        return render_text_lines(lines)
    if narrative_heading(text):
        first, *rest = lines
        section_match = re.match(r"^(\d+(?:\.\d+)+)\s+(.+)$", first)
        if section_match:
            level = min(4, 2 + section_match.group(1).count("."))
            section_heading = heading(
                f"{section_match.group(1)} {section_match.group(2)}", level
            )
        else:
            section_heading = heading(re.sub(r"^\d+\.\s+", "", first), 2)
        body = render_text_lines(rest)
        return f"{section_heading}\n\n{body}".rstrip()
    return render_text_lines(lines)


def render_sheet(document: Document, ws) -> tuple[str, str | None]:
    grid = read_grid(ws)
    status = None
    if len(grid) > 1 and grid[1][0].startswith("状态："):
        status = grid[1][0].removeprefix("状态：").strip()

    blocks = []
    row = 1
    while row <= len(grid):
        if row <= 2:
            row += 1
            continue
        if not any(grid[row - 1]):
            row += 1
            continue
        if is_table_header(ws, row):
            end = table_end(ws, row, grid)
            blocks.append(render_table(ws, row, end, grid))
            row = end + 1
            continue
        values = []
        while row <= len(grid) and any(grid[row - 1]) and not is_table_header(ws, row):
            values.extend(value for value in grid[row - 1] if value)
            row += 1
        block = render_narrative(values)
        if block:
            blocks.append(block)

    header = [
        heading(document.title),
        "",
        ".. note:: 规范来源",
        "",
        f"   本页由 :download:`{SOURCE.name} <../assets/protocol/{SOURCE.name}>` 的 "
        f"``{document.sheet}`` 工作表自动生成，请勿直接编辑。",
        "",
        "   修改规范后运行 ``python tools/sync_protocol.py``，并提交同步生成的页面。",
    ]
    if status:
        header.extend(["", ".. note:: 规范状态", "", f"   {status}"])
    return "\n\n".join(header + blocks).rstrip() + "\n", status


def render_index(summaries: list[dict]) -> str:
    rows = [
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: auto",
        "",
    ]
    for item in summaries:
        status = (item["status"] or "未标注").split("。", 1)[0]
        target = Path(item["filename"]).stem
        rows.extend(
            [
                f"   * - :doc:`{item['title']} <{target}>`",
                f"     - ``{item['sheet']}``",
                f"     - {status}",
            ]
        )
    return "\n".join(
        [
            heading("协议规范（Excel 同步）"),
            "",
            ".. note:: 内容来源",
            "",
            f"   本目录由 :download:`{SOURCE.name} <../assets/protocol/{SOURCE.name}>` 自动生成。",
            "   Excel 是当前新协议的事实来源；``docs/commands/`` 保留设备端实现状态和历史差异说明。",
            "",
            heading("工作簿映射", 2),
            "",
            *rows,
            "",
            heading("同步与校验", 2),
            "",
            ".. code-block:: bash",
            "",
            "   python tools/sync_protocol.py",
            "   python tools/sync_protocol.py --check",
            "",
            "导入工具会检查完整报文的 ``v-length``、损坏的公式值、工作簿引用缺口，并生成 ``source.json`` 供 CI 校验。",
            "",
            ".. toctree::",
            "   :maxdepth: 1",
            "   :hidden:",
            "",
            *[f"   {Path(item['filename']).stem}" for item in summaries],
            "",
        ]
    )


def validate(wb) -> tuple[dict, list[str]]:
    examples = 0
    errors = []
    formulas = 0
    formula_errors = []
    missing_references: dict[str, list[str]] = {}
    sheet_names = set(wb.sheetnames)
    command_by_sheet = {
        document.sheet: document.command
        for document in DOCUMENTS
        if document.command is not None
    }

    reference_patterns = (
        re.compile(r'见\s*[“"]([^”"]+)[”"]\s*工作表'),
        re.compile(r"(ws-[A-Za-z0-9_-]+\.md)"),
    )
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if isinstance(value, str):
                    normalized = " ".join(value.split())
                    expected_command = command_by_sheet.get(ws.title)
                    if PACKET.fullmatch(normalized) and expected_command:
                        tokens = HEX_PAIR.findall(normalized)
                        if tokens[0].upper() != expected_command.upper():
                            continue
                        examples += 1
                        declared = int(tokens[3] + tokens[4], 16)
                        actual = len(tokens) - 5
                        if declared != actual:
                            errors.append(
                                f"{ws.title}!{cell.coordinate}: declared v-length {declared}, actual {actual}"
                            )
                    for pattern in reference_patterns:
                        for reference in pattern.findall(value):
                            if reference.endswith(".md") or reference in sheet_names:
                                continue
                            missing_references.setdefault(reference, []).append(
                                f"{ws.title}!{cell.coordinate}"
                            )
                    if value.startswith("="):
                        formulas += 1
                    if any(marker in value for marker in ("#REF!", "#DIV/0!", "#VALUE!", "#N/A", "#NAME?")):
                        formula_errors.append(f"{ws.title}!{cell.coordinate}")

    report = {
        "complete_command_examples": examples,
        "formula_count": formulas,
        "formula_errors": formula_errors,
        "missing_referenced_sheets": missing_references,
    }
    return report, errors


def build_outputs() -> tuple[dict[Path, str], dict]:
    if not SOURCE.exists():
        raise FileNotFoundError(f"source workbook not found: {SOURCE}")
    wb = load_workbook(SOURCE, data_only=False)
    missing_sheets = [document.sheet for document in DOCUMENTS if document.sheet not in wb.sheetnames]
    if missing_sheets:
        raise ValueError(f"mapped sheets not found: {', '.join(missing_sheets)}")

    outputs: dict[Path, str] = {}
    summaries = []
    for document in DOCUMENTS:
        content, status = render_sheet(document, wb[document.sheet])
        path = OUTPUT_DIR / document.filename
        outputs[path] = content
        summaries.append(
            {
                "sheet": document.sheet,
                "filename": document.filename,
                "title": document.title,
                "command": document.command,
                "status": status,
                "rows": wb[document.sheet].max_row,
            }
        )
    outputs[OUTPUT_DIR / "index.rst"] = render_index(summaries)
    report, errors = validate(wb)
    manifest = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "documents": summaries,
        "checks": {
            **report,
            "vlength_errors": errors,
        },
    }
    outputs[MANIFEST] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if errors:
        raise ValueError("; ".join(errors))
    return outputs, manifest


def compare(outputs: dict[Path, str]) -> list[str]:
    stale = []
    obsolete = [OUTPUT_DIR / "index.md"] + [
        OUTPUT_DIR / Path(document.filename).with_suffix(".md").name
        for document in DOCUMENTS
    ]
    stale.extend(
        str(path.relative_to(ROOT)) for path in obsolete if path.exists()
    )
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
    parser.add_argument("--check", action="store_true", help="fail if generated pages are stale")
    args = parser.parse_args()

    outputs, manifest = build_outputs()
    if args.check:
        stale = compare(outputs)
        if stale:
            print("generated protocol pages are stale:")
            for path in stale:
                print(f"  {path}")
            return 2
        print("protocol pages are up to date")
    else:
        write(outputs)
        print(f"generated {len(outputs)} protocol files from {SOURCE.relative_to(ROOT)}")

    checks = manifest["checks"]
    print(
        f"checked {checks['complete_command_examples']} complete command examples; "
        f"v-length errors: {len(checks['vlength_errors'])}"
    )
    missing = checks["missing_referenced_sheets"]
    if missing:
        print("warning: workbook references sheets not included in the source:")
        for name, locations in sorted(missing.items()):
            print(f"  {name}: {', '.join(locations[:6])}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
