import pandas as pd
from io import StringIO

def load_csv(csv_content: str, delimiter: str, remove_duplicates: bool, remove_non_valid_data: bool):
    # Convert .csv into a Data frame 
    buffer = StringIO(csv_content)
    df = pd.read_csv(buffer, delimiter= delimiter)

    # Remove null values
    if (remove_non_valid_data):
        df = df.dropna()

    # Remove duplicates
    if (remove_duplicates):
        df.drop_duplicates(inplace = True)

    return df