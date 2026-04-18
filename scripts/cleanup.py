#!/usr/bin/env python3
"""
清理项目无用文件
- 清除 Python 缓存 (__pycache__, *.pyc)
- 清除输出报表 (output/ 目录)
- 可选保留最近N天的报表
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')


def clean_project(keep_recent_days: int = 0, dry_run: bool = False):
    """
    清理项目无用文件

    Args:
        keep_recent_days: 保留最近N天的报表 (0=全部删除)
        dry_run: 仅显示将删除的文件，不实际删除
    """
    project_root = Path(__file__).parent.parent
    deleted = []
    kept = []

    print(f"项目根目录: {project_root}")
    print(f"保留最近 {keep_recent_days} 天的报表")
    print(f"模式: {'预览' if dry_run else '执行删除'}")
    print("-" * 50)

    for pycache in project_root.rglob("__pycache__"):
        if ".venv" not in str(pycache):
            try:
                if not dry_run:
                    shutil.rmtree(pycache)
                deleted.append(str(pycache))
            except PermissionError:
                pass

    for pyc in project_root.rglob("*.pyc"):
        if ".venv" not in str(pyc):
            try:
                if not dry_run:
                    pyc.unlink()
                deleted.append(str(pyc))
            except PermissionError:
                pass

    output_dir = project_root / "output"
    if output_dir.exists():
        if keep_recent_days > 0:
            cutoff_date = datetime.now() - timedelta(days=keep_recent_days)
            for item in output_dir.iterdir():
                if item.is_dir():
                    try:
                        dir_date = datetime.strptime(item.name, "%Y%m%d")
                        if dir_date < cutoff_date:
                            if not dry_run:
                                shutil.rmtree(item)
                            deleted.append(str(item))
                        else:
                            kept.append(str(item))
                    except (ValueError, PermissionError):
                        pass
                else:
                    try:
                        if not dry_run:
                            item.unlink()
                        deleted.append(str(item))
                    except PermissionError:
                        print(f"  跳过 (文件被占用): {item}")
        else:
            for item in output_dir.iterdir():
                if item.is_dir():
                    try:
                        if not dry_run:
                            shutil.rmtree(item)
                        deleted.append(str(item))
                    except PermissionError:
                        print(f"  跳过 (文件被占用): {item}")
                else:
                    try:
                        if not dry_run:
                            item.unlink()
                        deleted.append(str(item))
                    except PermissionError:
                        print(f"  跳过 (文件被占用): {item}")

    print(f"\n已删除 ({len(deleted)} 项):")
    for item in deleted:
        print(f"  - {item}")

    if kept:
        print(f"\n已保留 ({len(kept)} 项):")
        for item in kept:
            print(f"  - {item}")

    print(f"\n{'预览完成，未实际删除' if dry_run else '清理完成'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="清理项目无用文件")
    parser.add_argument(
        "--keep-days",
        type=int,
        default=0,
        help="保留最近N天的报表 (默认: 0=全部删除)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览，不实际删除",
    )

    args = parser.parse_args()
    clean_project(keep_recent_days=args.keep_days, dry_run=args.dry_run)
