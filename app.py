import streamlit as st
import pandas as pd

from sku_generator import (
    BRAND_CODES,
    SUBBRANDS,
    SUBBRAND_CODES,
    add_brand,
    add_subbrand,
    generate_sku,
    generate_unique_number,
    make_subbrand_code,
)

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Beauty Queens SKU Generator",
    page_icon="🏷️",
    layout="wide"
)

# ----------------------------------
# CUSTOM CSS
# ----------------------------------
st.markdown("""
<style>

.main {
    background-color: #f8f9fb;
}

.hero {
    background: white;
    padding: 30px;
    border-radius: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 3px 15px rgba(0,0,0,0.07);
    text-align:center;
}

.footer {
    text-align:center;
    color:#777;
    margin-top:30px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------
# SIDEBAR — ADD BRAND / SUB BRAND
# ----------------------------------
with st.sidebar:

    st.header("➕ Add Brand / Sub Brand")

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

        st.subheader("New Sub Brand")

        s_brand = st.text_input("Belongs to brand")
        s_name = st.text_input("Sub brand name")
        s_code = st.text_input("Sub brand code (optional, 3 chars)")

        if st.form_submit_button("Add Sub Brand"):

            if s_brand.strip() and s_name.strip():
                code = add_subbrand(s_brand, s_name, s_code or None)
                st.success(f"{s_name.upper()} → {code}")
            else:
                st.error("Brand and sub brand required")

    with st.expander(f"Brands ({len(BRAND_CODES)})"):
        st.json(BRAND_CODES)

    with st.expander(f"Sub Brands ({len(SUBBRAND_CODES)})"):
        st.json(SUBBRAND_CODES)

# ----------------------------------
# HEADER
# ----------------------------------
st.markdown("""
<div class="hero">
    <h1>🏷️ Beauty Queens SKU Generator</h1>
    <p>
        Generate Shopify-ready SKUs using Brand Codes,
        Sub Brand Detection and Unique Numbers.
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# METRICS
# ----------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>✓</h3>
        <h4>Unique SKUs</h4>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>⚡</h3>
        <h4>Fast Processing</h4>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>🛒</h3>
        <h4>Shopify Ready</h4>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------
# SKU MODE
# ----------------------------------
st.markdown("## SKU Configuration")

mode = st.radio(
    "Generation Mode",
    [
        "Auto Detect",
        "Manual Brand Selection"
    ],
    horizontal=True
)

selected_brand = None
selected_subbrand = None

if mode == "Manual Brand Selection":

    brand_options = sorted(SUBBRANDS.keys())

    if not brand_options:

        st.warning(
            "No brands available yet. Add one from the sidebar."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            selected_brand = st.selectbox(
                "Select Brand",
                brand_options
            )

        with col2:

            selected_subbrand = st.selectbox(
                "Select Sub Brand",
                SUBBRANDS.get(
                    selected_brand,
                    []
                )
            )

        if selected_subbrand:

            st.success(
                f"Selected Brand: {selected_brand} | Selected Sub Brand: {selected_subbrand}"
            )

        else:

            st.warning(
                f"{selected_brand} has no sub brands yet. Add one from the sidebar."
            )

# ----------------------------------
# FILE UPLOAD
# ----------------------------------
st.markdown("## Upload Shopify CSV")

uploaded_file = st.file_uploader(
    "Choose CSV File",
    type=["csv"]
)

# ----------------------------------
# PROCESS CSV
# ----------------------------------
if uploaded_file:

    try:

        try:
            df = pd.read_csv(uploaded_file)
        except Exception:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file,
                encoding="latin1"
            )

        st.success("CSV uploaded successfully")

        st.markdown("### CSV Preview")

        st.dataframe(
            df.head(),
            width="stretch"
        )

        title_col = st.selectbox(
            "Product Title Column",
            df.columns
        )

        vendor_col = st.selectbox(
            "Vendor Column",
            df.columns
        )

        if st.button("🚀 Generate SKUs"):

            progress = st.progress(0)

            used_numbers = set()
            generated_skus = []

            total = len(df)

            for i, (_, row_data) in enumerate(df.iterrows()):

                if mode == "Manual Brand Selection":

                    brand_code = BRAND_CODES.get(
                        str(selected_brand).upper(),
                        str(selected_brand)[:3].upper()
                    )

                    subbrand_code = SUBBRAND_CODES.get(
                        str(selected_subbrand).upper().strip(),
                        make_subbrand_code(selected_subbrand) or "GEN"
                    )

                    random_number = generate_unique_number(
                        used_numbers
                    )

                    sku = (
                        f"{brand_code}-"
                        f"{subbrand_code}-"
                        f"{random_number}"
                    )

                else:

                    sku = generate_sku(
                        title=row_data[title_col],
                        vendor=row_data[vendor_col],
                        used_numbers=used_numbers
                    )

                generated_skus.append(sku)

                progress.progress(
                    (i + 1) / total
                )

            df["Generated SKU"] = generated_skus

            st.success(
                f"{len(df)} SKUs Generated Successfully"
            )

            st.markdown("### Generated Results")

            st.dataframe(
                df,
                width="stretch"
            )

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇ Download Generated CSV",
                data=csv,
                file_name="generated_skus.csv",
                mime="text/csv"
            )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )

# ----------------------------------
# FOOTER
# ----------------------------------
st.markdown("""
<div class="footer">
Built with Streamlit • Beauty Queens Cosmetics
</div>
""", unsafe_allow_html=True)