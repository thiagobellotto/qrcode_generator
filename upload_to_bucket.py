
import json
from google.cloud import storage
from google.oauth2 import service_account
from send_http_request import send_http_request

def upload_to_bucket(credentials, project_name: str, bucket_name: str, file_name: str, file_path: str):
    '''Upload a file to a bucket'''
    try:
        with open(credentials) as f:
            f = json.load(f)
    except Exception as error:
        print(f'Error: The file {credentials} needs to be in JSON format.')
        raise error

    credentials = service_account.Credentials.from_service_account_file(credentials)

    storage_client = storage.Client(credentials=credentials, project=project_name)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    with open(file_path, 'rb') as f:
        blob.upload_from_file(f)

    send_http_request()
    print(f'The file {file_name} was uploaded to {bucket_name}.')
