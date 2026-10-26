# QR Code Generator

A Streamlit app for website links, Wi-Fi networks, and vCard contact cards, with
PNG downloads and scalable SVG exports. QR codes are generated in memory using
Segno; no external QR service is called.

## Run locally with uv

Use Python 3.12 to match the recommended Community Cloud deployment:

```bash
uv sync --locked --python 3.12
uv run streamlit run app.py
```

Dependencies live in `pyproject.toml`, with exact resolved versions in `uv.lock`.
After intentionally changing dependencies, run `uv lock` and commit both files.
The old inline script metadata has been removed to avoid two sources of truth.

## Privacy

Streamlit processes submitted details on the server. This app does not write them
to disk, log them, globally cache them, or send them to an external QR service.
Generated files are retained in the current Streamlit session and served for
download. QR codes are **not encryption**: anyone with a Wi-Fi/contact QR can
recover its contents. Hosting-platform retention policies are separate.
