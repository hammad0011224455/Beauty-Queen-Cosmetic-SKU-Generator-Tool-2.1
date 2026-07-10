import streamlit as st
import pandas as pd
from sku_generator import generate_sku

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="SKU Generator",
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

.stButton>button {
    width:100%;
    height:55px;
    border-radius:12px;
    border:none;
    font-weight:600;
    font-size:16px;
}

.stDownloadButton>button {
    width:100%;
    height:55px;
    border-radius:12px;
    font-weight:600;
}

.upload-box {
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0 3px 15px rgba(0,0,0,0.07);
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
    <h1>🏷️ Shopify SKU Generator</h1>
    <p>
        Automatically generate unique Shopify SKUs using
        Brand Codes + Sub Brand Detection + Unique Number Logic.
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

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------
# FILE UPLOAD
# ----------------------------------
st.markdown("### Upload Shopify CSV")

uploaded_file = st.file_uploader(
    "Choose CSV File",
    type=["csv"]
)

# ----------------------------------
# PROCESS
# ----------------------------------
if uploaded_file:

    try:

        df = pd.read_csv(uploaded_file)

        st.success("CSV uploaded successfully")

        st.write("### Preview")

        st.dataframe(
            df.head(),
            use_container_width=True
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

            for i, row in enumerate(df.iterrows()):

                _, row_data = row

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
                use_container_width=True
            )

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇ Download CSV",
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
Built with Streamlit • Shopify SKU Automation Tool
</div>
""", unsafe_allow_html=True)

