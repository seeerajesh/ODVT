import streamlit as st
import pandas as pd
import plotly.express as px  # For interactive graphs

# ✅ Set Streamlit Page Title
st.set_page_config(page_title="Logistics & EWB Dashboard", layout="wide")
st.title("📊 Logistics & E-Way Bill Dashboard")

# ✅ File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        # ✅ Read data from both tabs
        df_pricing = pd.read_excel(uploaded_file, sheet_name="collective data", engine="openpyxl")
        df_ewb = pd.read_excel(uploaded_file, sheet_name="EWB", engine="openpyxl")

        # ✅ Ensure required columns exist in "collective data"
        required_columns_pricing = [
            "Origin Pin code", "Origin Locality", "Origin State",
            "Destination Pin code", "Destination Locality", "Destination State",
            "truck_type", "created_at", "Rate", "Category"
        ]
        missing_pricing = [col for col in required_columns_pricing if col not in df_pricing.col
