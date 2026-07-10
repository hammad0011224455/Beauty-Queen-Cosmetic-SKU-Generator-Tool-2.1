import streamlit as st
import pandas as pd

from sku_generator import generate_sku

st.set_page_config(
    page_title="Beauty Queens SKU Generator",
    layout="wide"
)

st.title("SKU Generator")

uploaded_file = st.file_uploader(
    "Upload Shopify CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    if "Title" in df.columns:
        df["Title"] = df["Title"].ffill()

    if "Vendor" in df.columns:
        df["Vendor"] = df["Vendor"].ffill()

    used_numbers = set()
    generated_skus = []

    progress = st.progress(0)

    for i, row in df.iterrows():

        sku = generate_sku(
            title=str(row["Title"]),
            vendor=str(row["Vendor"]),
            used_numbers=used_numbers
        )

        generated_skus.append(sku)

        progress.progress((i + 1) / len(df))

    df["Generated SKU"] = generated_skus

    st.success(f"{len(df)} SKUs Generated")

    st.dataframe(
        df[
            ["Title", "Vendor", "Generated SKU"]
        ],
        use_container_width=True
    )

    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode(),
        "sku_output.csv",
        "text/csv"
    )