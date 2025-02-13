import streamlit as st
import pandas as pd
import plotly.express as px  # For interactive visualization

# ✅ Set Streamlit Page Title
st.title("📊 Logistics Pricing Dashboard")

# ✅ File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        # ✅ Read data from "collective data" tab
        df = pd.read_excel(uploaded_file, sheet_name="collective data", engine="openpyxl")

        # ✅ Ensure required columns exist
        required_columns = [
            "Origin Pin code", "Origin Locality", "Origin State",
            "Destination Pin code", "Destination Locality", "Destination State",
            "truck_type", "created_at", "Rate", "Category"
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Missing required columns: {missing_columns}")
        else:
            # ✅ Convert "created_at" to datetime format
            df["created_at"] = pd.to_datetime(df["created_at"])

            # ✅ Sidebar Filters
            st.sidebar.header("🔍 Filter Data")
            origin_filter = st.sidebar.selectbox("Select Origin Pin Code", df["Origin Pin code"].unique())
            destination_filter = st.sidebar.selectbox("Select Destination Locality", df["Destination Locality"].unique())
            vehicle_filter = st.sidebar.selectbox("Select Truck Type", df["truck_type"].unique())
            date_range = st.sidebar.date_input("Select Date Range", 
                                               [df["created_at"].min(), df["created_at"].max()])

            # ✅ Apply Filters
            filtered_df = df[
                (df["Origin Pin code"] == origin_filter) &
                (df["Destination Locality"] == destination_filter) &
                (df["truck_type"] == vehicle_filter) &
                (df["created_at"].between(date_range[0], date_range[1]))
            ]

            # ✅ Aggregated Table (Average Price Per Month)
            aggregated_df = filtered_df.groupby(pd.Grouper(key="created_at", freq="M")).agg({"Rate": "mean"}).reset_index()

            # ✅ Display Data Table
            st.write("### 📋 Aggregated Price Data")
            st.dataframe(aggregated_df)

            # ✅ Price Trend Graph
            st.write("### 📈 Price Trend Over Time")
            fig = px.line(aggregated_df, x="created_at", y="Rate", title="Price Trend")
            st.plotly_chart(fig)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
