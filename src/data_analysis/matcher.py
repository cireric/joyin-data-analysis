"""
Point Matcher Module

Handles matching maintenance records to sales points via machine code.
"""

import re
import pandas as pd
from typing import Optional, Dict, Set


def extract_machine_code(site_name: str) -> Optional[str]:
    """
    Extract 5-digit machine code from site name.

    Args:
        site_name: Site name string (e.g., '小榄/23398/小榄服务区服务楼')

    Returns:
        5-digit machine code string, or None if not found

    Examples:
        >>> extract_machine_code('小榄/23398/小榄服务区服务楼')
        '23398'
        >>> extract_machine_code('粤北/南医五院外科楼/26040')
        '26040'
        >>> extract_machine_code('无机器码的站点')
        None
    """
    if not site_name or pd.isna(site_name):
        return None

    match = re.search(r'/(\d{5})(?:/|$)', str(site_name))
    if match:
        return match.group(1)

    match = re.search(r'(\d{5})', str(site_name))
    if match:
        return match.group(1)

    return None


def match_by_machine_code(
    maintenance_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    site_col: str = '站点名称',
    code_col: str = '机器编号',
    name_col: str = '点位名称'
) -> Dict[str, str]:
    """
    Match maintenance records to sales points via machine code.

    Args:
        maintenance_df: DataFrame with maintenance records
        sales_df: DataFrame with sales data
        site_col: Column name for site name in maintenance_df
        code_col: Column name for machine code in sales_df
        name_col: Column name for point name in sales_df

    Returns:
        Dict mapping machine code to point name: {'23398': '小榄服务区服务楼'}
    """
    valid_mask = sales_df[code_col].notna() & sales_df[name_col].notna()
    valid_df = sales_df[valid_mask]
    sales_code_to_name = dict(zip(
        valid_df[code_col].astype(int).astype(str),
        valid_df[name_col]
    ))

    matched = {}
    site_names = maintenance_df[site_col].dropna()
    for site_name in site_names:
        code = extract_machine_code(site_name)
        if code and code in sales_code_to_name:
            matched[code] = sales_code_to_name[code]

    return matched


def get_matched_codes(
    maintenance_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    site_col: str = '站点名称',
    code_col: str = '机器编号'
) -> Set[str]:
    """
    Get set of machine codes that matched successfully.

    Args:
        maintenance_df: DataFrame with maintenance records
        sales_df: DataFrame with sales data
        site_col: Column name for site name in maintenance_df
        code_col: Column name for machine code in sales_df

    Returns:
        Set of matched machine codes
    """
    sales_codes = set()
    for code in sales_df[code_col].dropna():
        sales_codes.add(str(int(code)))

    matched = set()
    for site_name in maintenance_df[site_col].dropna():
        code = extract_machine_code(site_name)
        if code and code in sales_codes:
            matched.add(code)

    return matched


def get_unmatched_records(
    maintenance_df: pd.DataFrame,
    matched_codes: Set[str],
    site_col: str = '站点名称'
) -> pd.DataFrame:
    """
    Get maintenance records that could not be matched.

    Args:
        maintenance_df: DataFrame with maintenance records
        matched_codes: Set of machine codes that matched
        site_col: Column name for site name

    Returns:
        DataFrame with unmatched records
    """
    site_names = maintenance_df[site_col]
    codes = site_names.apply(extract_machine_code)

    unmatched_mask = codes.isna() | ~codes.isin(matched_codes)
    result = maintenance_df[unmatched_mask].copy()
    result['提取机器码'] = codes[unmatched_mask]

    return result
