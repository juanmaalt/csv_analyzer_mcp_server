def format_output(data: dict, output_format: str):
    if output_format == 'json':
        return data

    header_text = "#DATA ANALYSIS\n\n"
    rows_text = total_rows_to_markdown(data['total_rows'], data.get('rows_removed'))
    columns_text = columns_to_markdown(data['columns'])

    return header_text + rows_text + columns_text


def total_rows_to_markdown(total_rows: int, rows_removed: int = None) -> str:
    text = f"## Total Information\nThis analysis was made over a total of {total_rows} rows."
    if rows_removed:
        text += f" ({rows_removed} rows removed during cleaning)"
    return text + "\n\n"


def columns_to_markdown(d: dict) -> str:
    blocks = ["## Information\n"]
    for section, stats in d.items():
        blocks.append(f"### {section}")
        for k, v in stats.items():
            if isinstance(v, list):
                blocks.append(f"- **{k}**:")
                for item in v:
                    blocks.append(f"  - {item}")
            else:
                blocks.append(f"- **{k}**: {v}")
        blocks.append("")
    return "\n".join(blocks)


def format_dataframe_preview(df, n_rows: int) -> str:
    preview = df.head(n_rows)
    cols = list(preview.columns)

    header = "| " + " | ".join(cols) + " |"
    separator = "| " + " | ".join("---" for _ in cols) + " |"
    rows = []
    for _, row in preview.iterrows():
        rows.append("| " + " | ".join(str(v) for v in row.values) + " |")

    return "\n".join([header, separator] + rows)
