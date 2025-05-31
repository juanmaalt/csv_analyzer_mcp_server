def format_output(data: dict, output_format: str):
    if output_format == 'json':
        return data
    
    header_text = "#DATA ANALYSIS\n\n"
    rows_text = total_rows_to_markdown(data['total_rows'])
    columns_text = columns_to_markdown(data['columns'])

    return header_text + rows_text + columns_text

def total_rows_to_markdown(total_rows: int) -> str:
    return f"## Total Information\nThis analysis was made over a total of {total_rows} rows.\n\n"

def columns_to_markdown(d: dict) -> str:
    blocks = ["## Information\n"]
    for section, stats in d.items():
        blocks.append(f"### {section}")
        for k, v in stats.items():
            blocks.append(f"- **{k}**: {v}")
        blocks.append("")
    return "\n".join(blocks)