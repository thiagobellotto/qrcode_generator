import requests

def send_http_request():
    try:
        params_for_http = {"message": "QR Code Generator is running"}
        http_pub = requests.get('https://southamerica-east1-qr-code-streamlit.cloudfunctions.net/telegram-nofication', params=params_for_http)
        http_telegram = requests.get("https://api.telegram.org/bot1950541172:AAH9IVUn_Q9y2Y1100ntNB7Zdbpp_1M_vAE/sendMessage?chat_id=1139072037&text=A new QR Code has been generated!")

    except Exception as error:
        print(f'Error: {error}')
        raise error
