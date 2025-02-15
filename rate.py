import streamlit as st
import pandas as pd
import plotly.express as px  # For visualization

# ✅ Set Streamlit Page Title
st.set_page_config(page_title="Logistics & EWB Dashboard", layout="wide")
st.title("📊 Logistics Pricing & EWB Dashboard")

# ✅ File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        # ✅ Read data from both tabs
        df_pricing = pd.read_excel(uploaded_file, sheet_name="Collective Data", engine="openpyxl")
        df_ewb = pd.read_excel(uploaded_file, sheet_name="EWB", engine="openpyxl")

        # ✅ Ensure required columns exist in "collective data"
        required_columns_pricing = [
            "Origin Pin code", "Origin Locality", "Origin State",
            "Destination Pin code", "Destination Locality", "Destination State",
            "Truck type", "Toll Vehicle Category", "created_at", "Shipper", 
            "Fleet owner Rate", "LSP Rate", "Transporter", "Category", "Rate type"
        ]
        missing_pricing = [col for col in required_columns_pricing if col not in df_pricing.columns]

        if missing_pricing:
            st.error(f"❌ Missing columns in 'collective data' tab: {missing_pricing}")
        else:
            # ✅ Convert "created_at" column to datetime format
            df_pricing["created_at"] = pd.to_datetime(df_pricing["created_at"])

            # ✅ Streamlit Sidebar Filters
            st.sidebar.header("🔍 Filter Data")
            origin_filter = st.sidebar.selectbox("Select Origin Pin Code", df_pricing["Origin Pin code"].unique())
            destination_filter = st.sidebar.selectbox("Select Destination Locality", df_pricing["Destination Locality"].unique())
            vehicle_filter = st.sidebar.selectbox("Select Truck Type", df_pricing["Truck type"].unique())

            # ✅ Fix Date Filter: Convert to datetime before filtering
            date_range = st.sidebar.date_input("Select Date Range", 
                                               [df_pricing["created_at"].min().date(), df_pricing["created_at"].max().date()])
            start_date = pd.to_datetime(date_range[0])  
            end_date = pd.to_datetime(date_range[1])  

            # ✅ Apply Filters
            filtered_pricing = df_pricing[
                (df_pricing["Origin Pin code"] == origin_filter) &
                (df_pricing["Destination Locality"] == destination_filter) &
                (df_pricing["Truck type"] == vehicle_filter) &
                (df_pricing["created_at"].between(start_date, end_date))
            ]

            ### **🔹 Section 1: Top Panel - Circle Charts**
            col1, col2 = st.columns(2)

            # ✅ Total "Shipper Rate" split by "Rate Type"
            if not filtered_pricing.empty:
                shipper_rate_total = filtered_pricing["Shipper"].sum()
                rate_type_data = filtered_pricing.groupby("Rate type")["Shipper"].sum().reset_index()
                fig1 = px.pie(rate_type_data, values="Shipper", names="Rate type", title="Shipper Rate Breakdown by Rate Type", hole=0.4)
                col1.plotly_chart(fig1)

                # ✅ Total Vehicles (Count of Rows) split by "Category"
                vehicle_count = len(filtered_pricing)
                category_data = filtered_pricing["Category"].value_counts().reset_index()
                category_data.columns = ["Category", "Vehicle Count"]
                fig2 = px.pie(category_data, values="Vehicle Count", names="Category", title="Vehicle Count by Category", hole=0.4)
                col2.plotly_chart(fig2)
            
            else:
                col1.warning("No data found for the selection.")
                col2.warning("No data found for the selection.")

            ### **🔹 Section 2: Transporter Table**
            if not filtered_pricing.empty:
                st.write("### 🚚 Transporter-wise Aggregated Data")
                transporter_agg = filtered_pricing.groupby("Transporter").agg(
                    Vehicles_Operated=("Transporter", "count"),
                    Total_Shipper_Rate=("Shipper", "sum")
                ).reset_index()
                st.dataframe(transporter_agg)

            else:
                st.warning("No data found for the selection.")

            ### **🔹 Section 3: Line Chart for Trending Shipper Rates**
            if not filtered_pricing.empty:
                st.write("### 📈 Trending Shipper Rates Over Time")
                aggregated_pricing = filtered_pricing.groupby(pd.Grouper(key="created_at", freq="M")).agg({"Shipper": "mean"}).reset_index()
                fig3 = px.line(aggregated_pricing, x="created_at", y="Shipper", title="Shipper Rate Trend")
                st.plotly_chart(fig3)

            else:
                st.warning("No data found for the selection.")

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
