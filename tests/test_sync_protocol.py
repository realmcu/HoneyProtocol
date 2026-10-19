import unittest

from tools.sync_protocol import DOCUMENTS, MANUAL_DOCUMENTS, OUTPUT_DIR, ROOT, SOURCE, build_outputs, heading


MANUAL_COMMANDS = (
    "0x01-firmware-upgrade.rst",
    "0x06-factory-test.rst",
    "0x0c-ble-conn-param.rst",
    "0x0d-wifi-provision.rst",
    "0x10-file-transfer.rst",
)


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
        self.assertTrue(appendix.startswith("4 附表\n"))
        self.assertIn(
            f":download:`协议工作簿（Excel） <assets/protocol/{SOURCE.name}>`",
            appendix,
        )
        self.assertTrue(SOURCE.is_file())
        command_index = self.page("index.rst")
        self.assertNotIn("附表", command_index)
        self.assertNotIn("   weather-types", command_index)
        self.assertNotIn("   language-codes", command_index)

    def test_flow_diagrams_and_references_render(self):
        data = self.page("0x05-data.rst")
        self.assertIn(".. code-block:: text\n\n   手机 手表", data)
        self.assertIn(":doc:`点测命令 <0x11-measurement>`", data)
        self.assertIn(":doc:`语言编码 <language-codes>`", self.page("0x02-settings.rst"))
        for name in ("0x04-notification.rst", "0x05-data.rst", "0x11-measurement.rst"):
            self.assertNotIn("ws-protocol-", self.page(name))
        self.assertIn("旧版协议差异\n", self.page("0x03-bind.rst"))
        self.assertIn("以下差异待对照原文复核", self.page("0x03-bind.rst"))

    def test_missing_source_sheets_are_disclosed(self):
        missing = self.manifest["checks"]["missing_referenced_sheets"]
        self.assertIn("数据类型", missing)
        self.assertNotIn("语言编码", missing)
        index = self.page("index.rst")
        self.assertIn("工作簿引用缺口", index)
        self.assertIn("``数据类型``", index)

    def test_heading_underline_covers_wide_characters(self):
        title, underline = heading("二、消息定义", 2).splitlines()
        self.assertEqual(title, "二、消息定义")
        self.assertGreater(len(underline), len(title))


if __name__ == "__main__":
    unittest.main()
