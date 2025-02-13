import streamlit as st
import json
from google.oauth2 import service_account

# ✅ Step 1: Paste Google Credentials Directly Here
GOOGLE_CREDENTIALS_JSON = """
{
    "type": "service_account",
    "project_id": "solid-scheme-450717-q8",
    "private_key_id": "f5d059394adf9d6f192c6068adf60d6564748882",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDC50uyrwLu+8wQ\npnjb/ZZzL2/YtdRySyJxA0RKl1orC4CxMLaqQG6//tz1GrO+vOrqvXZfuf/AWbP/\nhRL3qAZy1uiMZTXsAtlwET4ZawvZL2Qv0TA5Gt3tW5ItSmgqHz3V8edsknRHAR5w\nNPSVLbDrQ0nF729VuunKg0bQtlUV5q0jwGeU9hKGFAyxKCnxtDFvtsRXF+YxC0fN\nW88s50aB695u0Cz1kX+jo8BtBv31dp+tAFQP+5CxT1g8M593vMTnCjrUeMFixlbL\n/vcI8mBjvjDdL2U0b52IhJ6qVpkSURbhij8mzSyO8EHExlca9+80pdIEF2VqKBV/\nnYX7lT63AgMBAAECggEABI4V/yu061gzS6UuEX2PODjuhSwf2t318nV93ypn8Wzh\nLkwWgxQ+RvFtrvvp2H9oOKrwKu79rjxcveuHMCr2n55Q43Hzhk4rBy+u1TaHdQCZ\nnFDDnIoL2QZ5DnUzyd6DMPMNJKA6LZnITtRPJQY+jwtMwQMhvHuK4xT1Dszy8otm\n/IbXK4PuTv4Q3DaxBAky733V+6zKfOhmmroSkwRAWo1SoAcsHL1/wvuSmoFoV/QR\nlUNWyWe/GEu2cXqj+rz/0hhgVYlVJN8x3xBocVQe/EFMDh9i8MstYzOlkv1f+hIl\nwtcZQ3sntEkxnB2XoZdPFBXVAU56s4HNjna5Q3VHaQKBgQD+azMaWFtv1EXWCSXl\nk8jiDpfCmBN9U6WzklINE0ZR1w5CoW+8rLwS4tQwo49vhUWqHgHaBcy6bkKu2a23\nBj3sqzuftnp+sMx18qcW85N2IgWn2cVqy9X+tmPf3htCpgdUIfCSyjAWbKjL1UyZ\nGJLQCTGl4gcC/6SsDvJDDvBoLwKBgQDEHWcQsjfuuHnwgYWjHx82SdG+h6XXJP/Z\nEkAEReDopGzUoZV4beiM2OUSleDbQDBSA/tUGxIQmVOGdMl/3ojW4XVaROi9px1w\nS8zKB3OcpwhXQS6oD8fmacEzvNn1tI5Ez1W/v6uJe5vrhug6kfqc4Jb1WO/BPzME\nuqE0+Ttn+QKBgQC0ZEYDtAqBLD2oGSxpr3OL9VTdgP6wqhKfVGwhIT2G4bkWvWiA\nmulvaq2RHyegpxpSGJyvfdU/itZ1K5rkXuShXngUMkqAcdNG/hpDR8mSxWTFMr+r\njYPZ6nC+Vrl1dEtV+AqfygR2oey9OivpkWbnYt11BOJ72c9kv+Q+b+U9uQKBgAJq\nNkWvXB71aJL8lU+v52t8tzd4ZiNjEj9zCRTEY4OZ2rk3kCaee9mYJiH3dIBepvmr\nkOG1P6CysqOaNoz7iYXT2uUUqiUDtMoYNNpcAyFvsRuZ8uAg6Z49uSJQ9gIfigzw\n3KZyzsLvobjhvWRTPdnGrjUxNiqUA6XQQoHre77JAoGBAI+aV/RAS4+7Q2/pjq8A\n2t7eJmleYQhJRain1BxwtTk6sPB5PuET9FJvCOUGSLFZBvdXL/iL/+P1vQMJbkR7\n+94JOVQhBPKMK+OfL6NfTVrAqtIFKy22A7aMJ1WUfiVTghRyZMJ4vFACbtKeBPWL\nAGphVaYNcCN+PZMbVfJyWyvN\n-----END PRIVATE KEY-----\n",
    "client_email": "rateapi@solid-scheme-450717-q8.iam.gserviceaccount.com",
    "client_id": "102105676765134849082",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/rateapi%40solid-scheme-450717-q8.iam.gserviceaccount.com"
}
"""

st.title("Google Credentials Check ✅")

try:
    # ✅ Step 2: Try Parsing the Credentials
    creds_info = json.loads(GOOGLE_CREDENTIALS_JSON)
    credentials = service_account.Credentials.from_service_account_info(creds_info)
    
    # ✅ Step 3: Display Success Message
    st.success("✅ Google Credentials Loaded Successfully!")
    
except Exception as e:
    # ❌ If Credentials Fail, Show Error
    st.error("❌ Failed to Load Google Credentials!")
    st.write(e)
