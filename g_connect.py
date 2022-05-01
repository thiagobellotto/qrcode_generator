#!/usr/bin/env python
# coding: utf-8

from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st

## Define global variables for connection 
SCOPE = st.secrets['google_sheets']['scope']
SPREADSHEET_ID = st.secrets['google_sheets']['spreadsheet_id']
GSHEET_URL = st.secrets['google_sheets']['gsheet_url']

def connect_to_gsheet(data):
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        data,
        scopes=[SCOPE],
    )

    service = build("sheets", "v4", credentials=credentials)
    gsheet_connector = service.spreadsheets()
    return gsheet_connector

def add_row_to_gsheet(gsheet_connector, sheet_name, row) -> None:
    values = (
        gsheet_connector.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A:E",
            body=dict(values=row),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )