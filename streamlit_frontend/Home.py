import streamlit as st
import requests
import json
import base64

# Set page config
st.set_page_config(
    page_title="RFQ Supplier Matching",
    page_icon="📋",
    layout="wide"
)

# Define API URL
API_URL = "http://localhost:8000/api"

# Create session state variables if they don't exist
if "rfq_id" not in st.session_state:
    st.session_state.rfq_id = None

if "step" not in st.session_state:
    st.session_state.step = 1


def reset_app():
    """Reset the app to initial state"""
    st.session_state.rfq_id = None
    st.session_state.step = 1


# App header
st.title("🚀 RFQ Supplier Matching Platform")

st.markdown("""
Welcome to the RFQ Supplier Matching Platform! This tool allows you to:

1. Upload an RFQ document or enter details manually
2. Review and confirm extracted requirements
3. Match with suitable suppliers based on your criteria
4. Review and compare supplier scores
5. Generate and send email proposals to selected suppliers
""")

# Display the step progress
steps = ["Upload RFQ", "Review Requirements", "Match Suppliers", "Review Scores", "Send Proposals"]

col1, col2, col3, col4, col5 = st.columns(5)
cols = [col1, col2, col3, col4, col5]

for i, step in enumerate(steps, 1):
    if i < st.session_state.step:
        cols[i-1].markdown(f"#### ✅ **{i}. {step}**")
    elif i == st.session_state.step:
        cols[i-1].markdown(f"#### 🔄 **{i}. {step}**")
    else:
        cols[i-1].markdown(f"#### {i}. {step}")

st.divider()

# Main content
if st.session_state.step == 1:
    st.header("Upload Your RFQ")
    
    upload_tab, manual_tab = st.tabs(["Upload Document", "Enter Manually"])
    
    with upload_tab:
        uploaded_file = st.file_uploader("Upload RFQ document (TXT)", type=["txt"])
        
        if uploaded_file:
            st.success("File uploaded successfully")
            
            if st.button("Process RFQ"):
                with st.spinner("Extracting requirements..."):
                    files = {"file": uploaded_file}
                    response = requests.post(f"{API_URL}/rfqs/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.rfq_id = data.get("id")
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error(f"Error: {response.text}")
    
    with manual_tab:
        with st.form("manual_rfq_form"):
            title = st.text_input("RFQ Title")
            description = st.text_input("RFQ Description")
            specifications = st.text_area("RFQ Specifications", height=300)
            
            submit_button = st.form_submit_button("Process RFQ")
            
            if submit_button:
                if not title or not specifications:
                    st.error("Please enter a title and specifications")
                else:
                    with st.spinner("Extracting requirements..."):
                        payload = {
                            "title": title,
                            "description": description,
                            "specifications": specifications
                        }
                        
                        response = requests.post(f"{API_URL}/rfqs", json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.rfq_id = data.get("id")
                            st.session_state.step = 2
                            st.rerun()
                        else:
                            st.error(f"Error: {response.text}")

elif st.session_state.step > 1 and not st.session_state.rfq_id:
    st.warning("No RFQ selected. Please upload or create an RFQ first.")
    if st.button("Start Over"):
        reset_app()
        st.rerun()

# Footer
st.divider()
st.caption("RFQ Supplier Matching Platform - Powered by AI")
    
# Button to reset the app (for testing)
with st.sidebar:
    st.header("Navigation")
    if st.button("Reset Application"):
        reset_app()
        st.rerun()