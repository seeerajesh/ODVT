import streamlit as st
import json

# Debugging: Check if secrets are loading
st.write("🔍 Checking Streamlit Secrets...")

try:
    creds = st.secrets["GOOGLE_CREDENTIALS"]  # Fetch secrets
    st.write("✅ Secrets loaded successfully!")
    st.json(creds)  # Display secrets (for debugging, remove after testing)
except Exception as e:
    st.write("❌ Error loading secrets:", e)
