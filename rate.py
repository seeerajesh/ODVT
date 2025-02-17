import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ✅ Set Streamlit Page Title
st.set_page_config(page_title="Logistics & EWB Dashboard", layout="wide")
st.title("📊 Logistics & EWB Dashboard")

# ✅ Cache data loading to improve performance
@st.cache_data
def load_data(file):
    df_pricing = pd.read_excel(file, sheet_name="Collective Data", engine="openpyxl")
    df_ewb = pd.read_excel(file, sheet_name="EWB", engine="openpyxl")
    
    # Convert "created_at" to datetime
    df_pricing["created_at"] = pd.to_datetime(df_pricing["created_at"])
    df_ewb["year"] = df_ewb["year"].astype(int)

    # Remove #N/A values for numeric calculations
    df_pricing = df_pricing.replace("#N/A", pd.NA).dropna(subset=["Toll Cost", "ETA", "Lead Distance", "Shipper"])
    
    return df_pricing, df_ewb

# ✅ File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        df_pricing, df_ewb = load_data(uploaded_file)

        # ✅ Streamlit Navigation Tabs
        tab1, tab2 = st.tabs(["📦 Logistics Pricing Dashboard", "📜 E-Way Bill Dashboard"])

        ### **🔹 TAB 1: Logistics Pricing Dashboard**
        with tab1:
            st.header("📦 Logistics Pricing Dashboard")

            # ✅ Sidebar Filters
            st.sidebar.header("🔍 Filter Data")

            def multi_select_with_select_all(label, column_values):
                """Creates a multi-select filter with a 'Select All' option"""
                options = ["Select All"] + list(column_values)
                selected_values = st.sidebar.multiselect(label, options, default=["Select All"])

                return list(column_values) if "Select All" in selected_values else selected_values

            # ✅ Filters
            origin_filter = multi_select_with_select_all("Select Origin Locality", df_pricing["Origin Locality"].unique())
            destination_filter = multi_select_with_select_all("Select Destination Locality", df_pricing["Destination Locality"].unique())
            transporter_filter = multi_select_with_select_all("Select Transporter", df_pricing["Transporter"].unique())

            # ✅ Date Range Predefined Filters + Full Date Selection
            date_options = {
                "Month to Date": datetime.today().replace(day=1),
                "1 Month": datetime.today() - timedelta(days=30),
                "3 Months": datetime.today() - timedelta(days=90),
                "6 Months": datetime.today() - timedelta(days=180),
                "1 Year": datetime.today() - timedelta(days=365),
                "Full Date Range": None  # Custom date input
            }
            selected_date_range = st.sidebar.radio("Select Date Range", list(date_options.keys()), index=4)

            if selected_date_range == "Full Date Range":
                start_date, end_date = st.sidebar.date_input("Select Custom Date Range", 
                                                             [df_pricing["created_at"].min().date(), df_pricing["created_at"].max().date()])
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
            else:
                start_date = date_options[selected_date_range]
                end_date = datetime.today()

            # ✅ Apply Filters
            filtered_pricing = df_pricing[
                (df_pricing["Origin Locality"].isin(origin_filter)) &
                (df_pricing["Destination Locality"].isin(destination_filter)) &
                (df_pricing["Transporter"].isin(transporter_filter)) &
                (df_pricing["created_at"].between(start_date, end_date))
            ]

            ### **🔹 Top Panel - Circle Charts**
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

            ### **🔹 TAB 2: EWB Dashboard**
        with tab2:
            st.header("📜 E-Way Bill Analysis for 2024")

            # ✅ Fixed PDF Embedding (No Chrome Block Issue)
            st.markdown("""
            ### 📄 **E-Way Bill 3-Year Journey**
            👉 [View Full PDF](https://drive.google.com/file/d/1N2NHRznQXvQFXojk3EY2Ml6NsdLbmDBR/view)

            #### 📌 **Embedded Preview**
            """, unsafe_allow_html=True)

            pdf_url = "https://drive.google.com/file/d/1N2NHRznQXvQFXojk3EY2Ml6NsdLbmDBR/preview"
            st.components.v1.iframe(pdf_url, height=600, scrolling=True)

            # ✅ EWB Bar Charts
            df_ewb_agg = df_ewb.groupby(["year", "type_of_supply"]).agg(
                total_value=("assessable_value", "sum"),
                total_ewaybills=("number_of_eway_bills", "sum")
            ).reset_index()

            # ✅ Chart 1: Yearly Assessable Value
            fig4 = px.bar(df_ewb_agg, x="year", y="total_value", color="type_of_supply",
                          title="Assessable Value YoY (Split by Supply Type)")
            st.plotly_chart(fig4)

            # ✅ Chart 2: Yearly Number of EWB
            fig5 = px.bar(df_ewb_agg, x="year", y="total_ewaybills", color="type_of_supply",
                          title="Number of EWB YoY (Split by Supply Type)")
            st.plotly_chart(fig5)

            # ✅ Chart 3: Missing Chart for Top 5 States (YoY Assessable Value)
            top_5_states = ["Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka", "Uttar Pradesh"]
            df_states = df_ewb[df_ewb["State"].isin(top_5_states)]
            fig6 = px.bar(df_states, x="State", y="assessable_value", color="year",
                          title="Assessable Value in Top 5 States (YoY)")
            st.plotly_chart(fig6)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
