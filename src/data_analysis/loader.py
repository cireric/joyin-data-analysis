"""
Data Loader Module

Handles loading and validating data from Excel files.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Union


def load_data(config: dict) -> Dict[str, pd.DataFrame]:
    """
    Load data from Excel based on configuration.
    
    Args:
        config: Configuration dictionary with data_source and periods
        
    Returns:
        Dictionary mapping period labels to DataFrames
    """
    data = {}
    ds = config['data_source']
    periods = config.get('periods', {})

    if ds['type'] == 'multi_sheet':
        xl = pd.ExcelFile(ds['path'])
        for sheet in ds['sheets']:
            data[str(sheet)] = pd.read_excel(xl, sheet_name=str(sheet))
    elif ds['type'] == 'multi_file':
        for file_path in ds['files']:
            name = Path(file_path).stem
            df = pd.read_excel(file_path)
            if 'current_file' in periods and name == periods['current_file']:
                data[periods['current']] = df
            elif 'previous_file' in periods and name == periods['previous_file']:
                data[periods['previous']] = df
            else:
                data[name] = df

    return data


def validate_data(data: Dict[str, pd.DataFrame], periods: dict, 
                  key_column: str, value_columns: list) -> None:
    """
    Validate loaded data has required periods and columns.
    
    Args:
        data: Dict of period DataFrames
        periods: Period labels
        key_column: Key column name
        value_columns: List of value column configs
        
    Raises:
        ValueError: If data is invalid
    """
    current_key = periods['current']
    previous_key = periods['previous']
    
    if current_key not in data:
        raise ValueError(f"Current period data not found: '{current_key}'")
    if previous_key not in data:
        raise ValueError(f"Previous period data not found: '{previous_key}'")
    
    for period_key in [current_key, previous_key]:
        df = data[period_key]
        
        if df.empty:
            raise ValueError(f"Empty dataset for period: '{period_key}'")
        
        if key_column not in df.columns:
            raise ValueError(f"Key column '{key_column}' not found in period '{period_key}'")
        
        missing_cols = []
        for vc in value_columns:
            col_name = vc['name'] if isinstance(vc, dict) else vc
            if col_name not in df.columns:
                missing_cols.append(col_name)
        
        if missing_cols:
            raise ValueError(f"Value columns not found in period '{period_key}': {missing_cols}")


def validate_config(config: dict) -> None:
    """
    Validate configuration has all required fields.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValueError: If required fields are missing
    """
    required_keys = ['data_source', 'periods', 'key_column', 'value_columns', 'analysis', 'output']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: '{key}'")
    
    if 'current' not in config['periods'] or 'previous' not in config['periods']:
        raise ValueError("Config 'periods' must have 'current' and 'previous' keys")
    
    if 'title' not in config['output'] or 'dir' not in config['output']:
        raise ValueError("Config 'output' must have 'title' and 'dir' keys")
    
    if not config['value_columns']:
        raise ValueError("Config 'value_columns' cannot be empty")
