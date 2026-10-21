# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "segno==1.6.6",
#     "streamlit==1.66.0",
# ]
# ///

import datetime
import io

import segno
import streamlit as st
from segno import helpers

## Main settings from page
st.set_page_config(layout="centered", page_title="QR Code")
st.title("QR Code Generator")
st.subheader("Choose the type, fill in your details, and click 'Generate QR Code'.")

footer = """<style>
.footer a:link, .footer a:visited {
    color: inherit;
    background-color: transparent;
    text-decoration: underline;
}
.footer a:hover, .footer a:active {
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
    text-align: center;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
<div class="footer">
<p>Developed with ❤ by <a href="https://www.linkedin.com/in/thiago-bellotto/" target="_blank">Thiago Bellotto</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)

## Sidebar for QR Code Type Selection
QR_TYPES = ("Links/URLs", "WiFi", "Business Card")
choice = st.sidebar.radio("Select QR Code type:", QR_TYPES)

st.sidebar.subheader("About the app")
st.sidebar.info(
    "Developed by Thiago Bellotto to generate QR Codes for business cards, "
    "WiFi passwords, or links. Built with Streamlit."
)
st.sidebar.markdown(
    "Find me on [Website](https://thiagobellotto.com), "
    "[LinkedIn](https://www.linkedin.com/in/thiago-bellotto/), "
    "or [GitHub](https://github.com/thiagobellotto)."
)


def split_values(raw: str) -> list[str] | None:
    """Split a ';'-separated field, dropping blanks. Returns None if empty."""
    values = [v.strip() for v in raw.split(";") if v.strip()]
    return values or None


def vcard_name(full_name: str) -> str:
    """Convert 'First Middle Last' into the vCard 'Last;First Middle' format."""
    parts = full_name.split()
    if len(parts) < 2:
        return full_name
    return f"{parts[-1]};{' '.join(parts[:-1])}"


def to_png(qr: segno.QRCode, border: int, scale: int) -> bytes:
    """Render the QR code to PNG bytes in memory (no files on disk)."""
    buffer = io.BytesIO()
    qr.save(buffer, kind="png", border=border, scale=scale)
    return buffer.getvalue()


qr = None
file_name = "qrcode.png"

if choice == "Business Card":
    with st.form("VCard"):
        name = st.text_input("Full name *")
        phone = st.text_input("Telephone - Recommended format: +5511999999999")
        email = st.text_input('Email - For more than one, use ";"')
        url = st.text_input('URL - For more than one, use ";"')
        org = st.text_input("Company")
        title = st.text_input("Title")
        birthday = st.date_input(
            "Birth Date (optional)",
            value=None,
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
        )
        border = st.slider("Border Size", min_value=1, max_value=5, value=2)
        scale = st.slider("QR Code Size", min_value=5, max_value=10, value=6)
        submitted = st.form_submit_button("Generate QR Code")

    if submitted:
        if not name.strip():
            st.error("Please provide a name.")
        else:
            qr = helpers.make_vcard(
                name=vcard_name(name.strip()),
                displayname=name.strip(),
                phone=phone.strip() or None,
                email=split_values(email),
                url=split_values(url),
                org=org.strip() or None,
                title=title.strip() or None,
                birthday=birthday,
            )
            file_name = "vcard.png"

elif choice == "WiFi":
    with st.form("WiFi"):
        ssid = st.text_input("WiFi Name *")
        password = st.text_input("Password", type="password")
        security = st.radio("Security", ("WPA2 (Standard)", "WPA", "WEP", "None"))
        hidden = st.checkbox("Hidden network")
        border = st.slider("Border Size", min_value=1, max_value=5, value=2)
        scale = st.slider("QR Code Size", min_value=10, max_value=15, value=10)
        submitted = st.form_submit_button("Generate QR Code")

    if submitted:
        is_open = security == "None"
        if not ssid:
            st.error("Please provide the WiFi name.")
        elif not is_open and not password:
            st.error("Please provide the password, or choose 'None' as security.")
        else:
            qr = helpers.make_wifi(
                ssid=ssid,
                password=None if is_open else password,
                security=None if is_open else security.replace(" (Standard)", ""),
                hidden=hidden,
            )
            file_name = "wifi.png"

elif choice == "Links/URLs":
    with st.form("Link"):
        url = st.text_input("Link/URL *")
        border = st.slider("Border Size", min_value=1, max_value=5, value=2)
        scale = st.slider("QR Code Size", min_value=10, max_value=15, value=10)
        submitted = st.form_submit_button("Generate QR Code")

    if submitted:
        if not url.strip():
            st.error("Please provide a link.")
        else:
            qr = segno.make(url.strip(), error="m")
            file_name = "link.png"

## Display and Download QR Code after form submission
if qr is not None:
    png = to_png(qr, border=border, scale=scale)
    st.image(png, caption="Preview QR Code")
    st.download_button(
        "Download QR Code",
        data=png,
        file_name=file_name,
        mime="image/png",
    )
