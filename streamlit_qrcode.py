#!/usr/bin/env python
# coding: utf-8

from segno import helpers
import streamlit as st

st.set_page_config(layout="centered", page_icon='🐍')
st.title('Gerador de Cards em QRCode')

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

with st.form('VCard'):
        name = st.text_input('Nome', ' ')
        displayname = st.text_input('Nome para display', ' ')
        nickname = st.text_input('Apelido', ' ')
        phone = st.text_input('Telefone - Formato recomendado: +55 DD 999999999', '')
        email = st.text_input('Email', ' ')
        url = st.text_input('URL', ' ')
        city = st.text_input('Cidade', ' ')
        country = st.text_input('País', ' ')
        org = st.text_input('Organização', ' ')
        title = st.text_input('Título', ' ')
        
        border = st.slider(label='Selecione o tamanho da borda', min_value=1, max_value=5)
        scale = st.slider(label='Selecione o tamanho do QR Code', min_value=5, max_value=10)
        submitted1 = st.form_submit_button('Gerar QR Code')

if submitted1:
        qr = helpers.make_vcard(
                name=name,
                displayname=displayname,
                nickname=nickname,
                phone=phone,
                email=email,
                url=url,
                city=city,
                country=country,
                org=org,
                title=title,
        )
        
        qr_img = qr.save(out='vcard.png', border=border, scale=scale)
        with open('vcard.png', 'rb') as f:
                bytes = f.read()
                st.download_button(label="Download QR_Code", data=bytes, file_name="vcard.png", mime="image/png")
