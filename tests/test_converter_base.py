# tests/test_converter_base.py
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.converter_base import (
    validate_input,
    resolve_output,
    find_pandoc,
    detect_chinese,
    parse_frontmatter,
    get_available_pdf_engines,
    get_chinese_font,
)


class TestValidateInput:
    def test_validate_input_valid(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test", encoding="utf-8")
        result = validate_input(str(md_file), (".md", ".markdown"))
        assert result == md_file

    def test_validate_input_not_found(self):
        with pytest.raises(FileNotFoundError):
            validate_input("nonexistent.md", (".md", ".markdown"))

    def test_validate_input_invalid_ext(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test", encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid file extension"):
            validate_input(str(txt_file), (".md", ".markdown"))


class TestResolveOutput:
    def test_resolve_output_default(self, tmp_path):
        input_path = tmp_path / "test.md"
        input_path.write_text("# Test", encoding="utf-8")
        result = resolve_output(input_path, None, False, ".pdf")
        assert result == tmp_path / "test.pdf"

    def test_resolve_output_custom(self, tmp_path):
        input_path = tmp_path / "test.md"
        input_path.write_text("# Test", encoding="utf-8")
        custom_output = tmp_path / "output" / "custom.pdf"
        result = resolve_output(input_path, str(custom_output), False, ".pdf")
        assert result == custom_output

    def test_resolve_output_exists_no_force(self, tmp_path):
        input_path = tmp_path / "test.md"
        input_path.write_text("# Test", encoding="utf-8")
        output_path = tmp_path / "test.pdf"
        output_path.write_text("existing", encoding="utf-8")
        with pytest.raises(FileExistsError):
            resolve_output(input_path, None, False, ".pdf")

    def test_resolve_output_exists_with_force(self, tmp_path):
        input_path = tmp_path / "test.md"
        input_path.write_text("# Test", encoding="utf-8")
        output_path = tmp_path / "test.pdf"
        output_path.write_text("existing", encoding="utf-8")
        result = resolve_output(input_path, None, True, ".pdf")
        assert result == output_path


class TestFindPandoc:
    def test_find_pandoc_returns_string_or_none(self):
        result = find_pandoc()
        assert result is None or isinstance(result, str)


class TestDetectChinese:
    def test_detect_chinese_true(self):
        assert detect_chinese("这是中文") is True
        assert detect_chinese("Hello 世界") is True

    def test_detect_chinese_false(self):
        assert detect_chinese("Hello World") is False
        assert detect_chinese("123456") is False


class TestParseFrontmatter:
    def test_parse_frontmatter_valid(self):
        content = "---\ntitle: Test Title\nauthor: Test Author\n---\n\n# Content"
        result = parse_frontmatter(content)
        assert result == {"title": "Test Title", "author": "Test Author"}

    def test_parse_frontmatter_empty(self):
        content = "# No frontmatter"
        result = parse_frontmatter(content)
        assert result == {}

    def test_parse_frontmatter_partial(self):
        content = "---\ntitle: Only Title\n---\n\n# Content"
        result = parse_frontmatter(content)
        assert result == {"title": "Only Title"}


class TestGetAvailablePdfEngines:
    def test_get_available_pdf_engines_returns_list(self):
        result = get_available_pdf_engines()
        assert isinstance(result, list)


class TestGetChineseFont:
    def test_get_chinese_font_returns_string_or_none(self):
        result = get_chinese_font()
        assert result is None or isinstance(result, str)
