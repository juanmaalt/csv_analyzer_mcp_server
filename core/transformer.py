import pandas as pd


def clean_column_name(column_name: str):
    return column_name.strip().lower().replace(" ", "_")


def apply_filter(df: pd.DataFrame, column: str, operator: str, value: str) -> pd.DataFrame:
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found. Available columns: {list(df.columns)}")

    col = df[column]

    if pd.api.types.is_numeric_dtype(col):
        try:
            cast_value = float(value)
        except ValueError:
            raise ValueError(f"Cannot compare numeric column '{column}' with value '{value}'")
    else:
        cast_value = value

    operators = {
        '>':        lambda c, v: c > v,
        '<':        lambda c, v: c < v,
        '>=':       lambda c, v: c >= v,
        '<=':       lambda c, v: c <= v,
        '==':       lambda c, v: c == v,
        '!=':       lambda c, v: c != v,
        'contains': lambda c, v: c.astype(str).str.contains(str(v), case=False, na=False),
    }

    if operator not in operators:
        raise ValueError(f"Invalid operator '{operator}'. Valid operators: {list(operators.keys())}")

    mask = operators[operator](col, cast_value)
    return df[mask].reset_index(drop=True)
