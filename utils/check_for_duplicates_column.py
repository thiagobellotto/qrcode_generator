from collections import Counter


def check_columns(df):
    """
    It takes a dataframe as input and returns a list of duplicate column names.

    :param df: The dataframe you want to check for duplicate columns
    :return: A list of duplicate column names.
    """

    columns = df.columns.tolist()
    if len(columns) != len(set(columns)):
        count = Counter(columns).most_common(1000)
        list_of_duplicates = [i[0] for i in count if i[1] > 1]
        return list_of_duplicates
    else:
        return []
