# scripts/lib/converter_base.py
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional, Tuple


PDF_ENGINE_PRIORITY = ["weasyprint", "xelatex", "wkhtmltopdf", "pdflatex"]


def validate_input(input_path: str, allowed_extensions: Tuple[str, ...]) -> Path:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    if path.suffix.lower() not in allowed_extensions:
        raise ValueError(
            f"Invalid file extension: expected {allowed_extensions}, got {path.suffix}"
        )
    return path


def resolve_output(
    input_path: Path, output_arg: Optional[str], force: bool, default_suffix: str
) -> Path:
    if output_arg:
        output_path = Path(output_arg)
    else:
        output_path = input_path.with_suffix(default_suffix)

    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {output_path}\n"
            f"Use --force to overwrite."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def find_pandoc() -> Optional[str]:
    pandoc_path = shutil.which("pandoc")
    if pandoc_path:
        return pandoc_path

    candidates = [
        os.path.expandvars(r"%LOCALAPPDATA%\Pandoc\pandoc.exe"),
        os.path.expandvars(r"%ProgramFiles%\Pandoc\pandoc.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Pandoc\pandoc.exe"),
        os.path.expandvars(
            r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe\pandoc-3.9.0.2\pandoc.exe"
        ),
    ]

    for path in candidates:
        if path and os.path.isfile(path):
            return path

    wg_base = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    if os.path.isdir(wg_base):
        for root, _, files in os.walk(wg_base):
            if "pandoc.exe" in files:
                return os.path.join(root, "pandoc.exe")

    return None


def detect_chinese(text: str) -> bool:
    chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
    return bool(chinese_pattern.search(text))


def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}

    try:
        end_idx = content.index("---", 3)
        frontmatter_text = content[3:end_idx].strip()

        result = {}
        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result
    except (ValueError, IndexError):
        return {}


def get_available_pdf_engines() -> list:
    available = []
    for engine in PDF_ENGINE_PRIORITY:
        if engine == "weasyprint":
            try:
                import weasyprint

                available.append(engine)
            except ImportError:
                pass
        elif engine in ("xelatex", "pdflatex"):
            if shutil.which(engine):
                available.append(engine)
        elif engine == "wkhtmltopdf":
            if shutil.which("wkhtmltopdf"):
                available.append(engine)
    return available


def get_chinese_font() -> Optional[str]:
    chinese_fonts = ["SimSun", "Microsoft YaHei", "FangSong", "KaiTi", "SimHei"]

    if sys.platform == "win32":
        import winreg

        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
            )
            installed_fonts = []
            for i in range(winreg.QueryInfoKey(key)[1]):
                name, _ = winreg.EnumValue(key, i)
                installed_fonts.append(name)
            winreg.CloseKey(key)

            for font in chinese_fonts:
                for installed in installed_fonts:
                    if font in installed:
                        return font
        except Exception:
            pass

    return chinese_fonts[0] if chinese_fonts else None
