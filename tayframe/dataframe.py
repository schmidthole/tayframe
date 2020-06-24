#!/usr/bin/env python3

import csv


def check(df):
    """
    Checks to see if the provided dataframe conforms to the spec.

    The dataframe must be a list and each item in the dataframe must
    be a dict at lease containing the keys o,h,l,c,t and v.

    Params:
      - df (list): dataframe to check

    Returns:
     - (bool) whether the object is a valid dataframe.
    """

    def _check_row(r):
        return (
            isinstance(r, dict)
            and ("t" in r)
            and ("o" in r)
            and ("h" in r)
            and ("l" in r)
            and ("c" in r)
            and ("v" in r)
        )

    return isinstance(df, list) and not (False in [_check_row(r) for r in df])


def append_column(df, col_name, col):
    """
    Append a new column to a dataframe.

    Params:
      - df (list): input dataframe.
      - col_name (str): new column key name.
      - col (list): column data list (should be single items).

    Returns:
      - (list): new dataframe list with column appended.
    """
    # ensure the dataframe fits the new col size
    padded = ([None] * (len(df) - len(col))) + col
    return [{**df[i], **{col_name: padded[i]}} for i in range(len(df))]


def clean(df):
    """
    Clean out any rows containing None in any column.

    Params:
      - df (list): input dataframe.

    Returns:
      - (list): df with all None columns removed.
    """
    return list(filter(lambda r: None not in r.values(), df))


def df_to_csv(df, path):
    """
    Convert a dataframe to csv format with headers.

    Params:
      - df (list): input dataframe.
      - path (str): path string to place file at.
    """
    headers = list(df[-1].keys())

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        [writer.writerow([row[h] if h in row else "" for h in headers]) for row in df]
