#!/usr/bin/env python
# coding: utf-8

from segno import helpers
import segno
import pandas as pd
import datetime
from unidecode import unidecode
import streamlit as st
from gsheetsdb import connect

# Create a connection object.
conn = connect()

@st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows

sheet_url = st.secrets["DB_URL"]
# rows = run_query(f'SELECT * FROM "Links"')

st.set_page_config(layout="centered", page_title='QR Code')
st.title('Gerador de QR Code')
st.subheader('''
        A ferramenta permite gerar QR Code para utilização em WiFi e cartões de visita. Preencha as informações abaixo e clique em "Gerar" para gerar o QRCode. Ajuste as bordas e tamanho, e então salve o arquivo. As informações que não foram aplicáveis, serão ignoradas.
''')

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

card_visita, card_wifi, card_link = 'QR Code para cartão de visita', 'QR Code para WiFi', 'QR Code para links'

choice = st.radio('Escolha o tipo de QR Code', (card_link, card_wifi, card_visita), index=0)

if choice == card_visita:
        with st.form('VCard'):
                name = st.text_input('Nome', ' ')
                displayname = st.text_input('Nome para display', '')
                nickname = st.text_input('Apelido', ' ')
                phone = st.text_input('Telefone - Formato recomendado: +55 11 999999999', '')
                email = st.text_input('Email (Para adicionar mais de um, separe-os por vírgula)', ' ')
                url = st.text_input('URL (Para adicionar mais de um, separe-os por vírgula)', ' ')
                city = st.text_input('Cidade', ' ')
                country = st.text_input('País', ' ')
                org = st.text_input('Organização', ' ')
                title = st.text_input('Título', ' ')
                birthday = st.date_input('Data de nascimento', None, min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
                border = st.slider(label='Selecione o tamanho da borda', min_value=1, max_value=5)
                scale = st.slider(label='Selecione o tamanho do QR Code', min_value=5, max_value=10)
                submitted = st.form_submit_button('Gerar QR Code')
elif choice == card_wifi:
        with st.form('WiFi'):
                ssid = st.text_input('Nome do Wifi', ' ')
                password = st.text_input('Senha', ' ')
                security = st.radio('Tipo de segurança', ('WPA2 (Padrão)', 'WPA', 'Nenhuma'))
                border = st.slider(label='Selecione o tamanho da borda', min_value=1, max_value=5)
                scale = st.slider(label='Selecione o tamanho do QR Code', min_value=10, max_value=15)
                submitted = st.form_submit_button('Gerar QR Code')
elif choice == card_link:
        with st.form('Link'):
                url = st.text_input('Link', ' ')
                border = st.slider(label='Selecione o tamanho da borda', min_value=1, max_value=5)
                scale = st.slider(label='Selecione o tamanho do QR Code', min_value=10, max_value=15)
                submitted = st.form_submit_button('Gerar QR Code')
else:
        pass

if submitted:
        if choice == card_visita:
                ## Deal with birthday date, if empty
                if birthday == datetime.date.today():
                        birthday = None

                ## Deal with punctuation
                city = unidecode(city)
                city = unidecode(country)
                name = unidecode(name)

                qr = helpers.make_vcard(
                        name=name,
                        displayname=displayname,
                        nickname=nickname,
                        phone=phone,
                        email=[i for i in email.split(',')],
                        url=[i for i in url.split(',')],
                        city=city,
                        country=country,
                        org=org,
                        title=title,
                        birthday=birthday,
                        )
                
                qr_img = qr.save(out='vcard.png', border=border, scale=scale)
                with open('vcard.png', 'rb') as f:
                        bytes_qr = f.read()

                        st.write('Preview do QR Code')
                        st.image(bytes_qr, caption='Caso queira salvar, clique no botão abaixo')
                        st.download_button(label="Download QR Code", data=bytes_qr, file_name="vcard.png", mime="image/png")
        elif choice == card_wifi:
                if security == 'WPA2 (Padrão)':
                        security = 'WPA2'
                wifi = helpers.make_wifi(ssid=ssid,
                                        password=password,
                                        security=security)
                
                wifi_img = wifi.save(out='wifi.png', border=border, scale=scale)
                with open('wifi.png', 'rb') as f:
                        bytes_wifi = f.read()

                        st.write('Preview do QR Code')
                        st.image(bytes_wifi, caption='Caso queira salvar, clique no botão abaixo')
                        st.download_button(label="Download QR Code", data=bytes_wifi, file_name="wifi.png", mime="image/png")

        elif choice == card_link:
                link = segno.make(url)

                link_img = link.save(out='link.png', border=border, scale=scale)
                with open('link.png', 'rb') as f:
                        bytes_link = f.read()

                        st.write('Preview do QR Code')
                        st.image(bytes_link, caption='Caso queira salvar, clique no botão abaixo')
                        st.download_button(label="Download QR Code", data=bytes_link, file_name="link.png", mime="image/png", on_click='Obrigado por usar o QR Code Generator!')
        else:
                pass