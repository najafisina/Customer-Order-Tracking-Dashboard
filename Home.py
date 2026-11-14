import streamlit as st

st.set_page_config(
    page_title="Production Monitoring Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Production Monitoring Dashboard")

st.markdown("---")

st.header("Welcome")

st.write(
    """
    Welcome to the Production Monitoring Dashboard.

    Please select one of the pages from the left sidebar.
    """
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.info("🔍 Product Search")

with col2:
    st.info("📅 Delivery Schedule")