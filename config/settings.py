from dotenv import load_dotenv
import os

# Load values from .env file if present
load_dotenv()

# General configuration
MAX_ROWS_TO_ANALYZE = int(os.getenv("MAX_ROWS_TO_ANALYZE", 1000))
DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "json")
SUPPORTED_OUTPUT_FORMATS = {"json", "markdown"}

# Analysis-specific thresholds
NULL_THRESHOLD_WARNING = float(os.getenv("NULL_THRESHOLD_WARNING", 0.3))  # warn if >30% nulls
OUTLIER_STDDEV_CUTOFF = float(os.getenv("OUTLIER_STDDEV_CUTOFF", 3.0))    # for future use

# Formatter config
MAX_PREVIEW_ROWS = int(os.getenv("MAX_PREVIEW_ROWS", 10))
MAX_COLUMN_WIDTH = int(os.getenv("MAX_COLUMN_WIDTH", 30))

# JSON formatting
JSON_INDENT = int(os.getenv("JSON_INDENT", 2))
