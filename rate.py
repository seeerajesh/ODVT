import streamlit as st
import pandas as pd
import plotly.express as px
import openai  # Chatbot API

# ✅ Set Streamlit Page Title
st.set_page_config(page_title="Logistics & EWB Dashboard with Chatbot", layout="wide")
st.title("📊 Logistics Pricing & EWB Dashboard with Chatbot Support")

# ✅ Load OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
        tab1, tab2, tab3 = st.tabs(["📦 Logistics Pricing Dashboard", "📜 E-Way Bill Dashboard", "💬 Chatbot"])

        ### **🔹 TAB 1: Logistics Pricing Dashboard**
        with tab1:
            st.header("📦 Logistics Pricing Dashboard")
            st.write("Use filters to explore logistics data.")

        ### **🔹 TAB 2: EWB Dashboard**
        with tab2:
            st.header("📜 E-Way Bill Analysis for 2024")
            st.markdown("""
            📄 **E-Way Bill 3-Year Journey Document:**  
            👉 [Click here to view the PDF](https://docs.ewaybillgst.gov.in/Documents/ewaybill3yearJourney.pdf)
            """, unsafe_allow_html=True)

        ### **🔹 TAB 3: Chatbot**
        with tab3:
            st.header("💬 AI Chatbot for Data Queries")

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

                # ✅ Process query using OpenAI API
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # GPT-4 for better accuracy
                    messages=[
                        {"role": "system", "content": "You are a logistics assistant. Respond with relevant data insights from the provided DataFrame."},
                        {"role": "user", "content": user_query}
                    ]
                )

                bot_reply = response["choices"][0]["message"]["content"]

                # ✅ Display bot response
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload an Excel file.")
