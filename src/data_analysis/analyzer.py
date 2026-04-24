"""
Data Analyzer Module

Handles data analysis: merging, filling, calculating comparisons.
"""

import pandas as pd
import numpy as np
from typing import List, Union


def standardize_columns(df: pd.DataFrame, period: str, 
                        value_columns: list, key_column: str) -> pd.DataFrame:
    """Rename columns with period suffix."""
    new_cols = {key_column: 'key'}
    for vc in value_columns:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        if col_name in df.columns:
            new_cols[col_name] = f"{col_name}_{period}"
    return df.rename(columns=new_cols)


def merge_periods(data: dict, periods: dict, 
                  key_column: str, value_columns: list) -> pd.DataFrame:
    """
    Merge data from multiple periods using outer join.
    
    Args:
        data: Dict of period DataFrames
        periods: Dict with 'current' and 'previous' keys
        key_column: Column to merge on
        value_columns: List of value column configs
        
    Returns:
        Merged DataFrame with columns from both periods
    """
    current_df = standardize_columns(data[periods['current']], 'current', value_columns, key_column)
    previous_df = standardize_columns(data[periods['previous']], 'previous', value_columns, key_column)

    merged = current_df.merge(previous_df, on='key', how='outer')
    merged.rename(columns={'key': key_column}, inplace=True)

    return merged


def fill_missing_values(df: pd.DataFrame, key_column: str, value_columns: list) -> pd.DataFrame:
    """
    Fill missing values for existing points.
    
    Logic:
    - Point exists in both periods but data missing → fill with 0
    - Point only exists in one period → keep NaN (comparison shows N/A)
    """
    for vc in value_columns:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        current_col = f"{col_name}_current"
        previous_col = f"{col_name}_previous"
        
        if current_col in df.columns and previous_col in df.columns:
            both_have_data = df[current_col].notna() & df[previous_col].notna()
            one_has_data = df[current_col].notna() | df[previous_col].notna()
            fill_mask = one_has_data & ~both_have_data
            
            df.loc[fill_mask, current_col] = df.loc[fill_mask, current_col].fillna(0)
            df.loc[fill_mask, previous_col] = df.loc[fill_mask, previous_col].fillna(0)
    
    return df


def calc_comparison(current, previous):
    """
    Calculate comparison percentage.

    Returns 'N/A' if current or previous is NaN, or if previous is 0.
    """
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return 'N/A'
    return (current - previous) / previous


def calculate_analysis(df: pd.DataFrame, value_columns: list, 
                       analysis_types: list) -> pd.DataFrame:
    """
    Calculate YoY/MoM comparisons for each value column.
    
    Args:
        df: DataFrame with _current and _previous columns
        value_columns: List of value column configs
        analysis_types: List of analysis types (e.g., ['yoy'])
        
    Returns:
        DataFrame with added _yoy columns
    """
    for vc in value_columns:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        current_col = f"{col_name}_current"
        previous_col = f"{col_name}_previous"

        if 'yoy' in analysis_types:
            df[f"{col_name}_yoy"] = df.apply(
                lambda row: calc_comparison(row[current_col], row[previous_col]), axis=1
            )

    return df


def add_totals(df: pd.DataFrame, key_column: str, 
               value_columns: list, analysis_types: list) -> pd.DataFrame:
    """
    Add summary row at the end with totals and overall comparison.
    
    Args:
        df: DataFrame with analysis columns
        key_column: Name of key column
        value_columns: List of value column configs
        analysis_types: List of analysis types
        
    Returns:
        DataFrame with totals row appended
    """
    totals = {key_column: '总计'}

    for vc in value_columns:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        current_col = f"{col_name}_current"
        previous_col = f"{col_name}_previous"

        current_total = df[current_col].sum()
        previous_total = df[previous_col].sum()

        totals[current_col] = current_total
        totals[previous_col] = previous_total

        if 'yoy' in analysis_types:
            totals[f"{col_name}_yoy"] = calc_comparison(current_total, previous_total)

    point_count = len(df)
    totals[key_column] = f'总计（{point_count}台）'

    return pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
