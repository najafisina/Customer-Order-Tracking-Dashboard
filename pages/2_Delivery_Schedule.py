import streamlit as st
import pandas as pd

# ==========================================================
# Page Config
# ==========================================================

st.set_page_config(
    page_title="Delivery Schedule Dashboard",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 Delivery Schedule Dashboard")
st.write("Delivery Schedule Monitoring System")

# ==========================================================
# Excel Information
# ==========================================================

DATA_PATH = "data/production_data.xlsx"
SHEET_NAME = "hame"

# ==========================================================
# Load Excel
# ==========================================================

@st.cache_data
def load_data():

    df = pd.read_excel(
        DATA_PATH,
        sheet_name=SHEET_NAME
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    return df

try:

    df = load_data()

except Exception as e:

    st.error(f"Error Loading Excel File\n\n{e}")

    st.stop()

# ==========================================================
# Data Cleaning
# ==========================================================

df["Article Number"] = df["Article Number"].astype(str)

df["po no"] = df["po no"].astype(str)

numeric_columns = [
    "QTY",
    "Warehouse",
    "Transfer",
    "Nonsellable",
    "Packaging",
    "Plan",
    "producted"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["Requested Delivery date"] = pd.to_datetime(
    df["Requested Delivery date"],
    unit="D",
    origin="1899-12-30",
    errors="coerce"
)

# ==========================================================
# Date Filters
# ==========================================================

min_date = df["Requested Delivery date"].min()
max_date = df["Requested Delivery date"].max()

if pd.isna(min_date) or pd.isna(max_date):
    st.error("No valid delivery dates found in the dataset.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=min_date.date()
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=max_date.date()
    )

# ==========================================================
# Customer Filter
# ==========================================================

all_customers = sorted(
    df["Customer name"]
    .dropna()
    .astype(str)
    .unique()
)

selected_customers = st.multiselect(
    "Select Customer(s)",
    options=all_customers,
    default=all_customers
)

# ==========================================================
# Apply Filters
# ==========================================================

filtered_df = df[
    (df["Requested Delivery date"].dt.date >= start_date) &
    (df["Requested Delivery date"].dt.date <= end_date)
].copy()

if selected_customers:
    filtered_df = filtered_df[
        filtered_df["Customer name"].astype(str).isin(selected_customers)
    ]

if filtered_df.empty:
    st.warning("No data found for selected filters.")
    st.stop()

# ==========================================================
# KPI Calculations
# ==========================================================

total_delivery = filtered_df["QTY"].sum()
total_orders = len(filtered_df)
total_articles = filtered_df["Article Number"].nunique()

# ==========================================================
# KPI Cards
# ==========================================================

st.subheader("Summary")

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric("Total Delivery Qty", f"{total_delivery:,.0f}")

with kpi2:
    st.metric("Total Orders", f"{total_orders:,.0f}")

with kpi3:
    st.metric("Total Articles", f"{total_articles:,.0f}")

st.markdown("---")

# ==========================================================
# Delivery Orders Table
# ==========================================================

st.subheader("Delivery Orders")

orders_table = filtered_df[[
    "Article Number",
    "po no",
    "Customer name",
    "Description",
    "Requested Delivery date",
    "QTY"
]].copy()

orders_table["Requested Delivery date"] = orders_table["Requested Delivery date"].dt.strftime("%Y-%m-%d")

orders_table.columns = [
    "Article Number",
    "PO Number",
    "Customer Name",
    "Description",
    "Requested Delivery Date",
    "Delivery Quantity"
]

st.dataframe(
    orders_table,
    hide_index=True,
    use_container_width=True
)

st.markdown("---")

# ==========================================================
# Shortage Analysis
# ==========================================================

st.subheader("Shortage Analysis")

shortage_df = filtered_df.groupby([
    "Article Number",
    "Description"
], as_index=False).agg({
    "QTY": "sum",
    "Warehouse": "first",
    "Transfer": "first",
    "Nonsellable": "first",
    "Packaging": "first",
    "Plan": "first",
    "producted": "first"
})

shortage_df["Shortage"] = shortage_df["QTY"] - (
    shortage_df["Warehouse"] +
    shortage_df["Transfer"] +
    shortage_df["Nonsellable"]
)

shortage_df = shortage_df[shortage_df["Shortage"] > 0].copy()

if shortage_df.empty:
    st.success("No shortage found for selected filters.")
else:
    shortage_df = shortage_df[[
        "Article Number",
        "Description",
        "QTY",
        "Warehouse",
        "Transfer",
        "Nonsellable",
        "Packaging",
        "Plan",
        "producted",
        "Shortage"
    ]]

    shortage_df.columns = [
        "Article Number",
        "Description",
        "Delivery Qty",
        "Warehouse",
        "Transfer",
        "Nonsellable",
        "Packaging",
        "Plan",
        "Produced",
        "Shortage"
    ]

    st.dataframe(
        shortage_df,
        hide_index=True,
        use_container_width=True
    )
