from mcp.server.fastmcp import FastMCP
from core.loader import load_csv
from core.analyzer import analyze_data
from core.formatter import format_output


mcp = FastMCP("csv_analyzer")


@mcp.tool()
def analyze_csv(
    csv_content: str,
    delimiter: str = ",", 
    remove_duplicates: bool = True,
    remove_non_valid_data: bool = True,
    output_format: str = "json"
) -> dict | str:
    """
    Analyze the content of a CSV file and return structured data.

    Args:
        csv_content (str): The full text content of the CSV file as a string.
                           This should be passed directly (not as a file path).
                           For example, read the file and pass its content via file.read().
        delimiter (str): Character separating values in the CSV. Default is ','.
        remove_duplicates (bool): If True (default), removes rows that are exact duplicates.
        remove_non_valid_data (bool): If True (default), removes rows with missing or empty fields.
        output_format (str): Format of the output - 'json' (default) or 'markdown'.

    Returns:
        dict or str: Analysis summary and cleaned data in the specified output format.

    Notes:
        - This function does not read files from disk. All data must be passed as raw content.
        - Designed for use in remote or constrained environments where file paths aren't accessible.
    """

    if output_format not in {"json", "markdown"}:
        raise ValueError("output_format must be 'json' or 'markdown'")

    # Load and process the data
    data = load_csv(csv_content, delimiter, remove_duplicates, remove_non_valid_data)
    analysis = analyze_data(data, remove_duplicates, remove_non_valid_data)

    # Return formatted output
    return format_output(analysis, output_format=output_format)


# RUN SERVER
if __name__ == "__main__":
    mcp.run(transport="stdio")

