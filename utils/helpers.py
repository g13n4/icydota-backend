from tabulate import tabulate
import pandas as pd

def print_unique_values(df: pd.DataFrame, column: str):
    for x in sorted([x for x in df[column].unique().tolist() if isinstance(x, str)]):
        print(x)


def print_table(df: pd.DataFrame) -> None:
    print(tabulate(df, headers='keys', tablefmt='psql'))
    return None
