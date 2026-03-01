# CSV Analyzer MCP Server

A lightweight MCP server that exposes CSV analysis as tools callable by any MCP-compatible client.

Pass raw CSV content, get back structured statistics — row counts, type detection, null rates, duplicates, distributions, outlier detection, and more — in JSON or Markdown.

---

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) is an open standard that lets AI assistants call external tools. This server exposes CSV analysis as MCP tools, so you can ask Claude things like *"analyze this CSV and tell me which columns have the most nulls"* or *"filter rows where revenue > 10000 and then analyze the result"* and get back real computed results.

---

## Features

- **Column-level analysis** — type detection, null rate, unique values, min/max/avg/median/std, quartiles, most repeated values, date ranges
- **Frequency distribution** — ranked value counts with percentages for any column
- **Outlier detection** — IQR and z-score methods across all numeric columns
- **Row filtering** — filter by column condition and chain into further analysis
- **Data preview** — inspect the first N rows as a Markdown table before analyzing
- **CSV comparison** — diff two files by schema, row content, or both
- **Data cleaning** — optional deduplication and null-row removal before analysis
- **Dual output formats** — structured JSON for programmatic use or Markdown for readable summaries
- **Custom delimiters** — comma, semicolon, tab, pipe, or any separator
- **Content-based** — accepts raw CSV text, not file paths, making it safe and compatible with remote environments

---

## Installation

**Prerequisites:** Python ≥ 3.12 and [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
git clone https://github.com/juanmaalt/csv_analyzer_mcp_server.git
cd csv_analyzer_mcp_server
uv sync
```

---

## Connecting to an MCP Client

### Claude Desktop

Add the following to your `claude_desktop_config.json`
(usually at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "csv_analyzer": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/csv_analyzer_mcp_server",
        "python",
        "main.py"
      ]
    }
  }
}
```

### Cursor / VS Code (MCP extension)

```json
{
  "mcp": {
    "servers": {
      "csv_analyzer": {
        "command": "uv",
        "args": [
          "run",
          "--directory",
          "/absolute/path/to/csv_analyzer_mcp_server",
          "python",
          "main.py"
        ]
      }
    }
  }
}
```

Restart the client after saving the configuration. All tools will appear in the available tools list.

---

## Available Tools

### `analyze_csv`

Full statistical analysis of a CSV file. Returns per-column summaries including type, null rate, unique count, and type-specific stats.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `csv_content` | `str` | required | Full CSV text content (not a file path) |
| `delimiter` | `str` | `","` | Character separating values |
| `remove_duplicates` | `bool` | `True` | Drop exact duplicate rows before analysis |
| `remove_non_valid_data` | `bool` | `True` | Drop rows with missing/empty fields before analysis |
| `output_format` | `str` | `"json"` | `"json"` or `"markdown"` |

**JSON output structure:**

```json
{
  "total_rows": 38,
  "rows_removed": 2,
  "columns": {
    "age": {
      "null_count": "N/A",
      "null_percentage": "N/A",
      "duplicate_count": "N/A",
      "unique_values": 22,
      "type": "int",
      "min": 19,
      "max": 74,
      "avg": 43.5,
      "median": 42.0,
      "std": 14.2,
      "q25": 31.0,
      "q75": 57.0
    },
    "plan_type": {
      "null_count": "N/A",
      "null_percentage": "N/A",
      "duplicate_count": "N/A",
      "unique_values": 3,
      "type": "string",
      "most_repeated_value": "Premium",
      "top_values": [
        {"value": "Premium", "count": 18},
        {"value": "Basic", "count": 12},
        {"value": "Enterprise", "count": 8}
      ]
    }
  }
}
```

---

### `get_csv_preview`

Returns the first N rows of a CSV as a Markdown table. Useful for inspecting structure and values before running a full analysis. No cleaning is applied.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `csv_content` | `str` | required | Full CSV text content |
| `delimiter` | `str` | `","` | Character separating values |
| `n_rows` | `int` | `5` | Number of rows to return |

**Example output:**

```
| customer_id | age | plan_type | monthly_fee |
| --- | --- | --- | --- |
| 1001 | 34 | Premium | 49.99 |
| 1002 | 27 | Basic | 19.99 |
```

---

### `filter_csv`

Filters rows by a column condition and returns the result as a CSV string. The output can be passed directly into `analyze_csv` or any other tool.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `csv_content` | `str` | required | Full CSV text content |
| `column` | `str` | required | Column name to filter on |
| `operator` | `str` | required | One of: `>`, `<`, `>=`, `<=`, `==`, `!=`, `contains` |
| `value` | `str` | required | Value to compare against (auto-cast to column type) |
| `delimiter` | `str` | `","` | Character separating values |

**Supported operators:**

| Operator | Behavior |
|---|---|
| `>` `<` `>=` `<=` | Numeric comparison |
| `==` `!=` | Equality (works on any type) |
| `contains` | Case-insensitive substring match on string columns |

---

### `get_column_distribution`

Returns a ranked frequency table for a specific column — how many times each value appears and what percentage of rows it represents.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `csv_content` | `str` | required | Full CSV text content |
| `column` | `str` | required | Column name to analyze |
| `delimiter` | `str` | `","` | Character separating values |
| `top_n` | `int` | `10` | Maximum number of values to return |

**Example output:**

```json
[
  {"value": "Premium", "count": 18, "percentage": 45.0},
  {"value": "Basic", "count": 12, "percentage": 30.0},
  {"value": "Enterprise", "count": 8, "percentage": 20.0}
]
```

---

### `detect_outliers`

Finds rows with outlier values in numeric columns using IQR or z-score. Returns the flagged rows with the column name, value, and reason.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `csv_content` | `str` | required | Full CSV text content |
| `delimiter` | `str` | `","` | Character separating values |
| `method` | `str` | `"iqr"` | `"iqr"` or `"zscore"` |
| `columns` | `list[str]` | `None` | Specific columns to check. If omitted, all numeric columns are checked |

**Methods:**
- `iqr` — flags values outside `Q1 - 1.5 * IQR` and `Q3 + 1.5 * IQR`
- `zscore` — flags values more than 3 standard deviations from the mean

**Example output:**

```json
[
  {"row_index": 4, "column": "monthly_fee", "value": 999.99, "reason": "outside IQR bounds [10.5, 89.3]"},
  {"row_index": 21, "column": "age", "value": 3, "reason": "outside IQR bounds [22.0, 68.0]"}
]
```

---

### `compare_csvs`

Compares two CSV files by schema (column differences) and/or row content. Useful for detecting changes between versions of the same dataset.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `csv_content_a` | `str` | required | Full CSV text content of the first file |
| `csv_content_b` | `str` | required | Full CSV text content of the second file |
| `delimiter` | `str` | `","` | Character separating values in both files |
| `mode` | `str` | `"both"` | `"schema"`, `"rows"`, or `"both"` |

**Example output (`mode="both"`):**

```json
{
  "schema": {
    "columns_only_in_a": ["notes"],
    "columns_only_in_b": ["region"],
    "common_columns": ["client", "revenue", "date"]
  },
  "rows": {
    "total_rows_a": 25,
    "total_rows_b": 28,
    "rows_only_in_a": 4,
    "rows_only_in_b": 7,
    "common_rows": 21
  }
}
```

---

## Composing Tools

Tools are designed to chain together. Some useful patterns:

```
# Preview first, then analyze
get_csv_preview → analyze_csv

# Filter a subset, then analyze it
filter_csv (churned == True) → analyze_csv

# Check distribution before deciding how to filter
get_column_distribution → filter_csv → analyze_csv

# Find outliers, then filter them out and re-analyze
detect_outliers → filter_csv (!= outlier_value) → analyze_csv
```

---

## Configuration

Settings are loaded from the `.env` file at the project root:

| Variable | Default | Description |
|---|---|---|
| `MAX_ROWS_TO_ANALYZE` | `500` | Maximum rows processed per request |
| `DEFAULT_OUTPUT_FORMAT` | `markdown` | Fallback output format |
| `MAX_PREVIEW_ROWS` | `10` | Number of preview rows in summaries |
| `NULL_THRESHOLD_WARNING` | `0.3` | Null rate above which a warning is surfaced |
| `OUTLIER_STDDEV_CUTOFF` | `3.0` | Z-score cutoff for outlier detection |

---

## Project Structure

```
csv_analyzer_mcp_server/
├── core/
│   ├── loader.py        # CSV string → pandas DataFrame
│   ├── analyzer.py      # Per-column statistics, distribution, outlier detection, comparison
│   ├── formatter.py     # JSON / Markdown output, table preview
│   └── transformer.py   # Column name normalization, row filtering
├── config/
│   └── settings.py      # Environment-based configuration
├── data/                # Sample CSV files for testing
├── main.py              # MCP server entry point — all tool definitions
├── pyproject.toml       # Project metadata and dependencies
└── .env                 # Local configuration (not committed)
```

---

## Sample Data

Three sample CSV files are included in `data/` for testing:

| File | Rows | Description |
|---|---|---|
| `sample_data_usage.csv` | 40 | Telecom customer usage (age, plan, data, churn) |
| `sample_heart_checks.csv` | 40 | Medical records (cholesterol, BP, diabetes, heart disease) |
| `sample_project_revenue.csv` | 25 | Project billing with intentional missing values |

---
