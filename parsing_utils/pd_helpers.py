import pandas as pd


def print_unique_values(df: pd.DataFrame, column: str):
    for x in sorted([x for x in df[column].unique().tolist() if isinstance(x, str)]):
        print(x)


def iterate_df(df: pd.DataFrame, use_offset: bool = True, index_offset: int = 1) -> (int, dict):
    for index, values in df.T.to_dict().items():
        if use_offset:
            index += index_offset
        yield (index, values)
