import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI  # ✅ Correct OpenAI import for >=1.0.0

# ✅ Set Streamlit Page Title
st.set_page_config(page_title="Logistics & EWB Dashboard with Chatbot", layout="wide")
st.title("📊 Logistics & EWB Dashboard with Chatbot Support")

# ✅ Initialize OpenAI Client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    try:
        # ✅ Read data from both tabs
        df_pricing = pd.read_excel(uploaded_file, sheet_name="Collective Data", engine="openpyxl")
        df_ewb = pd.read_excel(uploaded_file, sheet_name="EWB", engine="openpyxl")

        # ✅ Convert "created_at" column to datetime format
        df_pricing["created_at"] = pd.to_datetime(df_pricing["created_at"])
        df_ewb["year"] = df_ewb["year"].astype(int)  

        # ✅ Streamlit Navigation Tabs
        tab1, tab2 = st.tabs(["📦 Logistics Pricing Dashboard", "📜 E-Way Bill Dashboard"])

        ### **🔹 TAB 1: Logistics Pricing Dashboard**
        with tab1:
            st.header("📦 Logistics Pricing Dashboard")

            # ✅ Sidebar Filters with Multi-Select & "Select All"
            st.sidebar.header("🔍 Filter Data")

            def multi_select_with_select_all(label, column_values):
                """Creates a multi-select filter with a 'Select All' option"""
                options = ["Select All"] + list(column_values)
                selected_values = st.sidebar.multiselect(label, options, default=["Select All"])

                # If "Select All" is chosen, return all options except "Select All"
                if "Select All" in selected_values:
                    return list(column_values)
                return selected_values

            origin_filter = multi_select_with_select_all("Select Origin Locality", df_pricing["Origin Locality"].unique())
            destination_filter = multi_select_with_select_all("Select Destination Locality", df_pricing["Destination Locality"].unique())
            vehicle_filter = multi_select_with_select_all("Select Truck Type", df_pricing["Truck type"].unique())
            origin_state_filter = multi_select_with_select_all("Select Origin State", df_pricing["Origin State"].unique())
            destination_state_filter = multi_select_with_select_all("Select Destination State", df_pricing["Destination State"].unique())
            transporter_filter = multi_select_with_select_all("Select Transporter", df_pricing["Transporter"].unique())

            # ✅ Date Range Filter
            date_range = st.sidebar.date_input("Select Date Range", 
                                               [df_pricing["created_at"].min().date(), df_pricing["created_at"].max().date()])
            start_date = pd.to_datetime(date_range[0])  
            end_date = pd.to_datetime(date_range[1])  

            # ✅ Apply Filters
            filtered_pricing = df_pricing[
                df_pricing["Origin Locality"].isin(origin_filter) &
                df_pricing["Destination Locality"].isin(destination_filter) &
                df_pricing["Truck type"].isin(vehicle_filter) &
                df_pricing["Origin State"].isin(origin_state_filter) &
                df_pricing["Destination State"].isin(destination_state_filter) &
                df_pricing["Transporter"].isin(transporter_filter) &
                df_pricing["created_at"].between(start_date, end_date)
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

            # ✅ Floating Chatbot Widget (Collapsible)
            with st.expander("💬 Open Chatbot"):
                st.subheader("AI Chatbot for Data Queries")

                # ✅ Initialize chat history
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                # ✅ Display chat history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # ✅ User input
                user_query = st.chat_input("Ask me about logistics data...")

                if user_query:
                    # ✅ Display user message in chat
                    st.session_state.messages.append({"role": "user", "content": user_query})
                    with st.chat_message("user"):
                        st.markdown(user_query)

                    try:
                        # ✅ Process query using OpenAI API (Fixed for latest version)
                        response = client.chat.completions.create(
                            model="gpt-4",  
                            messages=[
                                {"role": "system", "content": "You are a logistics assistant. Respond with relevant data insights from the provided DataFrame."},
                                {"role": "user", "content": user_query}
                            ]
                        )

                        bot_reply = response.choices[0].message.content  

                        # ✅ Display bot response
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                        with st.chat_message("assistant"):
                            st.markdown(bot_reply)

                    except Exception as e:
                        st.error(f"❌ Chatbot Error: {e}")

        ### **🔹 TAB 2: EWB Dashboard**
        with tab2:
            st.header("📜 E-Way Bill Analysis for 2024")
            st.markdown("""
            📄 **E-Way Bill 3-Year Journey Document:**  
            👉 [Click here to view the PDF](https://docs.ewaybillgst.gov.in/Documents/ewaybill3yearJourney.pdf)
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
