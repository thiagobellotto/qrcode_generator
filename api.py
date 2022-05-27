## Libraries related to the API
from flask import Flask, request, jsonify
from threading import Thread

## Custom packages
# from aitopus_complete import *
from utils.insert_to_table_dataset import insert_to_table_dataset
from utils.dataframe_reader import Dataframe_reader
from utils.dataframe_preview import (
    select_rows_from_df,
    convert_to_dict,
    normalize_var_type,
)
from utils.identify_features import identify_features
from utils.get_metadata import get_metadata_from_blob, get_metadata_from_dataframe

## Google Cloud libraries
from google.cloud import storage
from google.cloud.exceptions import NotFound

## Other libraries
import os
from io import BytesIO
import psycopg2

## Define the app object
app = Flask(__name__)


## To-do
# Usuario não pode enviar dataframe com nome de colunas repetidas


@app.route("/", methods=["GET"])
def index():
    return {
        "Status": "This is the API that will be used to train a Machine Learning model."
    }


@app.route("/bucket_preview", methods=["GET"])
def bucket_reader():
    """
    Bucket function to read files from a bucket.
    If no bucket is set, It will return a list of all files inside a bucket.
    If a bucket is set, It will return a list of all files inside a bucket.
    """

    bucket_name = request.args.get("bucket")
    file_name = request.args.get("file")
    connection_type = request.args.get("connection")

    ## Control flow - If bucket is none, it means it is probably on the root. So, return the instructions
    if bucket_name is None:
        return {"Status": "You need to specify a bucket name."}
    ## If the length of the name of the bucket is smaller than 4, return an advice for the user
    elif len(bucket_name) <= 4:
        return {
            "Status": "The name of the buckets must have the length greater than 4 characters."
        }
    ## If there is a file name without a bucket name, return an advice for the user
    elif file_name is not None and bucket_name is None:
        return {"Status": "You need to specify a bucket name."}

    ## Instantiate the object storage/bucket and search for the bucket sent
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except NotFound:
        return {"Alert": f"The bucket {bucket_name} was not found. Check for typos!"}

    ## List files on bucket
    blob_list = bucket.list_blobs()
    blob_list = list(blob_list)
    print("blob: ", blob_list)

    ## Checks for the name of the file. If None, reads the files/folders in the directory
    if file_name is None:
        return {f"Files found at bucket {bucket_name}": [x.name for x in blob_list]}
    ## Else, checks for the match of the file
    else:
        ## Look for the name of the file inside the list of blobs
        file_founded = [x for x in blob_list if x.name == file_name]

        ## If the file is not found, return an advice for the user
        if file_founded:

            ## If so, we access that specific file and return the metadata
            blob = bucket.get_blob(file_name)

            ## Get metadata, directly from the blob object
            file_type, bucket, file_size, file_name = get_metadata_from_blob(blob)

            ## Download the file as a BytesIO object
            file = BytesIO(blob.download_as_string())

            ## Process and parses the file to a dataframe, along with the extension
            df = Dataframe_reader(
                file,
                extension=file_type,
            )

            ## Get the types of the columns of the dataframe
            list_of_columns_types = normalize_var_type(df.dataframe)

            ## Gets the type of each column (class, many classes, integer, etc)
            id_features = identify_features(df.dataframe).identify_process()

            ## Obtain the metadata from the dataframe
            (
                rows_count,
                columns_count,
                list_of_columns,
                nan_count,
                empty_cells_count,
                list_of_columns_size,
            ) = get_metadata_from_dataframe(df.dataframe)

            ## Samples the dataframe to get a preview of the dataframe, with the first 5 + last 5 + random 5 rows
            df = select_rows_from_df(df.dataframe)

            ## Creates a tuple with the metadata of the dataframe and blob object
            values = (
                1,
                1,
                file_type,
                file_name,
                bucket,
                connection_type,
                file_size,
                rows_count,
                columns_count,
                list_of_columns,
                list_of_columns_types,
                list_of_columns_size,
                nan_count,
                empty_cells_count,
            )

            ## Inserts the log to the database
            insert_to_table_dataset(values=values)

            ## Returns the infos required by the front-end
            df_info = {
                "Name of Columns": df.columns.to_list(),
                "Types": id_features,
                "Dataframe": convert_to_dict(df),
                "Dropdown": ["Target variable"],
            }

            ## Returns the dataframe and the metadata
            return jsonify(df_info)
        else:
            return {"Status": "File was not found."}


# @app.route("/train_model", methods=["GET", "POST"])
# def return_status():

#     connect_db("Entrou na rota")
#     Thread(target=train_model, kwargs=request.get_json()).start()
#     return jsonify("Response asynchronosly")


# def train_model(**kwargs):

#     connect_db("Entrou na função")
#     req_json = kwargs

#     df = req_json["Dataframe"]
#     target = req_json["target"]
#     approach = int(req_json["approach"])
#     optimize = req_json["optimize"]
#     out_apply = eval(req_json["out_apply"])
#     sample_apply = eval(req_json["sample_apply"])
#     select_models = eval(req_json["select_models"])
#     tunning = eval(req_json["tunning"])
#     ensemble = eval(req_json["ensemble"])

#     connect_db("Pegou todos os parametros corretamente")

#     df = pd.DataFrame.from_dict(df, orient="columns")

#     df.replace({"": np.nan}, inplace=True)

#     tes = Aitopus(
#         dataframe=df,
#         target=target,
#         approach=approach,
#         optimize=optimize,
#         n_models=2,
#         exclude=[],
#     )
#     connect_db("Instancio o modelo")
#     tes.finish(ensemble=ensemble, tunning=tunning, start_models=select_models)
#     connect_db("Terminou a modelagem")

#     result = tes.plot_info(0)

#     connect_db("Completed")

#     return print("Process Finished")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
