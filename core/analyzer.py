import pandas as pd
from core.transformer import clean_column_name

def analyze_data(data: pd.DataFrame, remove_duplicates: bool, remove_non_valid_data: bool) -> dict:
    total_rows = data.size
    columns_data = {}

    for col in data.columns:
        column_name = clean_column_name(col)
        column_data = analyze_column(data[col], total_rows, remove_duplicates, remove_non_valid_data)

        columns_data[column_name] = column_data

    return {
        "total_rows": total_rows,
        "columns": columns_data
    }

def analyze_column(col: pd.Series, total_rows: int, remove_duplicates: bool, remove_non_valid_data: bool):
    null_count = col.isnull().sum() if not remove_non_valid_data else 'N/A'
    null_percentage = round((null_count / total_rows) * 100, 2) if not remove_non_valid_data else 'N/A'
    duplicate_count = col.duplicated().sum() if not remove_duplicates else 'N/A'
    unique_values = col.nunique(dropna=True)

    non_null = col.dropna() if not remove_non_valid_data else col

    analysis = {
        'null_count': null_count,
        'null_percentage': null_percentage,
        'duplicate_count': duplicate_count,
        'unique_values': unique_values,
    }

    if pd.api.types.is_numeric_dtype(col):
        dtype = 'int' if pd.api.types.is_integer_dtype(col) else 'float'
        analysis.update({
            'type': dtype,
            'min': non_null.min(),
            'max': non_null.max(),
            'avg': non_null.mean()
        })
    elif pd.api.types.is_datetime64_any_dtype(col):
        analysis.update({
            'type': 'date',
            'most_repeated_date': non_null.mode().iloc[0] if not non_null.mode().empty else None,
            'min_date': non_null.min(),
            'max_date': non_null.max(),
        })
    elif pd.api.types.is_string_dtype(col):
        analysis.update({
            'type': 'string',
            'most_repeated_value': non_null.mode().iloc[0] if not non_null.mode().empty else None,
        })
    else:
        analysis['type'] = 'unknown'

    return analysis