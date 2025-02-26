import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image

# ✅ Set Streamlit Page Title and Layout
st.set_page_config(page_title="Pre-Bidding Intelligence Dashboard", layout="wide")

# ✅ Load and Display Company Logo (Top Left) & Login Info (Top Right)
logo_path = "logo.png"  # Company Logo
login_path = "login.png"  # Login Logo

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
    else:
        st.warning("Company logo not found.")
with col3:
    login = load_image(login_path)
    if login:
        st.image(login, width=150)
    else:
        st.warning("Login image not found.")

# ✅ Sidebar Navigation Menu
st.sidebar.header("📌 Navigation")
menu_option = st.sidebar.radio("Select Page:", ["Control Tower", "Add Trip", "Pre-Bid Intelligence"])

# ✅ Handle Menu Selection
image_paths = {
    "Control Tower": "control_tower.png",
    "Add Trip": "add_trip.png"
}

if menu_option in image_paths:
    image = load_image(image_paths[menu_option])
    if image:
        st.image(image, use_container_width=True)
    else:
        st.warning(f"Image for {menu_option} not found.")
else:
    st.title("📊 Pre-Bidding Intelligence Dashboard")
    
    # ✅ Cache data loading to improve performance
    @st.cache_data
    def load_data(file):
        df_pricing = pd.read_excel(file, sheet_name="Collective Data", engine="openpyxl")
        df_ewb = pd.read_excel(file, sheet_name="EWB", engine="openpyxl")
        
        df_pricing["created_at"] = pd.to_datetime(df_pricing["created_at"])
        df_ewb["year"] = df_ewb["year"].astype(int)
        df_pricing = df_pricing.replace("#N/A", pd.NA).dropna(subset=["Toll Cost", "ETA", "Lead Distance", "Shipper", "Rating"])
        
        return df_pricing, df_ewb

    # ✅ File Upload
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

    if uploaded_file is not None:
        try:
            df_pricing, df_ewb = load_data(uploaded_file)
            tab1, tab2, tab3 = st.tabs(["📦 Overview Dashboard", "🚛 Transporter Discovery", "📜 EWB Dashboard"])
            
            # ✅ Move Filters to Main Screen
            st.header("🔍 Common Filters")
            def multi_select_with_select_all(label, column_values, key):
                options = ["Select All"] + list(column_values)
                selected_values = st.multiselect(label, options, default=["Select All"], key=key)
                return list(column_values) if "Select All" in selected_values else selected_values

            origin_filter = multi_select_with_select_all("Select Origin Locality", df_pricing["Origin Locality"].unique(), key="origin_filter")
            destination_filter = multi_select_with_select_all("Select Destination Locality", df_pricing["Destination Locality"].unique(), key="destination_filter")
            transporter_filter = multi_select_with_select_all("Select Transporter", df_pricing["Transporter"].unique(), key="transporter_filter")
            
            rating_ranges = {
                "<2": df_pricing[df_pricing["Rating"] < 2]["Rating"],
                "2-3": df_pricing[(df_pricing["Rating"] >= 2) & (df_pricing["Rating"] < 3)]["Rating"],
                "3-4": df_pricing[(df_pricing["Rating"] >= 3) & (df_pricing["Rating"] < 4)]["Rating"],
                ">4": df_pricing[df_pricing["Rating"] >= 4]["Rating"]
            }
            selected_ratings = st.multiselect("Select Transporter Rating", ["Select All", "<2", "2-3", "3-4", ">4"], default=["Select All"], key="rating_filter")
            if "Select All" in selected_ratings:
                selected_ratings = list(rating_ranges.keys())
            rating_filter_values = pd.concat([rating_ranges[r] for r in selected_ratings]).tolist()
            
            date_options = {
                "Month to Date": datetime.today().replace(day=1),
                "3 Months": datetime.today() - timedelta(days=90),
                "6 Months": datetime.today() - timedelta(days=180),
                "1 Year": datetime.today() - timedelta(days=365),
                "Full Range": None  
            }
            selected_date_range = st.radio("Select Date Range", list(date_options.keys()), index=3)
            if selected_date_range == "Full Range":
                start_date, end_date = st.date_input("Select Custom Date Range", [df_pricing["created_at"].min().date(), df_pricing["created_at"].max().date()])
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
            else:
                start_date = date_options[selected_date_range]
                end_date = datetime.today()
            
            filtered_pricing = df_pricing[
                (df_pricing["Origin Locality"].isin(origin_filter)) &
                (df_pricing["Destination Locality"].isin(destination_filter)) &
                (df_pricing["Transporter"].isin(transporter_filter)) &
                (df_pricing["Rating"].isin(rating_filter_values)) &
                (df_pricing["created_at"].between(start_date, end_date))
            ]
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
    else:
        st.info("📂 Please upload an Excel file.")
