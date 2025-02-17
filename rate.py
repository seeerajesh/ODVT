import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ✅ Set Streamlit Page Title
st.set_page_config(page_title="Pre-Bidding Intelligence Dashboard", layout="wide")
st.title("📊 Pre-Bidding Intelligence Dashboard")

# ✅ Cache data loading to improve performance
@st.cache_data
def load_data(file):
    df_pricing = pd.read_excel(file, sheet_name="Collective Data", engine="openpyxl")
    df_ewb = pd.read_excel(file, sheet_name="EWB", engine="openpyxl")
    
    # Convert "created_at" to datetime
    df_pricing["created_at"] = pd.to_datetime(df_pricing["created_at"])
    df_ewb["year"] = df_ewb["year"].astype(int)

    # Remove #N/A values for numeric calculations
    df_pricing = df_pricing.replace("#N/A", pd.NA).dropna(subset=["Toll Cost", "ETA", "Lead Distance", "Shipper", "Rating"])
    
    return df_pricing, df_ewb

# ✅ File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        df_pricing, df_ewb = load_data(uploaded_file)

        # ✅ Streamlit Navigation Tabs
        tab1, tab2, tab3 = st.tabs(["📦 Overview Dashboard", "🚛 Transporter Discovery", "📜 EWB Dashboard"])

        # ✅ Sidebar Common Filters (Applies to Both Overview & Transporter Discovery)
        st.sidebar.header("🔍 Common Filters")

        origin_filter = st.sidebar.multiselect("Select Origin Locality", df_pricing["Origin Locality"].unique(), 
                                               default=[], key="origin_filter")
        destination_filter = st.sidebar.multiselect("Select Destination Locality", df_pricing["Destination Locality"].unique(), 
                                                    default=[], key="destination_filter")
        transporter_filter = st.sidebar.multiselect("Select Transporter", df_pricing["Transporter"].unique(), 
                                                    default=[], key="transporter_filter")
        
        rating_filter = st.sidebar.selectbox("Select Transporter Rating", 
                                             ["<1", "1-3", "3-4", ">4"], key="rating_filter")

        # ✅ Date Range Selection
        date_options = {
            "Month to Date": datetime.today().replace(day=1),
            "3 Months": datetime.today() - timedelta(days=90),
            "6 Months": datetime.today() - timedelta(days=180),
            "1 Year": datetime.today() - timedelta(days=365),
            "Full Range": None  # Custom date input
        }
        selected_date_range = st.sidebar.radio("Select Date Range", list(date_options.keys()), index=3)

        if selected_date_range == "Full Range":
            start_date, end_date = st.sidebar.date_input("Select Custom Date Range", 
                                                         [df_pricing["created_at"].min().date(), df_pricing["created_at"].max().date()])
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
        else:
            start_date = date_options[selected_date_range]
            end_date = datetime.today()

        # ✅ Apply Common Filters
        filtered_pricing = df_pricing[
            (df_pricing["Origin Locality"].isin(origin_filter)) &
            (df_pricing["Destination Locality"].isin(destination_filter)) &
            (df_pricing["Transporter"].isin(transporter_filter)) &
            (df_pricing["created_at"].between(start_date, end_date))
        ]

        ### **🔹 TAB 1: Overview Dashboard**
        with tab1:
            st.header("📦 Overview Dashboard")

            ### **🔹 Origin → Destination Table**
            st.subheader("📌 Origin to Destination Rate Summary")
            od_table = filtered_pricing.groupby(["Origin Locality", "Destination Locality"]).agg(
                Avg_Shipper_Rate=("Shipper", "mean"),
                Avg_ETA=("ETA", "mean"),
                Avg_Toll_Cost=("Toll Cost", "mean"),
                Avg_Lead_Distance=("Lead Distance", "mean")
            ).reset_index()
            st.dataframe(od_table)

            ### **🔹 Bubble Chart: Top 5 Origin-Destination States**
            st.subheader("📌 Shipper Rate by Origin-Destination (Rounded to 2 Decimals)")
            top_states = ["Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka", "Uttar Pradesh"]
            state_agg = filtered_pricing[
                (filtered_pricing["Origin State"].isin(top_states)) & 
                (filtered_pricing["Destination State"].isin(top_states))
            ].groupby(["Origin State", "Destination State"]).agg(
                num_trips=("Shipper", "count"),
                avg_shipper_rate=("Shipper", "mean")
            ).reset_index()

            state_agg["avg_shipper_rate"] = state_agg["avg_shipper_rate"].round(2)

            fig1 = px.scatter(state_agg, 
                              x="Origin State", y="Destination State",
                              size="avg_shipper_rate", color="avg_shipper_rate",
                              title="Top 5 Origin-Destination Pairs by Shipper Rate",
                              hover_name="Origin State", size_max=30,
                              text="avg_shipper_rate")  
            fig1.update_traces(textposition="top center")
            st.plotly_chart(fig1)

        ### **🔹 TAB 2: Transporter Discovery Dashboard**
        with tab2:
            st.header("🚛 Transporter Discovery Dashboard")

            ### **🔹 Transporter Performance Table**
            st.subheader("📌 Transporter Performance Summary")
            transporter_table = filtered_pricing.groupby(["Transporter"]).agg(
                Transporter_Rating=("Rating", "mean"),
                Total_Vehicles=("Shipper", "count"),
                Avg_ETA=("ETA", "mean"),
                Avg_Shipper_Rate=("Shipper", "mean")
            ).reset_index()
            st.dataframe(transporter_table)

            ### **🔹 Transporter Bubble Chart**
            st.subheader("📌 Transporter Performance by Origin-Destination")
            fig2 = px.scatter(filtered_pricing, 
                              x="Origin State", y="Destination State",
                              size="Shipper", color="Transporter",
                              title="Transporter Activity by Origin-Destination",
                              hover_name="Transporter", size_max=30,
                              text="Shipper")  
            fig2.update_traces(textposition="top center")
            st.plotly_chart(fig2)

        ### **🔹 TAB 3: EWB Dashboard**
        with tab3:
            st.header("📜 E-Way Bill Analysis for 2024")

            # ✅ Clickable External PDF Link
            st.markdown("""
            ### 📄 **E-Way Bill 3-Year Journey**
            👉 [Click here to view PDF](https://docs.ewaybillgst.gov.in/Documents/ewaybill3yearJourney.pdf)
            """)

            # ✅ EWB Bar Charts
            df_ewb_agg = df_ewb.groupby(["year", "type_of_supply"]).agg(
                total_value=("assessable_value", "sum"),
                total_ewaybills=("number_of_eway_bills", "sum")
            ).reset_index()

            # ✅ Chart 1: Yearly Assessable Value
            fig3 = px.bar(df_ewb_agg, x="year", y="total_value", color="type_of_supply",
                          title="Assessable Value YoY (Split by Supply Type)")
            st.plotly_chart(fig3)

            # ✅ Chart 2: Yearly Number of EWB
            fig4 = px.bar(df_ewb_agg, x="year", y="total_ewaybills", color="type_of_supply",
                          title="Number of EWB YoY (Split by Supply Type)")
            st.plotly_chart(fig4)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
