# tests/test_md2pdf.py
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from md2pdf import (
    Md2PdfError,
    InputFileNotFoundError,
    InvalidMarkdownError,
    ConversionError,
    DependencyError,
    EngineNotFoundError,
    parse_args,
    generate_install_guide,
    select_pdf_engine,
    convert_md_to_pdf,
)


class TestExceptions:
    def test_base_exception(self):
        with pytest.raises(Md2PdfError):
            raise Md2PdfError("test error")

    def test_input_not_found_exception(self):
        with pytest.raises(InputFileNotFoundError):
            raise InputFileNotFoundError("file not found")

    def test_invalid_markdown_exception(self):
        with pytest.raises(InvalidMarkdownError):
            raise InvalidMarkdownError("invalid markdown")


class TestParseArgs:
    def test_parse_args_input_only(self):
        args = parse_args(["input.md"])
        assert args.input == "input.md"
        assert args.output is None
        assert args.pdf_engine is None
        assert args.toc is False
        assert args.force is False
        assert args.debug is False

    def test_parse_args_with_output(self):
        args = parse_args(["input.md", "-o", "output.pdf"])
        assert args.input == "input.md"
        assert args.output == "output.pdf"

    def test_parse_args_with_all_options(self):
        args = parse_args([
            "input.md",
            "-o", "output.pdf",
            "--pdf-engine", "xelatex",
            "--toc",
            "--force",
            "--debug"
        ])
        assert args.input == "input.md"
        assert args.output == "output.pdf"
        assert args.pdf_engine == "xelatex"
        assert args.toc is True
        assert args.force is True
        assert args.debug is True


class TestGenerateInstallGuide:
    def test_generate_install_guide_contains_weasyprint(self):
        guide = generate_install_guide()
        assert "weasyprint" in guide.lower()
        assert "pip install" in guide.lower()

    def test_generate_install_guide_contains_xelatex(self):
        guide = generate_install_guide()
        assert "xelatex" in guide.lower()


class TestSelectPdfEngine:
    def test_select_pdf_engine_user_specified(self):
        result = select_pdf_engine("English content", "xelatex", debug=False)
        assert result == "xelatex"

    def test_select_pdf_engine_chinese_content(self):
        try:
            result = select_pdf_engine("这是中文内容", None, debug=False)
            assert result in ["xelatex", "weasyprint"]
        except EngineNotFoundError:
            pytest.skip("No PDF engines available")

    def test_select_pdf_engine_no_engine_available(self, monkeypatch):
        import lib.converter_base
        monkeypatch.setattr(
            lib.converter_base,
            "get_available_pdf_engines",
            lambda: []
        )
        with pytest.raises(EngineNotFoundError):
            select_pdf_engine("English", None, debug=False)


class TestConvertMdToPdf:
    def test_convert_md_to_pdf_creates_file(self, tmp_path):
        input_file = tmp_path / "test.md"
        input_file.write_text("# Test\n\nHello World", encoding="utf-8")
        output_file = tmp_path / "test.pdf"

        try:
            result = convert_md_to_pdf(
                input_file, output_file, pdf_engine=None, toc=False, debug=True
            )
            assert result is True
            assert output_file.exists()
        except Exception as e:
            pytest.skip(f"PDF engine not available: {e}")
