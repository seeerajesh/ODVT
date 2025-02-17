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

        def multi_select_with_select_all(label, column_values, key):
            """Creates a multi-select filter with 'Select All' as default"""
            options = ["Select All"] + list(column_values)
            selected_values = st.sidebar.multiselect(label, options, default=["Select All"], key=key)
            return list(column_values) if "Select All" in selected_values else selected_values

        # ✅ Filters
        origin_filter = multi_select_with_select_all("Select Origin Locality", df_pricing["Origin Locality"].unique(), key="origin_filter")
        destination_filter = multi_select_with_select_all("Select Destination Locality", df_pricing["Destination Locality"].unique(), key="destination_filter")
        transporter_filter = multi_select_with_select_all("Select Transporter", df_pricing["Transporter"].unique(), key="transporter_filter")

        # ✅ Numeric Rating Filter (Multi-Select)
        rating_ranges = {
            "<2": df_pricing[df_pricing["Rating"] < 2]["Rating"],
            "2-3": df_pricing[(df_pricing["Rating"] >= 2) & (df_pricing["Rating"] < 3)]["Rating"],
            "3-4": df_pricing[(df_pricing["Rating"] >= 3) & (df_pricing["Rating"] < 4)]["Rating"],
            ">4": df_pricing[df_pricing["Rating"] >= 4]["Rating"]
        }
        selected_ratings = st.sidebar.multiselect("Select Transporter Rating", ["Select All", "<2", "2-3", "3-4", ">4"], default=["Select All"], key="rating_filter")

        if "Select All" in selected_ratings:
            selected_ratings = list(rating_ranges.keys())

        rating_filter_values = pd.concat([rating_ranges[r] for r in selected_ratings])

        # ✅ Date Range Selection (Default: 1 Year)
        date_options = {
            "Month to Date": datetime.today().replace(day=1),
            "3 Months": datetime.today() - timedelta(days=90),
            "6 Months": datetime.today() - timedelta(days=180),
            "1 Year": datetime.today() - timedelta(days=365),
            "Full Range": None  
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
            (df_pricing["Rating"].isin(rating_filter_values)) &
            (df_pricing["created_at"].between(start_date, end_date))
        ]

        ### **🔹 TAB 1: Overview Dashboard**
        with tab1:
            st.header("📦 Overview Dashboard")

            ### **🔹 Circle Chart 1: Total Shipper Rate Split by Rate Type**
            st.subheader("📌 Shipper Rate Split by Rate Type")
            rate_type_data = filtered_pricing.groupby("Rate type").agg(Total_Shipper_Rate=("Shipper", "sum")).reset_index()
            fig1 = px.pie(rate_type_data, names="Rate type", values="Total_Shipper_Rate", 
                          title="Total Shipper Rate Split by Rate Type", 
                          hover_data=["Total_Shipper_Rate"],
                          labels={"Rate type": "Rate Type", "Total_Shipper_Rate": "Total Shipper Rate"})
            fig1.update_traces(textinfo="percent+label", pull=[0.1, 0.1, 0.1])
            st.plotly_chart(fig1)

            ### **🔹 Circle Chart 2: Total Count of Vehicles Split by Category**
            st.subheader("📌 Vehicle Count Split by Category")
            category_data = filtered_pricing.groupby("Category").agg(Vehicle_Count=("Shipper", "count")).reset_index()
            fig2 = px.pie(category_data, names="Category", values="Vehicle_Count", 
                          title="Total Count of Vehicles Split by Category", 
                          hover_data=["Vehicle_Count"],
                          labels={"Category": "Category", "Vehicle_Count": "Vehicle Count"})
            fig2.update_traces(textinfo="percent+label", pull=[0.1, 0.1, 0.1])
            st.plotly_chart(fig2)

            ### **🔹 Origin → Destination Table**
            st.subheader("📌 Origin to Destination Rate Summary")
            od_table = filtered_pricing.groupby(["Origin Locality", "Destination Locality"]).agg(
                Avg_Shipper_Rate=("Shipper", "mean"),
                Avg_ETA=("ETA", "mean"),
                Avg_Toll_Cost=("Toll Cost", "mean"),
                Avg_Lead_Distance=("Lead Distance", "mean")
            ).reset_index()
            od_table = od_table.round(2)  # Round to 2 decimal places
            st.dataframe(od_table)

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
            transporter_table = transporter_table.round(2)  # Round to 2 decimal places
            st.dataframe(transporter_table)

            # ✅ Bubble Chart: Origin to Destination Trips (by Transporter)
            st.subheader("📌 Origin to Destination Transporter Performance")
            
            # Create the bubble chart data
            bubble_data = filtered_pricing.groupby(
                ["Origin State", "Destination State", "Transporter"]
            ).agg(
                Total_Trips=("Shipper", "count")
            ).reset_index()

            # Select origin and destination states via multi-select
            origin_states = bubble_data["Origin State"].unique()
            destination_states = bubble_data["Destination State"].unique()

            selected_origin_states = st.multiselect("Select Origin States", origin_states, default=origin_states)
            selected_destination_states = st.multiselect("Select Destination States", destination_states, default=destination_states)

            # Filter the bubble data
            bubble_filtered_data = bubble_data[
                (bubble_data["Origin State"].isin(selected_origin_states)) &
                (bubble_data["Destination State"].isin(selected_destination_states))
            ]

            # Create the bubble chart
            fig_bubble = px.scatter(
                bubble_filtered_data,
                x="Origin State", y="Destination State", size="Total_Trips", color="Transporter",
                hover_name="Transporter", hover_data=["Total_Trips"],
                title="Trips Between Origin and Destination States by Transporter",
                labels={"Origin State": "Origin State", "Destination State": "Destination State", "Total_Trips": "Number of Trips"}
            )
            fig_bubble.update_traces(marker=dict(sizemode="diameter", line=dict(width=2, color='DarkSlateGrey')))
            st.plotly_chart(fig_bubble)

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

            # ✅ Chart 3: Bubble Chart - Top 5 States by Assessable Value YoY
            top_states = ["Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka", "Uttar Pradesh"]
            df_states = df_ewb[df_ewb["state"].isin(top_states)].groupby(["year", "state"]).agg(total_value=("assessable_value", "sum")).reset_index()
            
            fig5 = px.scatter(df_states, x="year", y="state", size="total_value", color="state",
                              title="Top 5 States by Assessable Value YoY", text="total_value")
            fig5.update_traces(textposition="top center")
            st.plotly_chart(fig5)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
