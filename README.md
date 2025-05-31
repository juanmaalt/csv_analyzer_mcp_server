# CSV Analyzer MCP Server

A lightweight, modular tool designed to analyze CSV datasets and produce structured summaries suitable for consumption by language models (LLMs) like ChatGPT or Claude.

## Features

- **CSV Content Analysis**: Processes CSV data provided as raw content.
- **Data Cleaning**: Options to remove duplicate entries and rows with missing values.
- **Flexible Output**: Returns results in JSON or Markdown format.
- **Customizable Delimiters**: Supports various CSV delimiters.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/juanmaalt/csv_analyzer_mcp_server.git
   cd csv_analyzer_mcp_server
2. **Install dependencies using uv**:

    ```bash
    uv pip install -r requirements.txt
    ```
    _Note: Ensure you have uv installed. If not, refer to the uv installation guide._

## Usage
The primary function analyze_csv can be invoked with the following parameters:
* csv_content (str): Raw CSV data as a string.
* delimiter (str): Delimiter used in the CSV (default: ,).
* remove_duplicates (bool): Remove duplicate rows (default: True).
* remove_non_valid_data (bool): Remove rows with missing values (default: True).
* output_format (str): Output format - 'json' or 'markdown' (default: 'json').

## Project Structure
```plaintext
csv_analyzer_mcp_server/
├── config/             # Configuration files
├── core/               # Core functionality
├── data/               # Sample CSV files
├── main.py             # Entry point
├── pyproject.toml      # Project metadata
├── uv.lock             # Dependency lock file for uv
└── .gitignore          # Git ignore rules
```
## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.
