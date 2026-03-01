from mcp.server.fastmcp import FastMCP
from core.loader import load_csv
from core.analyzer import analyze_data, analyze_column_distribution, detect_column_outliers, compare_dataframes
from core.formatter import format_output, format_dataframe_preview
from core.transformer import apply_filter


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
        dict or str: Analysis summary in the specified output format. Includes total_rows,
                     rows_removed, and per-column statistics (type, nulls, uniques, min/max/avg,
                     median, std, quartiles for numeric; top_values for strings; date range for dates).

    Notes:
        - This function does not read files from disk. All data must be passed as raw content.
        - Designed for use in remote or constrained environments where file paths aren't accessible.
    """
    if output_format not in {"json", "markdown"}:
        raise ValueError("output_format must be 'json' or 'markdown'")

    data, original_row_count = load_csv(csv_content, delimiter, remove_duplicates, remove_non_valid_data)
    analysis = analyze_data(data, remove_duplicates, remove_non_valid_data, original_row_count)

    return format_output(analysis, output_format=output_format)


@mcp.tool()
def get_csv_preview(
    csv_content: str,
    delimiter: str = ",",
    n_rows: int = 5
) -> str:
    """
    Return the first n rows of a CSV file as a Markdown table.

    Args:
        csv_content (str): The full text content of the CSV file as a string.
        delimiter (str): Character separating values in the CSV. Default is ','.
        n_rows (int): Number of rows to preview. Default is 5.

    Returns:
        str: Markdown table with the first n rows and all column headers.

    Notes:
        - No data cleaning is applied. All rows are shown as-is, including nulls and duplicates.
    """
    data, _ = load_csv(csv_content, delimiter, remove_duplicates=False, remove_non_valid_data=False)
    return format_dataframe_preview(data, n_rows)


@mcp.tool()
def filter_csv(
    csv_content: str,
    column: str,
    operator: str,
    value: str,
    delimiter: str = ",",
) -> str:
    """
    Filter rows from a CSV by a column condition and return the filtered CSV as a string.

    Args:
        csv_content (str): The full text content of the CSV file as a string.
        column (str): Name of the column to filter on.
        operator (str): Comparison operator. One of: '>', '<', '>=', '<=', '==', '!=', 'contains'.
        value (str): Value to compare against. Will be cast to the column's dtype automatically.
        delimiter (str): Character separating values in the CSV. Default is ','.

    Returns:
        str: Filtered CSV content as a string. Can be passed directly to analyze_csv for further analysis.

    Notes:
        - 'contains' performs a case-insensitive substring match on string columns.
        - Numeric casting is applied automatically when the target column is numeric.
        - No data cleaning is applied before filtering.
    """
    data, _ = load_csv(csv_content, delimiter, remove_duplicates=False, remove_non_valid_data=False)
    filtered = apply_filter(data, column, operator, value)
    return filtered.to_csv(index=False)


@mcp.tool()
def get_column_distribution(
    csv_content: str,
    column: str,
    delimiter: str = ",",
    top_n: int = 10
) -> list:
    """
    Return a ranked frequency table for a specific column.

    Args:
        csv_content (str): The full text content of the CSV file as a string.
        column (str): Name of the column to analyze.
        delimiter (str): Character separating values in the CSV. Default is ','.
        top_n (int): Maximum number of values to return, sorted by frequency. Default is 10.

    Returns:
        list: List of dicts with 'value', 'count', and 'percentage' keys, sorted by frequency descending.

    Notes:
        - Null values are excluded from the frequency count.
        - No data cleaning is applied before computing the distribution.
    """
    data, _ = load_csv(csv_content, delimiter, remove_duplicates=False, remove_non_valid_data=False)
    return analyze_column_distribution(data, column, top_n)


@mcp.tool()
def detect_outliers(
    csv_content: str,
    delimiter: str = ",",
    method: str = "iqr",
    columns: list[str] | None = None
) -> list:
    """
    Detect outlier rows in numeric columns using IQR or z-score method.

    Args:
        csv_content (str): The full text content of the CSV file as a string.
        delimiter (str): Character separating values in the CSV. Default is ','.
        method (str): Detection method - 'iqr' (default) or 'zscore'.
                      IQR flags values outside Q1 - 1.5*IQR and Q3 + 1.5*IQR.
                      Z-score flags values more than 3 standard deviations from the mean.
        columns (list[str] | None): Limit detection to specific columns. If None, all numeric columns are checked.

    Returns:
        list: List of dicts with 'row_index', 'column', 'value', and 'reason' for each outlier found.

    Notes:
        - Rows with missing values are removed before detection.
        - Only numeric columns are analyzed. String and date columns are ignored.
    """
    if method not in {"iqr", "zscore"}:
        raise ValueError("method must be 'iqr' or 'zscore'")

    data, _ = load_csv(csv_content, delimiter, remove_duplicates=False, remove_non_valid_data=True)
    return detect_column_outliers(data, method, columns)


@mcp.tool()
def compare_csvs(
    csv_content_a: str,
    csv_content_b: str,
    delimiter: str = ",",
    mode: str = "both"
) -> dict:
    """
    Compare two CSV files by schema, row content, or both.

    Args:
        csv_content_a (str): The full text content of the first CSV file as a string.
        csv_content_b (str): The full text content of the second CSV file as a string.
        delimiter (str): Character separating values in both CSVs. Default is ','.
        mode (str): What to compare - 'schema', 'rows', or 'both' (default).
                    'schema' reports columns added, removed, and shared between the two files.
                    'rows' counts rows unique to each file vs rows present in both (on common columns).

    Returns:
        dict: Comparison result. 'schema' key contains column diffs. 'rows' key contains row counts.

    Notes:
        - No data cleaning is applied to either file before comparison.
        - Row comparison uses common columns only.
    """
    if mode not in {"schema", "rows", "both"}:
        raise ValueError("mode must be 'schema', 'rows', or 'both'")

    data_a, _ = load_csv(csv_content_a, delimiter, remove_duplicates=False, remove_non_valid_data=False)
    data_b, _ = load_csv(csv_content_b, delimiter, remove_duplicates=False, remove_non_valid_data=False)

    return compare_dataframes(data_a, data_b, mode)


# RUN SERVER
if __name__ == "__main__":
    mcp.run(transport="stdio")
