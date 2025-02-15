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
        df_pricing = pd.read_excel(uploaded_file, sheet_name="Collective Data", engine="openpyxl")
        df_ewb = pd.read_excel(uploaded_file, sheet_name="EWB", engine="openpyxl")

        # ✅ Ensure required columns exist in "collective data"
        required_columns_pricing = [
            "Origin Pin code", "Origin Locality", "Origin State",
            "Destination Pin code", "Destination Locality", "Destination State",
            "truck_type", "created_at", "Rate", "Category"
        ]
        missing_pricing = [col for col in required_columns_pricing if col not in df_pricing.columns]

        # ✅ Ensure required columns exist in "EWB"
        required_columns_ewb = [
            "fiscal_year", "year", "month", "state", "state_code",
            "type_of_supply", "assessable_value", "number_of_eway_bills",
            "number_of_suppliers", "unit", "notes"
        ]
        missing_ewb = [col for col in required_columns_ewb if col not in df_ewb.columns]

        if missing_pricing:
            st.error(f"❌ Missing columns in 'collective data' tab: {missing_pricing}")
        elif missing_ewb:
            st.error(f"❌ Missing columns in 'EWB' tab: {missing_ewb}")
        else:
            # ✅ Convert "created_at" column to datetime format in Pricing Data
            df_pricing["created_at"] = pd.to_datetime(df_pricing["created_at"])

            # ✅ Convert "year" column to integer in EWB Data
            df_ewb["year"] = df_ewb["year"].astype(int)

            # ✅ Streamlit Navigation Tabs
            tab1, tab2 = st.tabs(["📦 Logistics Pricing Dashboard", "📜 E-Way Bill Dashboard"])

            ### **🔹 TAB 1: Pricing Dashboard (From "Collective Data")**
            with tab1:
                st.header("📦 Logistics Pricing Dashboard")
                
                # ✅ Sidebar Filters
                st.sidebar.header("🔍 Filter Data")
                origin_filter = st.sidebar.selectbox("Select Origin Pin Code", df_pricing["Origin Pin code"].unique())
                destination_filter = st.sidebar.selectbox("Select Destination Locality", df_pricing["Destination Locality"].unique())
                vehicle_filter = st.sidebar.selectbox("Select Truck Type", df_pricing["truck_type"].unique())

                # ✅ Fix Date Filter: Convert to datetime before filtering
                date_range = st.sidebar.date_input("Select Date Range", 
                                                   [df_pricing["created_at"].min().date(), df_pricing["created_at"].max().date()])
                start_date = pd.to_datetime(date_range[0])  
                end_date = pd.to_datetime(date_range[1])  

                # ✅ Apply Filters
                filtered_pricing = df_pricing[
                    (df_pricing["Origin Pin code"] == origin_filter) &
                    (df_pricing["Destination Locality"] == destination_filter) &
                    (df_pricing["truck_type"] == vehicle_filter) &
                    (df_pricing["created_at"].between(start_date, end_date))
                ]

                # ✅ Aggregated Table (Average Price Per Month)
                aggregated_pricing = filtered_pricing.groupby(pd.Grouper(key="created_at", freq="M")).agg({"Rate": "mean"}).reset_index()

                # ✅ Display Data Table
                st.write("### 📋 Aggregated Price Data")
                st.dataframe(aggregated_pricing)

                # ✅ Price Trend Graph
                st.write("### 📈 Price Trend Over Time")
                fig = px.line(aggregated_pricing, x="created_at", y="Rate", title="Price Trend")
                st.plotly_chart(fig)

            ### **🔹 TAB 2: E-Way Bill Dashboard (From "EWB")**
            with tab2:
                st.header("📜 E-Way Bill Analysis for 2024")
                
                # ✅ Filter only 2024 data
                df_ewb_2024 = df_ewb[df_ewb["year"] == 2024]

                # ✅ Aggregate by state_code: Sum Assessable Value & E-Way Bills
                df_ewb_agg = df_ewb_2024.groupby("state_code").agg(
                    {"assessable_value": "sum", "number_of_eway_bills": "sum"}
                ).reset_index()

                # ✅ Get Top 10 State Codes by Assessable Value
                top_10_states = df_ewb_agg.nlargest(10, "assessable_value")

                # ✅ Bar Chart: Top 10 States by Assessable Value
                st.write("### 💰 Top 10 States by Assessable Value")
                fig1 = px.bar(top_10_states, x="state_code", y="assessable_value", 
                              title="Assessable Value by Top 10 States", 
                              labels={"state_code": "State Code", "assessable_value": "Assessable Value (₹)"},
                              color="state_code")
                st.plotly_chart(fig1)

                # ✅ Get Top 10 State Codes by Number of E-Way Bills
                top_10_states_ewb = df_ewb_agg.nlargest(10, "number_of_eway_bills")

                # ✅ Bar Chart: Top 10 States by Number of E-Way Bills
                st.write("### 📝 Top 10 States by Number of E-Way Bills")
                fig2 = px.bar(top_10_states_ewb, x="state_code", y="number_of_eway_bills", 
                              title="Number of E-Way Bills by Top 10 States", 
                              labels={"state_code": "State Code", "number_of_eway_bills": "Number of E-Way Bills"},
                              color="state_code")
                st.plotly_chart(fig2)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
