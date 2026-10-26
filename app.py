import datetime
import io
from urllib.parse import urlsplit

import segno
import streamlit as st
from segno import helpers

## Main settings from page
st.set_page_config(layout="centered", page_title="QR Code", page_icon="🔳")
st.title("QR Code Generator")
st.caption("Choose a type, fill in your details, and generate a QR code.")

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


def vcard_name(given_name: str, family_name: str) -> str:
    """Escape components separately; Segno intentionally leaves N unescaped."""
    def escape(value):
        return (value.strip().replace("\\", "\\\\").replace(";", "\\;")
                .replace(",", "\\,").replace("\r\n", "\n")
                .replace("\r", "\n").replace("\n", "\\n"))
    return f"{escape(family_name)};{escape(given_name)};;;"


def to_png(qr: segno.QRCode, border: int, scale: int) -> bytes:
    """Render the QR code to PNG bytes in memory (no files on disk)."""
    buffer = io.BytesIO()
    qr.save(buffer, kind="png", border=border, scale=scale)
    return buffer.getvalue()


def generate(factory, **kwargs):
    """Handle expected invalid/oversized payloads without exposing user data."""
    try:
        return factory(**kwargs)
    except segno.DataOverflowError:
        st.error("Too much information for one QR code. Shorten the fields and try again.")
    except ValueError:
        st.error("These details could not be encoded. Check the fields and try again.")
    return None


def valid_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return (parsed.scheme in {"http", "https"} and bool(parsed.hostname)
                and not any(c.isspace() or ord(c) < 32 for c in value))
    except ValueError:
        return False


# Results are private to this session; never globally cache contact/Wi-Fi data.
if st.session_state.get("result_type") != choice:
    st.session_state.pop("result", None)
    st.session_state.result_type = choice

qr = None
file_name = "qrcode.png"

if choice == "Business Card":
    with st.form("VCard"):
        name = st.text_input("Full name / display name *")
        given_name = st.text_input("Given name(s) (optional)")
        family_name = st.text_input("Family name (optional)")
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
        border = st.slider("Border Size", min_value=4, max_value=8, value=4, help="White margin in modules; at least four keeps standard QR codes scannable.")
        scale = st.slider("QR Code Size", min_value=5, max_value=10, value=6)
        submitted = st.form_submit_button("Generate QR Code", type="primary", width="stretch")

    if submitted:
        st.session_state.pop("result", None)
        if not name.strip():
            st.error("Please provide a name.")
        else:
            qr = generate(helpers.make_vcard,
                name=vcard_name(given_name.strip() or name, family_name),
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
        security = st.radio("Security", ("WPA/WPA2", "WEP", "None"))
        hidden = st.checkbox("Hidden network")
        border = st.slider("Border Size", min_value=4, max_value=8, value=4, help="White margin in modules; at least four keeps standard QR codes scannable.")
        scale = st.slider("QR Code Size", min_value=10, max_value=15, value=10)
        submitted = st.form_submit_button("Generate QR Code", type="primary", width="stretch")

    if submitted:
        st.session_state.pop("result", None)
        is_open = security == "None"
        if not ssid:
            st.error("Please provide the WiFi name.")
        elif not is_open and not password:
            st.error("Please provide the password, or choose 'None' as security.")
        else:
            qr = generate(helpers.make_wifi,
                ssid=ssid,
                password=None if is_open else password,
                security=None if is_open else ("WPA" if security == "WPA/WPA2" else "WEP"),
                hidden=hidden,
            )
            file_name = "wifi.png"

elif choice == "Links/URLs":
    with st.form("Link"):
        url = st.text_input("Link/URL *", placeholder="https://example.com")
        border = st.slider("Border Size", min_value=4, max_value=8, value=4, help="White margin in modules; at least four keeps standard QR codes scannable.")
        scale = st.slider("QR Code Size", min_value=10, max_value=15, value=10)
        submitted = st.form_submit_button("Generate QR Code", type="primary", width="stretch")

    if submitted:
        st.session_state.pop("result", None)
        if not url.strip():
            st.error("Please provide a link.")
        elif not valid_url(url.strip()):
            st.error("Enter a complete http:// or https:// URL, without spaces.")
        else:
            qr = generate(segno.make_qr, content=url.strip(), error="m")
            file_name = "link.png"

# Keep the last submitted result through reruns and download without a rerun.
if qr is not None:
    svg_buffer = io.BytesIO()
    qr.save(svg_buffer, kind="svg", border=border, scale=scale, light="white")
    st.session_state.result = {
        "png": to_png(qr, border=border, scale=scale),
        "svg": svg_buffer.getvalue(),
        "file_name": file_name,
    }

result = st.session_state.get("result")
if result:
    st.image(result["png"], caption="Last generated QR code — submit again after editing.")
    png_column, svg_column = st.columns(2)
    with png_column:
        st.download_button("Download PNG", data=result["png"],
                           file_name=result["file_name"], mime="image/png",
                           on_click="ignore", width="stretch")
    with svg_column:
        st.download_button("Download SVG", data=result["svg"],
                           file_name=result["file_name"].replace(".png", ".svg"),
                           mime="image/svg+xml", on_click="ignore", width="stretch")
    st.caption("Scan-test before sharing or printing. SVG stays sharp at any size.")
    if choice == "WiFi":
        st.warning("Anyone with this QR code can read the Wi-Fi password.")
    if st.button("Clear generated code"):
        st.session_state.pop("result", None)
        st.rerun()

st.divider()
st.caption("Details are processed on the app server. This app does not save them to disk "
           "or send them to a QR-code service.")
st.caption("Developed with ❤ by [Thiago Bellotto](https://www.linkedin.com/in/thiago-bellotto/)")
