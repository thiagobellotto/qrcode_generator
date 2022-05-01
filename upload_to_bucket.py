
import json
import requests
import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import os

def upload_to_bucket(credentials, project_name: str, bucket_name: str, file_name: str, file_path: str):
    '''Upload a file to a bucket'''
    try:
        with open(credentials) as f:
            f = json.load(f)
    except Exception as error:
        print(f'Error: The file {credentials} needs to be in JSON format.')
        raise error

    credentials = service_account.Credentials.from_service_account_file(credentials)
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
        # os.environ['GCP_SERVICE_ACCOUNT']
    )

    storage_client = storage.Client(credentials=credentials, project=project_name)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    with open(file_path, 'rb') as f:
        blob.upload_from_file(f)
        try:
            token = st.secrets["telegram_token"]['token']
            # token = os.environ.get('TELEGRAM_TOKEN')
            requests.get(token)
        except Exception as error:
            print(f'Error: {error}')

    print(f'The file {file_name} was uploaded to {bucket_name}.')
