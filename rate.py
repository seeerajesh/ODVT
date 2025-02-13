import streamlit as st
import pandas as pd

# ✅ Streamlit Title
st.title("📊 Local File Upload - Data Viewer")

# ✅ File Upload
uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)  # Read CSV
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")  # ✅ Explicitly use openpyxl
        
        # ✅ Display Data
        st.write("### 📋 Data Preview:")
        st.dataframe(df)

        # ✅ Show Summary Statistics
        st.write("### 📊 Summary Statistics:")
        st.write(df.describe())

        # ✅ Column Selection for Chart
        column = st.selectbox("Select a column for visualization", df.columns)
        st.line_chart(df[column])

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("📂 Please upload a CSV or Excel file.")
