import pandas as pd
from core.transformer import clean_column_name


def analyze_data(data: pd.DataFrame, remove_duplicates: bool, remove_non_valid_data: bool, original_row_count: int) -> dict:
    total_rows = len(data)
    columns_data = {}

    for col in data.columns:
        column_name = clean_column_name(col)
        column_data = analyze_column(data[col], total_rows, remove_duplicates, remove_non_valid_data)
        columns_data[column_name] = column_data

    return {
        "total_rows": total_rows,
        "rows_removed": original_row_count - total_rows,
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
            'avg': round(non_null.mean(), 4),
            'median': non_null.median(),
            'std': round(non_null.std(), 4),
            'q25': non_null.quantile(0.25),
            'q75': non_null.quantile(0.75),
        })
    elif pd.api.types.is_datetime64_any_dtype(col):
        analysis.update({
            'type': 'date',
            'most_repeated_date': non_null.mode().iloc[0] if not non_null.mode().empty else None,
            'min_date': non_null.min(),
            'max_date': non_null.max(),
        })
    elif pd.api.types.is_string_dtype(col):
        top_values = (
            non_null.value_counts()
            .head(5)
            .rename_axis('value')
            .reset_index(name='count')
            .to_dict(orient='records')
        )
        analysis.update({
            'type': 'string',
            'most_repeated_value': non_null.mode().iloc[0] if not non_null.mode().empty else None,
            'top_values': top_values,
        })
    else:
        analysis['type'] = 'unknown'

    return analysis


def analyze_column_distribution(df: pd.DataFrame, column: str, top_n: int) -> list:
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found. Available columns: {list(df.columns)}")

    col = df[column]
    total = len(col)
    counts = col.value_counts().head(top_n)

    return [
        {
            "value": str(value),
            "count": int(count),
            "percentage": round((count / total) * 100, 2)
        }
        for value, count in counts.items()
    ]


def detect_column_outliers(df: pd.DataFrame, method: str, columns: list | None) -> list:
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    if columns:
        invalid = [c for c in columns if c not in df.columns]
        if invalid:
            raise ValueError(f"Columns not found: {invalid}")
        numeric_cols = [c for c in columns if c in numeric_cols]

    outliers = []

    for col_name in numeric_cols:
        col = df[col_name].dropna()

        if method == 'iqr':
            q1 = col.quantile(0.25)
            q3 = col.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (df[col_name] < lower) | (df[col_name] > upper)
            reason_template = f"outside IQR bounds [{round(lower, 4)}, {round(upper, 4)}]"
        else:  # zscore
            mean = col.mean()
            std = col.std()
            mask = ((df[col_name] - mean) / std).abs() > 3
            reason_template = "z-score > 3"

        for idx in df[mask].index.tolist():
            outliers.append({
                "row_index": int(idx),
                "column": col_name,
                "value": df.loc[idx, col_name],
                "reason": reason_template
            })

    return outliers


def compare_dataframes(df_a: pd.DataFrame, df_b: pd.DataFrame, mode: str) -> dict:
    cols_a = set(df_a.columns)
    cols_b = set(df_b.columns)
    result = {}

    if mode in ('schema', 'both'):
        result['schema'] = {
            'columns_only_in_a': sorted(cols_a - cols_b),
            'columns_only_in_b': sorted(cols_b - cols_a),
            'common_columns': sorted(cols_a & cols_b),
        }

    if mode in ('rows', 'both'):
        common_cols = sorted(cols_a & cols_b)
        if common_cols:
            merged = df_a[common_cols].merge(df_b[common_cols], how='outer', indicator=True)
            rows_only_in_a = merged[merged['_merge'] == 'left_only']
            rows_only_in_b = merged[merged['_merge'] == 'right_only']
            common_rows = merged[merged['_merge'] == 'both']
            result['rows'] = {
                'total_rows_a': len(df_a),
                'total_rows_b': len(df_b),
                'rows_only_in_a': len(rows_only_in_a),
                'rows_only_in_b': len(rows_only_in_b),
                'common_rows': len(common_rows),
            }
        else:
            result['rows'] = {'error': 'No common columns to compare rows on.'}

    return result
