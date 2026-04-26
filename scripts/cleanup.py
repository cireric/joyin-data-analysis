#!/usr/bin/env python3
"""
清理项目无用文件
- 清除 Python 缓存 (__pycache__, *.pyc)
- 清除输出报表 (output/ 目录)
- 可选保留最近N天的报表
"""

import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass


def _delete_item(item: Path, dry_run: bool) -> tuple:
    """
    删除单个文件或目录
    
    Args:
        item: 文件或目录路径
        dry_run: 是否仅预览
        
    Returns:
        (是否成功, 错误消息或None)
    """
    try:
        if item.is_dir():
            if not dry_run:
                shutil.rmtree(item)
        else:
            if not dry_run:
                item.unlink()
        return True, None
    except PermissionError:
        return False, f"权限不足: {item}"
    except Exception as e:
        return False, f"删除失败: {item} ({e})"


def _should_keep_output_dir(dir_name: str, keep_recent_days: int) -> bool:
    """
    判断输出目录是否应该保留
    
    Args:
        dir_name: 目录名（格式：YYYYMMDD）
        keep_recent_days: 保留天数
        
    Returns:
        是否保留
    """
    if keep_recent_days <= 0:
        return False
    
    try:
        dir_date = datetime.strptime(dir_name, "%Y%m%d")
        cutoff_date = datetime.now() - timedelta(days=keep_recent_days)
        return dir_date >= cutoff_date
    except ValueError:
        return False


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
    skipped = []

    print(f"项目根目录: {project_root}")
    print(f"保留最近 {keep_recent_days} 天的报表")
    print(f"模式: {'预览' if dry_run else '执行删除'}")
    print("-" * 50)

    for pycache in project_root.rglob("__pycache__"):
        if ".venv" not in str(pycache):
            success, error = _delete_item(pycache, dry_run)
            if success:
                deleted.append(str(pycache))
            elif error:
                skipped.append(error)

    for pyc in project_root.rglob("*.pyc"):
        if ".venv" not in str(pyc):
            success, error = _delete_item(pyc, dry_run)
            if success:
                deleted.append(str(pyc))
            elif error:
                skipped.append(error)

    output_dir = project_root / "output"
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir() and _should_keep_output_dir(item.name, keep_recent_days):
                kept.append(str(item))
                continue
            
            success, error = _delete_item(item, dry_run)
            if success:
                deleted.append(str(item))
            elif error:
                skipped.append(error)

    print(f"\n已删除 ({len(deleted)} 项):")
    for item in deleted:
        print(f"  - {item}")

    if kept:
        print(f"\n已保留 ({len(kept)} 项):")
        for item in kept:
            print(f"  - {item}")

    if skipped:
        print(f"\n已跳过 ({len(skipped)} 项):")
        for item in skipped:
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