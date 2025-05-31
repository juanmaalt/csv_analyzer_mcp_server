def clean_column_name(column_name: str):
    return column_name.strip().lower().replace(" ", "_")
