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

            # ✅ Date Range Predefined Filters
            date_options = {
                "Month to Date": datetime.today().replace(day=1),
                "1 Month": datetime.today() - timedelta(days=30),
                "3 Months": datetime.today() - timedelta(days=90),
                "6 Months": datetime.today() - timedelta(days=180),
                "1 Year": datetime.today() - timedelta(days=365)
            }
            selected_date_range = st.sidebar.radio("Select Date Range", list(date_options.keys()), index=4)
            start_date = date_options[selected_date_range]
            end_date = datetime.today()

            # ✅ Apply Filters
            filtered_pricing = df_pricing[
                (df_pricing["Origin Locality"].isin(origin_filter)) &
                (df_pricing["Destination Locality"].isin(destination_filter)) &
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

            ### **🔹 New Cards for Toll Cost & ETA**
            avg_toll = filtered_pricing["Toll Cost"].mean()
            avg_eta = filtered_pricing["ETA"].mean()
            col1.metric("🚦 Average Toll Cost", f"₹{avg_toll:,.2f}")
            col2.metric("⏳ Average ETA", f"{avg_eta:.1f} hours")

            ### **🔹 Bubble Chart: Top 5 Origin & Destination States**
            top_states = ["Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka", "Uttar Pradesh"]
            state_agg = filtered_pricing[
                (filtered_pricing["Origin State"].isin(top_states)) & 
                (filtered_pricing["Destination State"].isin(top_states))
            ].groupby(["Origin State", "Destination State"]).agg(
                num_trips=("Shipper", "count"),
                avg_shipper_rate=("Shipper", "mean")
            ).reset_index()

            fig3 = px.scatter(state_agg, 
                              x="Origin State", y="Destination State",
                              size="avg_shipper_rate", color="avg_shipper_rate",
                              title="Top 5 Origin-Destination Pairs by Shipper Rate",
                              hover_name="Origin State", size_max=30,
                              text="avg_shipper_rate")  # ✅ Display values inside bubbles
            fig3.update_traces(textposition="top center")
            st.plotly_chart(fig3)

        ### **🔹 TAB 2: EWB Dashboard**
        with tab2:
            st.header("📜 E-Way Bill Analysis for 2024")

            # ✅ Embed EWB PDF
            st.markdown("""
            ### 📄 **E-Way Bill 3-Year Journey**
            👉 [View Full PDF](https://docs.ewaybillgst.gov.in/Documents/ewaybill3yearJourney.pdf)

            #### 📌 **Embedded Preview**
            """, unsafe_allow_html=True)

            pdf_url = "https://docs.ewaybillgst.gov.in/Documents/ewaybill3yearJourney.pdf"
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

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
