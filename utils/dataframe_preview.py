import pandas as pd


def select_rows_from_df(df, number_of_rows: int = 5):
    """
    Function to select the first 5 rows, last 5 rows and 5 random rows.
    """
    ## Select first N and last N rows
    df_first = df.head(number_of_rows)
    df_last = df.tail(number_of_rows)

    ## Select 5 random rows, except the first and last 5
    df_random = df.drop(df_first.index)
    df_random = df.drop(df_last.index)
    df_random = df_random.sample(number_of_rows)

    df = pd.concat([df_first, df_random, df_last])

    return df


def convert_to_dict(df):
    """
    Converts a dataframe to a json object.
    """
    list_of_rows = []
    for row in df.itertuples(index=False):
        list_of_rows.append([str(i) for i in row])

    return list_of_rows


def normalize_var_type(df):
    """Function to normalize the types of variables."""

    type_dict = {
        "string": "string",
        "object": "string",
        "boolean": "bool",
        "float": "float",
        "float32": "float",
        "float64": "float",
        "int": "int",
        "int32": "int",
        "int64": "int",
        "datetime64[ns]": "date",
    }

    ## Get the actual types of variable types
    actual_type = [i.name.lower() for i in df.dtypes]

    ## Loop over the list of variable types, and set the normalized names
    for index, data in enumerate(actual_type):
        for key, value in type_dict.items():
            if key in data:
                actual_type[index] = data.replace(key, type_dict[key])

    ## Return the new dict
    return actual_type
