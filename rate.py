import streamlit as st
import pandas as pd
import plotly.express as px  

# ✅ Set Streamlit Page Title
st.set_page_config(page_title="Logistics & EWB Dashboard", layout="wide")
st.title("📊 Logistics Pricing & EWB Dashboard")

# ✅ File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        # ✅ Read data from both tabs
        df_pricing = pd.read_excel(uploaded_file, sheet_name="collective data", engine="openpyxl")
        df_ewb = pd.read_excel(uploaded_file, sheet_name="EWB", engine="openpyxl")

        # ✅ Ensure required columns exist in "collective data"
        required_columns_pricing = [
            "Origin Locality", "Origin State", "Destination Locality",
            "Truck type", "Toll Vehicle Category", "created_at", "Shipper", 
            "Fleet owner Rate", "LSP Rate", "Transporter", "Category", "Rate type", "Rating"
        ]
        missing_pricing = [col for col in required_columns_pricing if col not in df_pricing.columns]

        # ✅ Ensure required columns exist in "EWB"
        required_columns_ewb = [
            "fiscal_year", "year", "month", "state", "state_code",
            "type_of_supply", "assessable_value", "number_of_eway_bills"
        ]
        missing_ewb = [col for col in required_columns_ewb if col not in df_ewb.columns]

        if missing_pricing:
            st.error(f"❌ Missing columns in 'collective data' tab: {missing_pricing}")
        elif missing_ewb:
            st.error(f"❌ Missing columns in 'EWB' tab: {missing_ewb}")
        else:
            # ✅ Convert "created_at" column to datetime format
            df_pricing["created_at"] = pd.to_datetime(df_pricing["created_at"])

            # ✅ Convert "year" column to integer in EWB Data
            df_ewb["year"] = df_ewb["year"].astype(int)

            # ✅ Streamlit Navigation Tabs
            tab1, tab2 = st.tabs(["📦 Logistics Pricing Dashboard", "📜 E-Way Bill Dashboard"])

            ### **🔹 TAB 1: Logistics Pricing Dashboard**
            with tab1:
                st.header("📦 Logistics Pricing Dashboard")

                # ✅ Sidebar Filters
                st.sidebar.header("🔍 Filter Data")
                origin_filter = st.sidebar.selectbox("Select Origin Locality", df_pricing["Origin Locality"].unique())
                destination_filter = st.sidebar.selectbox("Select Destination Locality", df_pricing["Destination Locality"].unique())
                vehicle_filter = st.sidebar.selectbox("Select Truck Type", df_pricing["Truck type"].unique())

                # ✅ Fix Date Filter: Convert to datetime before filtering
                date_range = st.sidebar.date_input("Select Date Range", 
                                                   [df_pricing["created_at"].min().date(), df_pricing["created_at"].max().date()])
                start_date = pd.to_datetime(date_range[0])  
                end_date = pd.to_datetime(date_range[1])  

                # ✅ Apply Filters
                filtered_pricing = df_pricing[
                    (df_pricing["Origin Locality"] == origin_filter) &
                    (df_pricing["Destination Locality"] == destination_filter) &
                    (df_pricing["Truck type"] == vehicle_filter) &
                    (df_pricing["created_at"].between(start_date, end_date))
                ]

                ### **🔹 Section 1: Top Panel - Circle Charts**
                col1, col2 = st.columns(2)

                if not filtered_pricing.empty:
                    # ✅ Shipper Rate Breakdown
                    shipper_rate_total = filtered_pricing["Shipper"].sum()
                    rate_type_data = filtered_pricing.groupby("Rate type")["Shipper"].sum().reset_index()
                    fig1 = px.pie(rate_type_data, values="Shipper", names="Rate type", hole=0.4,
                                  title=f"Shipper Rate Breakdown (Total: ₹{shipper_rate_total:,.2f})")
                    col1.plotly_chart(fig1)

                    # ✅ Vehicle Count Breakdown
                    vehicle_count = len(filtered_pricing)
                    category_data = filtered_pricing["Category"].value_counts().reset_index()
                    category_data.columns = ["Category", "Vehicle Count"]
                    fig2 = px.pie(category_data, values="Vehicle Count", names="Category", hole=0.4,
                                  title=f"Total Vehicles Plying: {vehicle_count}")
                    col2.plotly_chart(fig2)
                
                ### **🔹 Section 2: Transporter Table (Sorted by Rating)**
                if not filtered_pricing.empty:
                    st.write("### 🚚 Transporter-wise Aggregated Data")
                    transporter_agg = filtered_pricing.groupby("Transporter").agg(
                        Vehicles_Operated=("Transporter", "count"),
                        Total_Shipper_Rate=("Shipper", "sum"),
                        Rating=("Rating", "max")
                    ).reset_index().sort_values(by="Rating", ascending=False)
                    st.dataframe(transporter_agg)

                ### **🔹 Section 3: Line Chart for Trending Shipper Rates**
                if not filtered_pricing.empty:
                    st.write("### 📈 Trending Shipper Rates Over Time")
                    aggregated_pricing = filtered_pricing.groupby(pd.Grouper(key="created_at", freq="M")).agg({"Shipper": "mean"}).reset_index()
                    fig3 = px.line(aggregated_pricing, x="created_at", y="Shipper", title="Shipper Rate Trend")
                    st.plotly_chart(fig3)

                ### **🔹 Section 4: Summary Card**
                st.subheader("📌 Summary Insights")
                rate_trend = "Increasing" if filtered_pricing["Shipper"].iloc[-1] > filtered_pricing["Shipper"].iloc[0] else "Decreasing"
                top_transporter = transporter_agg.iloc[0]["Transporter"] if not transporter_agg.empty else "No Data"
                total_trips = len(filtered_pricing)

                st.markdown(f"""
                - **Rate Trend:** {rate_trend} 📈📉  
                - **Recommended Transporter:** {top_transporter} (Best Rating & Most Trips) 🚛  
                - **Total Trips:** {total_trips} 🚚  
                """)

            ### **🔹 TAB 2: EWB Dashboard**
            with tab2:
                st.header("📜 E-Way Bill Analysis for 2024")
                df_ewb_2024 = df_ewb[df_ewb["year"] == 2024]
                ewb_agg = df_ewb_2024.groupby("state_code").agg({"assessable_value": "sum", "number_of_eway_bills": "sum"}).reset_index()
                st.bar_chart(ewb_agg.set_index("state_code"))

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
