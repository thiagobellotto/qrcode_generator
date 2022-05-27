def get_metadata_from_blob(blob):

    file_type = blob.name.split(".")[-1]
    bucket = blob.bucket.name
    file_name = blob.name
    file_size = blob.size

    return file_type, bucket, file_size, file_name


def get_metadata_from_dataframe(df):

    rows_count = df.shape[0]
    columns_count = df.shape[1]
    list_of_columns = df.columns.to_list()
    nan_count = df.isna().sum().to_list()
    empty_cells_count = df.applymap(lambda x: x == " ").sum().to_list()
    list_of_columns_size = df.memory_usage().to_list()

    return (
        rows_count,
        columns_count,
        list_of_columns,
        nan_count,
        empty_cells_count,
        list_of_columns_size,
    )
