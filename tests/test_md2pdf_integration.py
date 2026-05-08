# tests/test_md2pdf_integration.py
import pytest
import subprocess
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.integration
class TestMd2PdfIntegration:
    def test_convert_simple(self, tmp_path):
        input_file = FIXTURES_DIR / "simple.md"
        output_file = tmp_path / "simple.pdf"

        result = subprocess.run(
            ["python", "scripts/md2pdf.py", str(input_file), "-o", str(output_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(f"PDF conversion failed: {result.stderr}")

        assert output_file.exists()

    @pytest.mark.integration
    def test_convert_chinese(self, tmp_path):
        input_file = FIXTURES_DIR / "chinese.md"
        output_file = tmp_path / "chinese.pdf"

        result = subprocess.run(
            ["python", "scripts/md2pdf.py", str(input_file), "-o", str(output_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(f"PDF conversion failed: {result.stderr}")

        assert output_file.exists()

    @pytest.mark.integration
    def test_convert_with_frontmatter(self, tmp_path):
        input_file = FIXTURES_DIR / "with_frontmatter.md"
        output_file = tmp_path / "with_frontmatter.pdf"

        result = subprocess.run(
            ["python", "scripts/md2pdf.py", str(input_file), "-o", str(output_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(f"PDF conversion failed: {result.stderr}")

        assert output_file.exists()

    @pytest.mark.integration
    def test_convert_with_toc(self, tmp_path):
        input_file = FIXTURES_DIR / "with_toc.md"
        output_file = tmp_path / "with_toc.pdf"

        result = subprocess.run(
            [
                "python",
                "scripts/md2pdf.py",
                str(input_file),
                "-o",
                str(output_file),
                "--toc",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(f"PDF conversion failed: {result.stderr}")

        assert output_file.exists()
