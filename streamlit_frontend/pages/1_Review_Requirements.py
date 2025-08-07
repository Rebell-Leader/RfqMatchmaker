
import streamlit as st
import requests
import json
import time
from datetime import datetime

# Constants
API_URL = "http://localhost:8000/api"

# Set page configuration
st.set_page_config(
    page_title="Review Requirements | RFQ Processor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .card {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">Step 1: Review Requirements</div>', unsafe_allow_html=True)
st.markdown("Review and confirm the extracted requirements before proceeding to supplier matching.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Check if we have an RFQ ID
if not st.session_state.rfq_id:
    st.warning("No RFQ has been uploaded or created. Please go back to Upload RFQ.")
    if st.button("Go to Upload RFQ", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
else:
    st.success("Requirements loaded successfully!")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Edit Requirements", use_container_width=True):
            st.info("Editing feature will be available in a future version.")
    
    with col2:
        if st.button("Confirm & Proceed to Matching", use_container_width=True):
            st.session_state.current_step = 3
            st.success("Requirements confirmed! Proceeding to supplier matching...")
            time.sleep(1)
            st.switch_page("pages/2_Match_Suppliers.py")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Upload", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
with col3:
    if st.button("Skip to Matching →", use_container_width=True):
        st.session_state.current_step = 3
        st.switch_page("pages/2_Match_Suppliers.py")
