#!/usr/bin/env python
# coding: utf-8

## QR Code library
from segno import helpers
import segno

## Create datetime and handle punctuation
import datetime
from unidecode import unidecode
import json

## Streamlit
import streamlit as st

## Import google cloud authentication and functions
from google.oauth2 import service_account
from googleapiclient.discovery import build
from g_connect import connect_to_gsheet, add_row_to_gsheet

## Main settings from page
st.set_page_config(layout="centered", page_title='QR Code')
st.title('QR Code Generator')
# st.subheader('''
#         A ferramenta permite gerar QR Code para utilização em Links, Wifis e cartões de visita. Preencha as informações abaixo e clique em "Gerar QRCode".
# ''')

footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}
a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: transparent;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: block; color: white; text-align: center;' href="https://www.linkedin.com/in/thiago-bellotto/" target="_blank">Thiago Bellotto</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

card_visita, card_wifi, card_link = 'Business Card', 'WiFi', 'Links/URLs'

choice = st.radio('Select the type of QR Code:', (card_link, card_wifi, card_visita), index=0)

if choice == card_visita:
        with st.form('VCard'):
                name = st.text_input('Name', '')
                phone = st.text_input('Telephone - Recommended: +5511999999999', '')
                email = st.text_input('Email - For more than one, use ";" ', '')
                url = st.text_input('URL - For more than one, use ";" ', '')
                org = st.text_input('Company', '')
                title = st.text_input('Title', '')
                birthday = st.date_input('Birth Date - In case of omission, keep the default date', None, min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
                border = st.slider(label='Border Size', min_value=1, max_value=5)
                scale = st.slider(label='QR Code Size', min_value=5, max_value=10)
                submitted = st.form_submit_button('Generate QR Code')
elif choice == card_wifi:
        with st.form('WiFi'):
                ssid = st.text_input('Wifi Name', '')
                password = st.text_input('Password', '')
                security = st.radio('Security', ('WPA2 (Standard)', 'WPA', 'None'))
                border = st.slider(label='Border Size', min_value=1, max_value=5)
                scale = st.slider(label='QR Code Size', min_value=10, max_value=15)
                submitted = st.form_submit_button('Generate QR Code')
elif choice == card_link:
        with st.form('Link'):
                url = st.text_input('Links/URLs', '')
                border = st.slider(label='Border Size', min_value=1, max_value=5)
                scale = st.slider(label='QR Code Size', min_value=10, max_value=15)
                submitted = st.form_submit_button('Generate QR Code')
else:
        pass

if submitted:
        if choice == card_visita:
                ## Deal with birthday date, if empty
                if birthday == datetime.date.today():
                        birthday = None

                ## Deal with punctuation
                name = unidecode(name)

                try:
                        with open('qr_code.json', 'r') as f:
                                qr_json = json.load(f)
                        
                        sheet_name = "VCard"
                        gsheet_connector = connect_to_gsheet(qr_json)
                        add_row_to_gsheet(gsheet_connector, sheet_name, 
                                        [[name, phone, email, url, org, 
                                        title, str(birthday), border, scale, str(datetime.date.today())]])
                except Exception as e:
                        print('Error:', e)
                finally:
                        qr = helpers.make_vcard(
                                name=name,
                                displayname=name,
                                phone=phone,
                                email=[i for i in email.split(';')],
                                url=[i for i in url.split(';')],
                                org=org,
                                title=title,
                                birthday=birthday,
                                )
                        
                        qr_img = qr.save(out='vcard.png', border=border, scale=scale)
                        with open('vcard.png', 'rb') as f:
                                bytes_qr = f.read()

                                st.write('Preview QR Code')
                                st.image(bytes_qr)
                                st.download_button(label="Download QR Code", data=bytes_qr, file_name="vcard.png", mime="image/png")
        elif choice == card_wifi:
                try:
                        with open('qr_code.json', 'r') as f:
                                qr_json = json.load(f)
                                
                        sheet_name = "Wifi"
                        gsheet_connector = connect_to_gsheet(qr_json)
                        add_row_to_gsheet(gsheet_connector, sheet_name, 
                                        [[ssid, password, security, border, scale, str(datetime.date.today())]])
                except Exception as e:
                        print('Error:', e)
                finally:
                        if security == 'WPA2 (Standard)':
                                security = 'WPA2'
                        wifi = helpers.make_wifi(ssid=ssid,
                                                password=password,
                                                security=security)
                        
                        wifi_img = wifi.save(out='wifi.png', border=border, scale=scale)
                        with open('wifi.png', 'rb') as f:
                                bytes_wifi = f.read()

                                st.write('Preview QR Code')
                                st.image(bytes_wifi)
                                st.download_button(label="Download QR Code", data=bytes_wifi, file_name="wifi.png", mime="image/png")

        elif choice == card_link:

                try:
                        with open('qr_code.json', 'r') as f:
                                qr_json = json.load(f)
                                
                        sheet_name = "Links"
                        gsheet_connector = connect_to_gsheet(qr_json)
                        add_row_to_gsheet(gsheet_connector, sheet_name, [[url, border, scale, str(datetime.date.today())]])
                except Exception as e:
                        print('Error:', e)
                finally:

                        link = segno.make(url)

                        link_img = link.save(out='link.png', border=border, scale=scale)
                        with open('link.png', 'rb') as f:
                                bytes_link = f.read()

                                st.write('Preview QR Code')
                                st.image(bytes_link)
                                st.download_button(label="Download QR Code", data=bytes_link, file_name="link.png", mime="image/png")
        else:
                pass
