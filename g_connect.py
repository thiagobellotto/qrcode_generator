#!/usr/bin/env python
# coding: utf-8

from google.oauth2 import service_account
from googleapiclient.discovery import build

## Define global variables for connection 
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1o3_pxe9VcjFJGCtRoqLw6Npfhwj1ZNzCe-W_ru3SNVM"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

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