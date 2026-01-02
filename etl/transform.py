import pandas as pd

def filter_expensive_products(df: pd.DataFrame, min_price: float = 100) -> pd.DataFrame:
    """
    Keep products with price greater than min_price
    """
    return df[df["price"] > min_price]
