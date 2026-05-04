"""
Maintenance Data Module

Handles loading and processing maintenance records.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional

from .matcher import extract_machine_code, get_matched_codes, get_unmatched_records


def load_maintenance_data(file_path: str) -> pd.DataFrame:
    """
    Load maintenance records from Excel file.

    Args:
        file_path: Path to maintenance Excel file

    Returns:
        DataFrame with maintenance records
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Maintenance file not found: {file_path}")

    df = pd.read_excel(path)
    return df


def count_maintenance_by_point(
    maintenance_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    site_col: str = '站点名称',
    code_col: str = '机器编号',
    name_col: str = '点位名称'
) -> Dict[str, int]:
    """
    Count maintenance visits per point.

    Args:
        maintenance_df: DataFrame with maintenance records
        sales_df: DataFrame with sales data
        site_col: Column name for site name in maintenance_df
        code_col: Column name for machine code in sales_df
        name_col: Column name for point name in sales_df

    Returns:
        Dict mapping point name to maintenance count: {'江门戴爱莲': 2}
    """
    sales_code_to_name = {}
    for _, row in sales_df.iterrows():
        code = row.get(code_col)
        name = row.get(name_col)
        if pd.notna(code) and pd.notna(name):
            sales_code_to_name[str(int(code))] = name

    counts: Dict[str, int] = {}
    for _, row in maintenance_df.iterrows():
        site_name = row.get(site_col)
        code = extract_machine_code(site_name)
        if code and code in sales_code_to_name:
            point_name = sales_code_to_name[code]
            counts[point_name] = counts.get(point_name, 0) + 1

    return counts


def generate_unmatched_sheet(
    maintenance_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    site_col: str = '站点名称',
    code_col: str = '机器编号'
) -> Optional[pd.DataFrame]:
    """
    Generate sheet for unmatched maintenance records.

    Args:
        maintenance_df: DataFrame with maintenance records
        sales_df: DataFrame with sales data
        site_col: Column name for site name in maintenance_df
        code_col: Column name for machine code in sales_df

    Returns:
        DataFrame with unmatched records, or None if all matched
    """
    matched_codes = get_matched_codes(maintenance_df, sales_df, site_col, code_col)
    unmatched = get_unmatched_records(maintenance_df, matched_codes, site_col)

    if unmatched.empty:
        return None

    result = unmatched.copy()
    result['提取机器码'] = result[site_col].apply(extract_machine_code)

    return result


def process_maintenance_data(
    maintenance_file: str,
    sales_df: pd.DataFrame,
    site_col: str = '站点名称',
    code_col: str = '机器编号',
    name_col: str = '点位名称'
) -> tuple:
    """
    Process maintenance data and return counts and unmatched records.

    Args:
        maintenance_file: Path to maintenance Excel file
        sales_df: DataFrame with sales data
        site_col: Column name for site name in maintenance file
        code_col: Column name for machine code in sales_df
        name_col: Column name for point name in sales_df

    Returns:
        Tuple of (maintenance_counts, unmatched_df)
        - maintenance_counts: Dict mapping point name to count
        - unmatched_df: DataFrame with unmatched records (or None)
    """
    maintenance_df = load_maintenance_data(maintenance_file)

    counts = count_maintenance_by_point(
        maintenance_df, sales_df, site_col, code_col, name_col
    )

    unmatched = generate_unmatched_sheet(
        maintenance_df, sales_df, site_col, code_col
    )

    return counts, unmatched
