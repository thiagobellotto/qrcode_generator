from functools import partial
import base64
import html
import datetime
import io
from urllib.parse import urlsplit

import segno
import streamlit as st
from segno import helpers

text_input = partial(st.text_input, persist_state="session")
selectbox = partial(st.selectbox, persist_state="session")
checkbox = partial(st.checkbox, persist_state="session")
date_input = partial(st.date_input, persist_state="session")

st.set_page_config(page_title="QR Code Generator", page_icon=":material/qr_code_2:", layout="wide")
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


def normalize_url(value: str) -> str:
    """Default scheme-less web addresses to HTTPS; preserve explicit schemes."""
    value = value.strip()
    if not value:
        return value
    if value.startswith("//"):
        return "https:" + value
    try:
        parsed = urlsplit(value)
        # urlsplit treats example.com:8080 as a scheme. Recognize host:port too.
        authority = urlsplit("//" + value)
        host_with_port = (
            authority.port is not None
            and bool(authority.hostname)
            and ("." in authority.hostname or authority.hostname == "localhost")
        )
        if not parsed.scheme or host_with_port:
            return "https://" + value
    except ValueError:
        pass
    return value


def valid_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return (parsed.scheme in {"http", "https"} and bool(parsed.hostname)
                and not any(c.isspace() or ord(c) < 32 for c in value))
    except ValueError:
        return False




def change_count(key: str, delta: int):
    count = st.session_state.get(key, 1)
    if delta < 0 and count > 1:
        st.session_state.pop(f"{key.removesuffix('_count')}_{count - 1}", None)
    st.session_state[key] = max(1, min(5, count + delta))


def multiple_inputs(label: str, prefix: str, placeholder: str) -> list[str]:
    """Explicit controls for multiple values, without delimiter conventions."""
    count_key = prefix + "_count"
    count = st.session_state.setdefault(count_key, 1)
    values = [text_input(label if i == 0 else f"{label} {i + 1}",
                            key=f"{prefix}_{i}", placeholder=placeholder).strip()
              for i in range(count)]
    with st.container(horizontal=True, gap="small"):
        st.button(f"Add another {label.lower()}", key=prefix + "_add",
                  on_click=change_count, args=(count_key, 1), disabled=count >= 5,
                  type="tertiary", icon=":material/add:")
        if count > 1:
            st.button(f"Remove last {label.lower()}", key=prefix + "_remove",
                      on_click=change_count, args=(count_key, -1), type="tertiary")
    return [value for value in values if value]


def clear_result():
    st.session_state.pop("result", None)


def reset_form(choice: str):
    prefix = {"Website link": "link_", "Wi-Fi network": "wifi_", "Contact card": "contact_"}[choice]
    for key in list(st.session_state):
        if key.startswith(prefix) or key in {"qr_border", "qr_size"}:
            del st.session_state[key]
    clear_result()


@st.dialog("Full-size QR code", width="large")
def show_full_size(png: bytes):
    st.image(png, width="content", alt="Full-size generated QR code")
    st.caption("Scan with another device. The image fits smaller screens.")


def wifi_print_card(ssid: str, png: bytes) -> str:
    """A standalone print document: escaped user text, embedded image, no scripts."""
    image = base64.b64encode(png).decode("ascii")
    name = html.escape(ssid)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wi-Fi card</title><style>
body {{font-family:system-ui,sans-serif;color:#24332f;background:white;margin:0;padding:24px;text-align:center}}
main {{max-width:140mm;margin:20px auto;padding:24px;border:1px solid #cad4cf;border-radius:12px}}
h1 {{font-size:28px}} h2 {{font-size:22px;overflow-wrap:anywhere;white-space:pre-wrap}}
img {{width:90mm;max-width:100%;height:auto;image-rendering:pixelated}}
p {{line-height:1.5}} .instructions {{color:#46584f}}
@media print {{body {{padding:0}} main {{break-inside:avoid}} .instructions {{display:none}}}}
@page {{margin:15mm}}
</style></head><body><p class="instructions">Use your browser’s Print command (Ctrl+P or ⌘P) to print or save as PDF.</p>
<main><h1>Welcome. Connect to Wi-Fi.</h1><h2>{name}</h2>
<img src="data:image/png;base64,{image}" alt="Wi-Fi connection QR code">
<p>Scan with your phone’s camera to connect.</p></main></body></html>'''


with st.container(horizontal=True, horizontal_alignment="center"):
    workspace = st.container(width=1100)

with workspace:
    st.title("QR Code Generator")
    st.caption("Create a code for a website, a Wi-Fi network, or a contact. Ready to share in seconds.")
    choice = st.segmented_control(
        "What would you like to share?", ["Website link", "Wi-Fi network", "Contact card"],
        default="Website link", required=True, key="qr_type", width="stretch",
    )
    if st.session_state.get("result_type") != choice:
        clear_result()
        st.session_state.result_type = choice

    details, preview = st.columns([1.25, 1], gap="medium", wrap=True)
    with details:
        with st.container(border=True, key="details"):
            st.subheader("Your details")
            st.caption("Required fields are marked *. Press Enter or leave a field to apply edits.")
            data = {}
            errors = {}
            if choice == "Website link":
                data["url"] = text_input("Website address *", key="link_url",
                    placeholder="google.com", help="No prefix needed — we add https:// automatically.").strip()
                errors["url"] = st.empty()
            elif choice == "Wi-Fi network":
                data["ssid"] = text_input("Network name *", key="wifi_ssid", placeholder="Your Wi-Fi name")
                errors["ssid"] = st.empty()
                data["security"] = selectbox("Security", ["WPA/WPA2", "WEP", "None (open network)"], key="wifi_security")
                is_open = data["security"] == "None (open network)"
                password = text_input("Password" if is_open else "Password *", type="password", key="wifi_password",
                                         disabled=is_open, help="Not required for open networks." if is_open else None)
                data["password"] = "" if is_open else password
                errors["password"] = st.empty()
                data["hidden"] = checkbox("Hidden network", key="wifi_hidden")
                st.caption("For personal Wi-Fi networks. Enterprise sign-in is not supported.")
            else:
                data["name"] = text_input("Display name *", key="contact_name", placeholder="Alex Morgan").strip()
                errors["name"] = st.empty()
                data["phone"] = text_input("Phone", key="contact_phone", placeholder="+1 555 123 4567").strip()
                data["emails"] = multiple_inputs("Email", "contact_email", "alex@example.com")
                with st.expander("Work & website"):
                    data["org"] = text_input("Company", key="contact_org").strip()
                    data["title"] = text_input("Job title", key="contact_title").strip()
                    data["urls"] = multiple_inputs("Website", "contact_url", "example.com")
                errors["urls"] = st.empty()
                with st.expander("Additional contact details"):
                    st.caption("Optional names control how the contact is sorted in an address book. "
                               "Otherwise, we use the display name without guessing a surname.")
                    data["given"] = text_input("Given name(s)", key="contact_given").strip()
                    data["family"] = text_input("Family name", key="contact_family").strip()
                    data["birthday"] = date_input("Birthday", value=None, key="contact_birthday",
                        min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())

            with st.expander("Appearance & size"):
                border = st.slider("White margin", 1, 8, 1, key="qr_border",
                    help="Margin in modules. Four or more is recommended for reliable scanning.")
                size = st.select_slider("PNG size", [512, 1024, 2048], value=1024, key="qr_size",
                    format_func=lambda value: f"Up to {value} × {value} px")
                st.caption("PNG uses whole QR modules for sharp edges. "
                           "SVG can be resized without losing quality.")
            snapshot = {"type": choice, "data": data, "border": border, "size": size}
            previous = st.session_state.get("result")
            current = previous is not None and previous["snapshot"] == snapshot
            submitted = st.button("Generate QR code", type="secondary" if current else "primary", width="stretch", icon=":material/qr_code_2:")
            st.button("Reset current form", type="tertiary", on_click=reset_form, args=(choice,),
                      help="Clear this type’s fields and generated code, and reset appearance settings.")
            if submitted:
                clear_result()
                qr = None
                summary = []
                filename = "qrcode"
                vcf = None
                print_card = None
                if choice == "Website link":
                    url = normalize_url(data["url"])
                    if not data["url"]:
                        errors["url"].error("Enter a website address to generate your code.")
                    elif not valid_url(url):
                        errors["url"].error("Check the website address. Use a domain such as google.com, without spaces.")
                    else:
                        qr = generate(segno.make_qr, content=url, error="m")
                        summary = [url]
                        filename = "link"
                elif choice == "Wi-Fi network":
                    if not data["ssid"]:
                        errors["ssid"].error("Enter the network name.")
                    elif not is_open and not data["password"]:
                        errors["password"].error("Enter the password, or choose an open network.")
                    else:
                        qr = generate(helpers.make_wifi, ssid=data["ssid"],
                            password=None if is_open else data["password"],
                            security=None if is_open else ("WPA" if data["security"] == "WPA/WPA2" else "WEP"),
                            hidden=data["hidden"])
                        summary = [data["ssid"], data["security"] + (" · Hidden network" if data["hidden"] else "")]
                        filename = "wifi"
                else:
                    urls = [normalize_url(value) for value in data["urls"]]
                    if not data["name"]:
                        errors["name"].error("Enter a display name for the contact.")
                    elif any(not valid_url(value) for value in urls):
                        errors["urls"].error("Check the website addresses under Work & website. Use domains without spaces.")
                    else:
                        contact_fields = dict(
                            name=vcard_name(data["given"] or data["name"], data["family"]),
                            displayname=data["name"], phone=data["phone"] or None,
                            email=data["emails"] or None, url=urls or None,
                            org=data["org"] or None, title=data["title"] or None, birthday=data["birthday"])
                        qr = generate(helpers.make_vcard, **contact_fields)
                        if qr is not None:
                            vcf = helpers.make_vcard_data(**contact_fields).encode("utf-8")
                        summary = [data["name"], data["phone"], *data["emails"], data["org"], *urls]
                        filename = "contact"
                if qr is not None:
                    modules = qr.symbol_size(scale=1, border=border)[0]
                    scale = max(1, size // modules)
                    svg_buffer = io.BytesIO()
                    qr.save(svg_buffer, kind="svg", border=border, scale=1, light="white")
                    if choice == "Wi-Fi network":
                        # Printed cards use the standard quiet zone even when preview margin is compact.
                        print_card = wifi_print_card(data["ssid"], to_png(qr, border=max(4, border), scale=12))
                    st.session_state.result = {
                        "png": to_png(qr, border=border, scale=scale), "svg": svg_buffer.getvalue(),
                        "snapshot": snapshot, "summary": [line for line in summary if line],
                        "filename": filename, "pixels": modules * scale, "vcf": vcf, "print_card": print_card,
                    }
                    st.rerun()

    with preview:
        with st.container(border=True, key="preview"):
            st.subheader("Your QR code")
            result = st.session_state.get("result")
            if result is None:
                st.markdown("**Your QR code will appear here.**")
                st.caption("Enter your details, then choose Generate QR code. Download as PNG for sharing or SVG for printing.")
            else:
                stale = result["snapshot"] != snapshot
                if stale:
                    st.warning("Details changed — generate again to update your QR code.")
                    st.caption("The preview below shows your previous code. Downloads are paused until you regenerate.")
                st.image(result["png"], width=320, alt="Generated QR code; its content summary is shown below.")
                label = {"Website link": "Destination", "Wi-Fi network": "Network", "Contact card": "Contact"}[choice]
                st.caption(label if not stale else f"Previous {label.lower()}")
                if choice == "Contact card":
                    st.text(result["summary"][0])
                    fields = result["snapshot"]["data"]
                    st.caption(f"{len(fields['emails'])} email(s) · {len(fields['urls'])} website(s)"
                               + (" · Phone included" if fields["phone"] else ""))
                    with st.expander("View encoded details"):
                        for line in result["summary"][1:]:
                            st.text(line)
                        if fields["title"]:
                            st.text(fields["title"])
                        if fields["given"] or fields["family"]:
                            st.text(f"Given name: {fields['given'] or fields['name']} · Family name: {fields['family']}")
                        if fields["birthday"]:
                            st.text(f"Birthday: {fields['birthday'].isoformat()}")
                else:
                    for line in result["summary"]:
                        st.text(line)
                png_download, svg_download = st.columns(2, gap="small")
                with png_download:
                    st.download_button("Download PNG", data=result["png"],
                        file_name=result["filename"] + ".png", mime="image/png", type="secondary" if stale else "primary",
                        on_click="ignore", disabled=stale, width="stretch",
                        help="Best for sharing, documents, and everyday use.")
                with svg_download:
                    st.download_button("Download SVG", data=result["svg"],
                        file_name=result["filename"] + ".svg", mime="image/svg+xml",
                        on_click="ignore", disabled=stale, width="stretch",
                        help="Best for printing and resizing without losing quality.")
                with st.expander("More options"):
                    if st.button("View full-size QR", disabled=stale, width="stretch"):
                        show_full_size(result["png"])
                    if result.get("vcf") is not None:
                        st.download_button("Save contact (.vcf)", data=result["vcf"], file_name="contact.vcf",
                            mime="text/vcard", on_click="ignore", disabled=stale, width="stretch")
                    if result.get("print_card") is not None:
                        st.download_button("Download printable Wi-Fi card", data=result["print_card"],
                            file_name="wifi-card.html", mime="text/html", on_click="ignore", disabled=stale,
                            width="stretch", help="Open the downloaded file in your browser and print. Uses a print-safe white margin.")
                if choice == "Wi-Fi network":
                    st.caption("Anyone with this QR code can read its Wi-Fi credentials.")
                st.button("Clear generated code", on_click=clear_result, type="tertiary")

    st.divider()
    st.caption("Made by [Thiago Bellotto](https://thiagobellotto.com) · "
               "[LinkedIn](https://www.linkedin.com/in/thiago-bellotto/) · "
               "[GitHub](https://github.com/thiagobellotto)")

