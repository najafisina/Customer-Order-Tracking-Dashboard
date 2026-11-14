import streamlit as st
import pandas as pd


# ==========================================================
# Excel Information
# ==========================================================

DATA_PATH = "data/production_data.xlsx"
SHEET_NAME = "hame"


# ==========================================================
# Core Columns
# ==========================================================

CORE_COLUMNS = [
    "Article Number",
    "po no",
    "Description",
    "Customer name",
    "QTY",
    "Requested Delivery date",
]


# ==========================================================
# Load & Prepare Data
# ==========================================================

@st.cache_data
def load_data():

    # ------------------------------------------------------
    # Load Excel
    # ------------------------------------------------------

    df = pd.read_excel(
        DATA_PATH,
        sheet_name=SHEET_NAME
    )

    # ------------------------------------------------------
    # Clean Column Names
    # ------------------------------------------------------

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # ------------------------------------------------------
    # Check Core Columns
    # ------------------------------------------------------

    missing_columns = [
        column
        for column in CORE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # ------------------------------------------------------
    # Basic Data Types
    # ------------------------------------------------------

    df["Article Number"] = (
        df["Article Number"]
        .astype(str)
    )

    df["po no"] = (
        df["po no"]
        .astype(str)
    )

    # ------------------------------------------------------
    # Numeric Columns
    # ------------------------------------------------------

    numeric_columns = [
        "QTY",
        "Warehouse",
        "Nonsellable",
        "Transfer",
        "producted",
        "Plan",
        "Packaging",
        "final check",
        "sorting",
        "cutting",
        "Print test",
        "UV printing",
        "offset print",
        "Roll-to-Sheet Offset",
        "slitting",
        "Gravure printing",
        "emboss",
        "Simultaneous cutting and embossing",
        "mix",
        "roll to roll",
        "Shrink",
        "boresh",
        "Back printing",
        "Print pass 2",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

    # ------------------------------------------------------
    # Requested Delivery Date
    # ------------------------------------------------------

    if "Requested Delivery date" in df.columns:

        df["Requested Delivery date"] = pd.to_datetime(
            df["Requested Delivery date"],
            unit="D",
            origin="1899-12-30",
            errors="coerce"
        )

    # ------------------------------------------------------
    # Return Prepared Data
    # ------------------------------------------------------

    return df