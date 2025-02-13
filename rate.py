import streamlit as st
import pandas as pd

# ✅ Step 1: Set Streamlit Title
st.title("📊 Local File Upload - Data Viewer")

# ✅ Step 2: Allow File Upload
uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["csv", "xls", "xlsx"])

# ✅ Step 3: Process File if Uploaded
if uploaded_file is not None:
    # Detect file type and read
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)  # Read CSV
    else:
        df = pd.read_excel(uploaded_file)  # Read Excel
    
    # ✅ Display Data Table
    st.write("### 📋 Data Preview:")
    st.dataframe(df)

    # ✅ Show Basic Info
    st.write("### 📊 Summary Statistics:")
    st.write(df.describe())

    # ✅ Allow Column Selection for Visualization
    column = st.selectbox("Select a column for line chart visualization", df.columns)

    # ✅ Show Line Chart
    st.write(f"### 📈 Line Chart for {column}")
    st.line_chart(df[column])

else:
    st.info("📂 Please upload a file to begin.")
