import unittest

from openpyxl import load_workbook

from tools.sync_protocol import DOCUMENTS, MANUAL_DOCUMENTS, OUTPUT_DIR, ROOT, SOURCE, build_outputs, heading


MANUAL_COMMANDS = (
    "0x01-firmware-upgrade.rst",
    "0x06-factory-test.rst",
    "0x0c-ble-conn-param.rst",
    "0x0d-wifi-provision.rst",
    "0x10-file-transfer.rst",
)

LEGACY_PROTOCOL_MARKERS = ("旧版协议", "旧协议", "老协议", "原编号", "原来的编号", "原定")


class ProtocolRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs, cls.manifest = build_outputs()

    @classmethod
    def page(cls, name):
        return cls.outputs[OUTPUT_DIR / name]

    def test_opening_sections_are_not_dropped(self):
        for name in ("0x02-settings.rst", "0x03-bind.rst"):
            page = self.page(name)
            self.assertIn("命令格式\n--------\n", page)
            self.assertLess(page.index("命令格式\n--------"), page.index(".. list-table::"))

    def test_generated_chapters_have_one_navigation_level(self):
        for name in (
            "0x02-settings.rst",
            "0x03-bind.rst",
            "0x04-notification.rst",
            "0x05-data.rst",
            "0x0a-log.rst",
            "0x11-measurement.rst",
            "0x12-simulator.rst",
            "0x13-audio.rst",
        ):
            with self.subTest(name=name):
                page = self.page(name)
                self.assertTrue(page.startswith(":tocdepth: 2\n\n"))
                self.assertRegex(page, r"\n命令格式\n-+\n")
                self.assertRegex(page, r"\n具体命令\n-+\n")
                self.assertNotRegex(page, r"(?m)^1\.\d+ .+\n~+")
                self.assertNotRegex(page, r"(?m)^\d+\. 通用说明\n-+")
        for name in ("0x03-bind.rst", "0x04-notification.rst", "0x05-data.rst"):
            self.assertRegex(self.page(name), r"\n消息定义\n-+\n")

    def test_generated_chapters_do_not_show_source_metadata(self):
        for document in DOCUMENTS:
            with self.subTest(name=document.filename):
                page = self.page(document.filename)
                self.assertNotIn("container:: doc-meta", page)
                self.assertNotIn("工作表（自动同步）", page)

    def test_manual_key_details_are_nested_under_chapters(self):
        for name in MANUAL_COMMANDS:
            with self.subTest(name=name):
                page = (OUTPUT_DIR / name).read_text(encoding="utf-8")
                self.assertTrue(page.startswith(":tocdepth: 2\n\n"))
                self.assertRegex(page, r"\n消息定义\n-+\n")
                self.assertRegex(page, r"\n具体命令\n-+\n\n0x")
                self.assertNotRegex(page, r"(?m)^0x[\da-fA-F/]+ — .+\n-+")
        self.assertRegex((OUTPUT_DIR / "0x08-dump-stack.rst").read_text(), r"\n消息定义\n-+\n")

    def test_tocdepth_precedes_title_on_every_command_page(self):
        generated = {document.filename for document in DOCUMENTS if document.command}
        filenames = sorted(generated)
        filenames.extend(filename for filename, _, _ in MANUAL_DOCUMENTS)
        for name in filenames:
            with self.subTest(name=name):
                page = (
                    self.page(name)
                    if name in generated
                    else (OUTPUT_DIR / name).read_text(encoding="utf-8")
                )
                self.assertTrue(page.startswith(":tocdepth: 2\n\n0x"), name)

    def test_command_pages_do_not_repeat_l2_version(self):
        generated = {document.filename for document in DOCUMENTS if document.command}
        filenames = sorted(generated)
        filenames.extend(filename for filename, _, _ in MANUAL_DOCUMENTS)
        for name in filenames:
            with self.subTest(name=name):
                page = (
                    self.page(name)
                    if name in generated
                    else (OUTPUT_DIR / name).read_text(encoding="utf-8")
                )
                self.assertNotIn("L2 版本号", page)

    def test_command_field_uses_length_name(self):
        generated = {document.filename for document in DOCUMENTS if document.command}
        filenames = sorted(generated)
        filenames.extend(filename for filename, _, _ in MANUAL_DOCUMENTS)
        for name in filenames:
            with self.subTest(name=name):
                page = (
                    self.page(name)
                    if name in generated
                    else (OUTPUT_DIR / name).read_text(encoding="utf-8")
                )
                self.assertNotIn("v-length", page)
        for name in ("architecture.rst", "conventions.rst"):
            with self.subTest(name=name):
                page = (ROOT / "docs" / name).read_text(encoding="utf-8")
                self.assertNotIn("v-length", page.lower())

    def test_internal_section_references_follow_renamed_headings(self):
        data = self.page("0x05-data.rst")
        self.assertIn("筛选条件（0x01、0x03 共用）", data)
        self.assertIn(":ref:`筛选条件（0x01、0x03 共用） <cmd-05-section-1-4>`", data)
        self.assertIn("见 :ref:`具体命令 <cmd-05-section-1-9>`", data)
        bind = self.page("0x03-bind.rst")
        self.assertIn("见 :ref:`消息定义 <cmd-03-section-2>`", bind)
        self.assertNotIn('见"二、消息定义"', bind)
        settings = self.page("0x02-settings.rst")
        self.assertIn("见 :ref:`操作码 <cmd-02-section-2>`", settings)
        for name in ("0x04-notification.rst", "0x05-data.rst", "0x11-measurement.rst"):
            self.assertNotIn("见:ref:", self.page(name))

    def test_packet_examples_are_tables_even_when_source_lines_join(self):
        for name in (
            "0x02-settings.rst",
            "0x03-bind.rst",
            "0x04-notification.rst",
            "0x05-data.rst",
            "0x0a-log.rst",
            "0x11-measurement.rst",
            "0x12-simulator.rst",
            "0x13-audio.rst",
        ):
            with self.subTest(name=name):
                self.assertIn(".. list-table:: 示例：", self.page(name))
        bind = self.page("0x03-bind.rst")
        self.assertIn("   * - ``03 00``\n     - ``04``\n     - ``00 01``\n     - ``00``", bind)
        self.assertNotIn("Value03 00", bind)
        self.assertNotIn("操作数据02 00", self.page("0x02-settings.rst"))

    def test_appendices_include_headers_and_first_entries(self):
        weather = self.page("weather-types.rst")
        self.assertTrue(weather.startswith(":orphan:\n\n"))
        self.assertIn("   * - 取值\n     - 天气\n     - 英文", weather)
        self.assertIn("   * - 0x00\n     - 其他\n     - Other", weather)
        language = self.page("language-codes.rst")
        self.assertTrue(language.startswith(":orphan:\n\n"))
        self.assertIn("   * - 取值\n     - 语言\n     - 英文", language)
        self.assertIn("   * - 0x00（0）\n     - 英文\n     - English", language)

    def test_appendix_is_a_separate_chapter_with_workbook_download(self):
        root_index = (ROOT / "docs/index.rst").read_text(encoding="utf-8")
        appendix = (ROOT / "docs/appendix.rst").read_text(encoding="utf-8")
        self.assertIn("   protocol/index\n   appendix\n", root_index)
        self.assertTrue(appendix.startswith("附表\n"))
        self.assertIn(
            f":download:`协议工作簿（Excel） <assets/protocol/{SOURCE.name}>`",
            appendix,
        )
        self.assertTrue(SOURCE.is_file())
        command_index = self.page("index.rst")
        self.assertNotIn("附表", command_index)
        self.assertNotIn("   weather-types", command_index)
        self.assertNotIn("   language-codes", command_index)

    def test_chapter_and_section_numbers_are_generated_by_toctree(self):
        root_index = (ROOT / "docs/index.rst").read_text(encoding="utf-8")
        self.assertIn("   :includehidden:\n   :numbered:\n", root_index)
        for filename, title in (
            ("conventions.rst", "名词解释与约定"),
            ("architecture.rst", "协议结构介绍"),
            ("appendix.rst", "附表"),
        ):
            source = (ROOT / "docs" / filename).read_text(encoding="utf-8")
            self.assertTrue(source.startswith(f"{title}\n"), filename)
        self.assertTrue(self.page("index.rst").startswith("L2 Command 详解\n"))

    def test_intro_chapters_use_concise_unnumbered_section_titles(self):
        chapters = {
            "conventions.rst": ("名词解释", "约定", "CRC16 计算范围"),
            "architecture.rst": ("协议栈结构", "L0 接入承载", "L1 传输层", "L2 应用层"),
        }
        for filename, titles in chapters.items():
            page = (ROOT / "docs" / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                for title in titles:
                    self.assertIn(heading(title, 2), page)
                self.assertNotRegex(page, r"(?m)^[12]\.\d+(?:\.\d+)? .+\n[-~]+")
        architecture = (ROOT / "docs/architecture.rst").read_text(encoding="utf-8")
        self.assertIn(heading("BLE UART Profile", 3), architecture)
        self.assertNotIn(heading("GATT 服务 UUID", 3), architecture)
        for anchor in ("l0-uart-profile-ble", "l1-transport-layer", "l2-application-layer"):
            self.assertIn(f".. _{anchor}:", architecture)

    def test_architecture_does_not_impose_a_20_byte_mtu_limit(self):
        architecture = (ROOT / "docs/architecture.rst").read_text(encoding="utf-8")
        self.assertNotIn("ATT MTU", architecture)
        self.assertNotIn("20 字节", architecture)
        self.assertNotIn("20 bytes", architecture)
        self.assertIn("L1 通过拆包/组包支持最大 **65535 bytes** payload", architecture)

    def test_l2_payload_table_uses_compact_unit_layout(self):
        architecture = (ROOT / "docs/architecture.rst").read_text(encoding="utf-8")
        self.assertIn("L2 Payload 由连续的 Key-Value 单元组成", architecture)
        self.assertIn(".. list-table:: L2 Payload 单元结构", architecture)
        self.assertIn(":class: packet-table payload-unit-table", architecture)
        self.assertNotIn("* - Key-Value 1", architecture)

    def test_short_bitfield_tables_use_centered_cells(self):
        architecture = (ROOT / "docs/architecture.rst").read_text(encoding="utf-8")
        self.assertEqual(architecture.count(":class: packet-table bitfield-table"), 2)
        self.assertIn("   * - Command ID\n     - 8 bits\n     - 命令类型，见 Command 列表", architecture)
        self.assertIn("   * - Length\n     - 16 bits\n     - 该 key 的 value 字节数，最大 65535", architecture)

    def test_table_names_are_captions_instead_of_section_headings(self):
        architecture = (ROOT / "docs" / "architecture.rst").read_text(encoding="utf-8")
        for heading_text, caption in (
            ("L1 Header（8 bytes，Big-Endian）", ".. table:: L1 Header（8 bytes，Big-Endian）"),
            ("ACK 包格式", ".. table:: ACK 包格式"),
            ("L2 Header（16 bits，Big-Endian）", ".. list-table:: L2 Header（16 bits，Big-Endian）"),
            ("Key Header（16 bits）", ".. list-table:: Key Header（16 bits）"),
        ):
            with self.subTest(heading=heading_text):
                self.assertNotIn(heading(heading_text, 3), architecture)
                self.assertIn(caption, architecture)
        self.assertIn(".. table:: GATT 服务 UUID", architecture)

        wifi = (OUTPUT_DIR / "0x0d-wifi-provision.rst").read_text(encoding="utf-8")
        self.assertIn(".. list-table:: error 错误码\n", wifi)
        self.assertIn(".. list-table:: state 状态码\n", wifi)
        self.assertIn(".. list-table:: error 错误码（state=0x03）\n", wifi)

        data = self.page("0x05-data.rst")
        self.assertIn(".. list-table:: 筛选结果示例\n", data)
        self.assertIn(".. list-table:: 0x0C / 0x0D 设置（7B", data)
        self.assertIn(".. list-table:: 0x0B 今日数据（版本 1，24B）\n", data)

    def test_table_captions_use_centered_italic_style(self):
        stylesheet = (ROOT / "docs/_static/custom.css").read_text(encoding="utf-8")
        self.assertIn(".rst-content table.docutils > caption {", stylesheet)
        self.assertIn("text-align: center;", stylesheet)
        self.assertIn("font-style: italic;", stylesheet)

    def test_heading_hierarchy_is_visually_distinct(self):
        stylesheet = (ROOT / "docs/_static/custom.css").read_text(encoding="utf-8")
        self.assertIn(".rst-content h1 {\n  margin: 0 0 1.4rem;", stylesheet)
        self.assertIn(".rst-content h2 {\n  margin: 2.4rem 0 1.05rem;", stylesheet)
        self.assertIn("border-left: 4px solid #1f6f95;", stylesheet)
        self.assertIn("font-size: 1.48rem;", stylesheet)
        self.assertIn(".rst-content h3 {\n  margin: 1.65rem 0 0.7rem;", stylesheet)
        self.assertIn("font-size: 1.04rem;", stylesheet)

    def test_architecture_stack_uses_structured_protocol_map(self):
        architecture = (ROOT / "docs/architecture.rst").read_text(encoding="utf-8")
        self.assertIn('<figure class="protocol-stack"', architecture)
        self.assertNotIn("block-beta", architecture)
        for layer in ("L2", "L1", "L0"):
            with self.subTest(layer=layer):
                self.assertIn(f'<span class="protocol-layer__id">{layer}</span>', architecture)
        for adapter in ("ble", "uart", "socket"):
            with self.subTest(adapter=adapter):
                self.assertIn(f"protocol-adapter--{adapter}", architecture)
        for carrier in ("BLE", "UART", "SOCKET"):
            with self.subTest(carrier=carrier):
                self.assertIn(f">{carrier}</span>", architecture)

    def test_flow_diagrams_and_references_render(self):
        data = self.page("0x05-data.rst")
        self.assertIn(".. code-block:: text\n\n   手机 手表", data)
        self.assertIn(":doc:`点测命令 <0x11-measurement>`", data)
        self.assertIn(":doc:`语言编码 <language-codes>`", self.page("0x02-settings.rst"))
        for name in ("0x04-notification.rst", "0x05-data.rst", "0x11-measurement.rst"):
            self.assertNotIn("ws-protocol-", self.page(name))

    def test_protocol_docs_do_not_compare_against_legacy_protocols(self):
        document_paths = set(self.outputs) | set(OUTPUT_DIR.glob("*.rst"))
        document_paths.update(
            path
            for path in (ROOT / "docs").glob("*.rst")
            if path.name in {"architecture.rst", "conventions.rst", "index.rst"}
        )
        for path in document_paths:
            if path.suffix not in {".rst", ".json"}:
                continue
            content = path.read_text(encoding="utf-8")
            for marker in LEGACY_PROTOCOL_MARKERS:
                with self.subTest(path=str(path.relative_to(ROOT)), marker=marker):
                    self.assertNotIn(marker, content)

        workbook = load_workbook(SOURCE, read_only=True, data_only=False)
        for worksheet in workbook.worksheets:
            for row in worksheet.iter_rows():
                for cell in row:
                    if not isinstance(cell.value, str):
                        continue
                    for marker in LEGACY_PROTOCOL_MARKERS:
                        with self.subTest(sheet=worksheet.title, cell=cell.coordinate, marker=marker):
                            self.assertNotIn(marker, cell.value)

    def test_missing_source_sheets_are_disclosed(self):
        missing = self.manifest["checks"]["missing_referenced_sheets"]
        self.assertIn("数据类型", missing)
        self.assertNotIn("语言编码", missing)
        index = self.page("index.rst")
        self.assertIn(".. warning::", index)
        self.assertIn("``数据类型``", index)

    def test_admonitions_do_not_repeat_manual_titles(self):
        document_paths = set(self.outputs) | set(OUTPUT_DIR.glob("*.rst"))
        document_paths.update((ROOT / "docs").glob("*.rst"))
        for path in document_paths:
            if path.suffix != ".rst":
                continue
            content = path.read_text(encoding="utf-8")
            for line in content.splitlines():
                with self.subTest(path=str(path.relative_to(ROOT)), line=line):
                    self.assertFalse(line.startswith(".. note:: ") or line.startswith(".. warning:: "))

    def test_heading_underline_covers_wide_characters(self):
        title, underline = heading("二、消息定义", 2).splitlines()
        self.assertEqual(title, "二、消息定义")
        self.assertGreater(len(underline), len(title))

    def test_command_format_tables_use_readable_column_widths(self):
        for name in (
            "0x02-settings.rst",
            "0x03-bind.rst",
            "0x04-notification.rst",
            "0x05-data.rst",
            "0x0a-log.rst",
            "0x11-measurement.rst",
            "0x12-simulator.rst",
            "0x13-audio.rst",
        ):
            with self.subTest(name=name):
                page = self.page(name)
                self.assertIn(":widths: 18 10 18 54", page)
                self.assertIn(
                    ":class: protocol-table command-format columns-4", page
                )


if __name__ == "__main__":
    unittest.main()
