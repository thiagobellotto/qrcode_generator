import requests

def send_http_request():
    try:
        params_for_http = {"message": "QR Code Generator is running"}
        http = requests.get('https://southamerica-east1-qr-code-streamlit.cloudfunctions.net/telegram-nofication', params=params_for_http)
        print(f'Request status: {http.text}')
    except Exception as error:
        print(f'Error: {error}')
        raise error
