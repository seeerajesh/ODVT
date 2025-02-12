import os
import streamlit as st
import json

# Debug: Check if GOOGLE_CREDENTIALS is set
st.write("🔍 Checking Environment Variables...")

google_creds = os.getenv("GOOGLE_CREDENTIALS")

if google_creds:
    st.write("✅ Environment variable loaded successfully!")
    st.json(json.loads(google_creds))  # Display JSON (for debugging, remove later)
else:
    st.write("❌ ERROR: GOOGLE_CREDENTIALS not found in environment!")
