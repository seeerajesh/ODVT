import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image

# ✅ Set Streamlit Page Title and Layout
st.set_page_config(page_title="Pre-Bidding Intelligence Dashboard", layout="wide")

# ✅ Load and Display Company Logo (Top Left) & Login Info (Top Right)
logo_path = "Image_1.png"  # Company Logo
login_path = "Image_2.png"  # Login Logo

def load_image(image_path):
    try:
        return Image.open(image_path)
    except Exception:
        return None

col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
with col1:
    logo = load_image(logo_path)
    if logo:
        st.image(logo, width=150)
with col3:
    login = load_image(login_path)
    if login:
        st.image(login, width=150)

# ✅ Sidebar Navigation Menu
st.sidebar.header("📌 Navigation")
menu_option = st.sidebar.radio("Select Page:", ["Control Tower", "Add Trip", "Pre-Bid Intelligence"])

@st.cache_data
def load_data(file):
    df_pricing = pd.read_excel(file, sheet_name="Collective Data", engine="openpyxl")
    df_ewb = pd.read_excel(file, sheet_name="EWB", engine="openpyxl")
    df_pricing["created_at"] = pd.to_datetime(df_pricing["created_at"], errors='coerce')
    df_ewb["year"] = pd.to_numeric(df_ewb["year"], errors='coerce').dropna().astype(int)
    df_pricing = df_pricing.replace("#N/A", pd.NA).dropna(subset=["Toll Cost", "ETA", "Lead Distance", "Shipper", "Rating"])
    return df_pricing, df_ewb

uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        df_pricing, df_ewb = load_data(uploaded_file)
        
        st.header("🔍 Common Filters")
        
        def multi_select_with_select_all(label, column_values, key):
            options = ["Select All"] + list(column_values)
            selected_values = st.multiselect(label, options, default=["Select All"], key=key)
            return list(column_values) if "Select All" in selected_values else selected_values
        
        origin_filter = multi_select_with_select_all("Select Origin Locality", df_pricing["Origin Locality"].dropna().unique(), key="origin_filter")
        destination_filter = multi_select_with_select_all("Select Destination Locality", df_pricing["Destination Locality"].dropna().unique(), key="destination_filter")
        
        date_range = st.date_input("Select Date Range", [df_pricing["created_at"].min().date(), df_pricing["created_at"].max().date()])
        
        filtered_pricing = df_pricing[(df_pricing["Origin Locality"].isin(origin_filter)) &
                                      (df_pricing["Destination Locality"].isin(destination_filter)) &
                                      (df_pricing["created_at"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))]
        
        if menu_option == "Pre-Bid Intelligence":
            st.subheader("📊 Pre-Bid Intelligence Dashboard")
            
            col1, col2 = st.columns(2)
            
            with col1:
                shipper_chart = px.pie(filtered_pricing, values="Shipper", names="Rate Type", title="Total Shipper Rate by Rate Type", hole=0.4)
                st.plotly_chart(shipper_chart, use_container_width=True)
            
            with col2:
                vehicle_chart = px.pie(filtered_pricing, names="Category", title="Total Vehicle Count by Category", hole=0.4)
                st.plotly_chart(vehicle_chart, use_container_width=True)
            
            avg_table = filtered_pricing.groupby(["Origin Locality", "Destination Locality"]).agg({"Shipper": "mean", "ETA": "mean", "Toll Cost": "mean", "Lead Distance": "mean"}).reset_index()
            avg_table = avg_table.round(2)
            st.dataframe(avg_table)
            
            top_states = ["Maharastra", "Gujarat", "Tamil Nadu", "Karnataka", "Uttar Pradesh"]
            df_bubble = filtered_pricing[filtered_pricing["Origin State"].isin(top_states) & filtered_pricing["Destination State"].isin(top_states)]
            bubble_chart = px.scatter(df_bubble, x="Origin State", y="Destination State", size="Shipper", color="Origin State", title="Bubble Chart: Origin vs Destination State")
            st.plotly_chart(bubble_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
else:
    st.info("📂 Please upload an Excel file.")
