import pandas as pd

def extract_products(path: str) -> pd.DataFrame:
    """
    Read products CSV into a DataFrame
    """
    return pd.read_csv(path, sep=r"\s+", skipinitialspace=True)



