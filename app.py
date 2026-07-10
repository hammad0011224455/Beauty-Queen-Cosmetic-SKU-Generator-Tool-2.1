import streamlit as st
import pandas as pd
import json
import re
import random

from sku_generator import generate_sku

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Beauty Queens SKU Generator",
    page_icon="🏷️",
    layout="wide"
)

# ----------------------------------
# LOAD JSON FILES
# ----------------------------------
with open("brand_codes.json", "r", encoding="utf-8") as f:
    BRAND_CODES = json.load(f)

with open("Subbrands.json", "r", encoding="utf-8") as f:
    SUBBRANDS = json.load(f)

# ----------------------------------
# HELPERS
# ----------------------------------
def create_subbrand_code(name):

    words = re.findall(
        r"[A-Za-z0-9]+",
        str(name).upper()
    )

    if not words:
        return "GEN"

    if len(words) >= 2:
        return (
            words[0][:2] +
            words[1][:1]
        )[:3]

    return words[0][:3]


def generate_unique_number(used_numbers):

    while True:

        number = random.randint(
            1000,
            9999
        )

        if number not in used_numbers:

            used_numbers.add(number)

            return str(number)

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

    col1, col2 = st.columns(2)

    with col1:

        selected_brand = st.selectbox(
            "Select Brand",
            sorted(SUBBRANDS.keys())
        )

    with col2:

        selected_subbrand = st.selectbox(
            "Select Sub Brand",
            SUBBRANDS.get(
                selected_brand,
                []
            )
        )

    st.success(
        f"Selected Brand: {selected_brand} | Selected Sub Brand: {selected_subbrand}"
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
        except:
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
                        selected_brand.upper(),
                        selected_brand[:3].upper()
                    )

                    subbrand_code = create_subbrand_code(
                        selected_subbrand
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
