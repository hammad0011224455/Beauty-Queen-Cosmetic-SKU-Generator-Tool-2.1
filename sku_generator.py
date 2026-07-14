import pandas as pd
import streamlit as st

from sku_generator import (
    BRAND_CODES,
    SUBBRANDS,
    SUBBRAND_CODES,
    add_brand,
    add_subbrand,
    generate_sku,
)

st.set_page_config(page_title="Beauty Queens SKU Generator", layout="wide")

st.title("SKU Generator")

# ---------- manual brand / subbrand entry ----------
with st.sidebar:
    st.header("Add Brand / Sub-brand")

    with st.form("add_brand_form", clear_on_submit=True):
        st.subheader("New Brand")
        b_name = st.text_input("Brand name")
        b_code = st.text_input("Brand code (optional, 3 chars)")
        if st.form_submit_button("Add Brand"):
            if b_name.strip():
                code = add_brand(b_name, b_code or None)
                st.success(f"{b_name.upper()} → {code}")
            else:
                st.error("Brand name required")

    with st.form("add_subbrand_form", clear_on_submit=True):
        st.subheader("New Sub-brand")
        s_brand = st.text_input("Belongs to brand")
        s_name = st.text_input("Sub-brand name")
        s_code = st.text_input("Sub-brand code (optional, 3 chars)")
        if st.form_submit_button("Add Sub-brand"):
            if s_brand.strip() and s_name.strip():
                code = add_subbrand(s_brand, s_name, s_code or None)
                st.success(f"{s_name.upper()} → {code}")
            else:
                st.error("Brand and sub-brand required")

    with st.expander(f"Brands ({len(BRAND_CODES)})"):
        st.json(BRAND_CODES)
    with st.expander(f"Sub-brands ({len(SUBBRAND_CODES)})"):
        st.json(SUBBRAND_CODES)

# ---------- CSV processing ----------
uploaded_file = st.file_uploader("Upload Shopify CSV", type=["csv"])

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
            used_numbers=used_numbers,
        )
        generated_skus.append(sku)
        progress.progress((i + 1) / len(df))

    df["Generated SKU"] = generated_skus

    st.success(f"{len(df)} SKUs Generated")
    st.dataframe(df[["Title", "Vendor", "Generated SKU"]], use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode(),
        "sku_output.csv",
        "text/csv",
    )