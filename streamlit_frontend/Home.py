import streamlit as st
import requests
import json
import os
import time
from datetime import datetime

# Constants
API_URL = "http://localhost:8000/api"

# Set page configuration
st.set_page_config(
    page_title="RFQ Processor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.5rem;
        font-weight: 500;
        color: #424242;
        margin-bottom: 2rem;
    }
    .card {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .step-number {
        font-size: 1.2rem;
        font-weight: 700;
        color: white;
        background-color: #1E88E5;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E88E5;
    }
    .step-content {
        margin-left: 40px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown('<div class="main-title">B2B RFQ Processing Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Match supplier products with RFQ requirements and generate purchase proposals</div>', unsafe_allow_html=True)

def reset_app():
    """Reset the app to initial state"""
    # Clear session state
    st.session_state.rfq_id = None
    st.session_state.requirements = None
    st.session_state.supplier_matches = None
    st.session_state.selected_matches = None
    st.session_state.email_template = None
    st.session_state.current_step = 1
    
    # Display success message
    st.success("Application reset successfully. Start a new RFQ process.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'supplier_matches' not in st.session_state:
    st.session_state.supplier_matches = None
if 'selected_matches' not in st.session_state:
    st.session_state.selected_matches = None
if 'email_template' not in st.session_state:
    st.session_state.email_template = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
    
# Main content layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## Process Overview")
    st.markdown("This platform automates the B2B RFQ processing workflow, helping procurement teams find the best suppliers for their requirements and generate professional purchase proposals.")
    
    st.markdown("### 5-Step Workflow")
    
    # Step 1
    st.markdown('<span class="step-number">1</span><span class="step-title">Upload RFQ</span>', unsafe_allow_html=True)
    st.markdown('<div class="step-content">Upload an RFQ document or enter requirements manually. Our AI will extract key specifications.</div>', unsafe_allow_html=True)
    
    # Step 2
    st.markdown('<span class="step-number">2</span><span class="step-title">Review Requirements</span>', unsafe_allow_html=True)
    st.markdown('<div class="step-content">Review and edit the extracted requirements to ensure accuracy before proceeding.</div>', unsafe_allow_html=True)
    
    # Step 3
    st.markdown('<span class="step-number">3</span><span class="step-title">Match Suppliers</span>', unsafe_allow_html=True)
    st.markdown('<div class="step-content">Our system matches supplier products with your requirements, finding the best options.</div>', unsafe_allow_html=True)
    
    # Step 4
    st.markdown('<span class="step-number">4</span><span class="step-title">Score Results</span>', unsafe_allow_html=True)
    st.markdown('<div class="step-content">Review supplier matches, scored based on price, quality, and delivery time factors.</div>', unsafe_allow_html=True)
    
    # Step 5
    st.markdown('<span class="step-number">5</span><span class="step-title">Send Proposals</span>', unsafe_allow_html=True)
    st.markdown('<div class="step-content">Generate customized purchase proposals and email templates for selected suppliers.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## Get Started")
    
    if st.button("Start New RFQ Process", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
    
    if st.button("Reset Application", use_container_width=True):
        reset_app()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Status card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## Current Status")
    
    if st.session_state.rfq_id:
        st.success(f"RFQ ID: {st.session_state.rfq_id}")
        st.info(f"Current Step: {st.session_state.current_step}")
        
        if st.session_state.current_step > 1:
            st.info("Requirements extracted ✓")
        if st.session_state.current_step > 2:
            st.info("Suppliers matched ✓")
        if st.session_state.current_step > 3:
            st.info("Matches scored ✓")
        if st.session_state.current_step > 4:
            st.success("Proposals generated ✓")
    else:
        st.info("No active RFQ process. Click 'Start New RFQ Process' to begin.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("© 2023 RFQ Processor | Developed for Hackathon")