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
    .info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #1E88E5;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .spec-table {
        width: 100%;
        margin: 15px 0;
    }
    .spec-table th {
        background-color: #e3f2fd;
        padding: 8px;
        text-align: left;
    }
    .spec-table td {
        padding: 8px;
        border-bottom: 1px solid #e0e0e0;
    }
    .criteria-box {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">Step 2: Review Requirements</div>', unsafe_allow_html=True)
st.markdown("Review and confirm the extracted requirements before proceeding to supplier matching.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Function to fetch RFQ data
def fetch_rfq_data():
    """Fetch RFQ data from API"""
    if not st.session_state.rfq_id:
        return None
    
    try:
        response = requests.get(f"{API_URL}/rfqs/{st.session_state.rfq_id}")
        if response.status_code == 200:
            data = response.json()
            st.session_state.requirements = data["extractedRequirements"]
            return data
        else:
            st.error(f"Error fetching RFQ data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Check if we have an RFQ ID
if not st.session_state.rfq_id:
    st.warning("No RFQ has been uploaded or created. Please go back to Step 1.")
    if st.button("Go to Upload RFQ", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
else:
    # Fetch RFQ data if not already in session state
    rfq_data = fetch_rfq_data() if not st.session_state.requirements else {"extractedRequirements": st.session_state.requirements}
    
    if rfq_data:
        requirements = rfq_data["extractedRequirements"]
        
        # Display requirements summary
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### RFQ Overview")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {requirements['title']}")
            if requirements.get('description'):
                st.markdown(f"**Description:** {requirements['description']}")
        
        with col2:
            st.markdown(f"**Categories:** {', '.join(requirements['categories'])}")
            st.markdown(f"**RFQ ID:** {st.session_state.rfq_id}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display detailed requirements
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Detailed Requirements")
        
        # Laptops section
        if "Laptops" in requirements['categories'] and requirements.get('laptops'):
            laptop_reqs = requirements['laptops']
            st.markdown("#### Laptop Requirements")
            st.markdown(f"<div class='info-box'>Quantity: {laptop_reqs['quantity']} units</div>", unsafe_allow_html=True)
            
            st.markdown("<table class='spec-table'>", unsafe_allow_html=True)
            st.markdown("<tr><th>Specification</th><th>Requirement</th></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Operating System</td><td>{laptop_reqs['os']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Processor</td><td>{laptop_reqs['processor']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Memory</td><td>{laptop_reqs['memory']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Storage</td><td>{laptop_reqs['storage']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Display</td><td>{laptop_reqs['display']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Battery</td><td>{laptop_reqs['battery']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Durability</td><td>{laptop_reqs['durability']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Connectivity</td><td>{laptop_reqs['connectivity']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Warranty</td><td>{laptop_reqs['warranty']}</td></tr>", unsafe_allow_html=True)
            st.markdown("</table>", unsafe_allow_html=True)
        
        # Monitors section
        if "Monitors" in requirements['categories'] and requirements.get('monitors'):
            monitor_reqs = requirements['monitors']
            st.markdown("#### Monitor Requirements")
            st.markdown(f"<div class='info-box'>Quantity: {monitor_reqs['quantity']} units</div>", unsafe_allow_html=True)
            
            st.markdown("<table class='spec-table'>", unsafe_allow_html=True)
            st.markdown("<tr><th>Specification</th><th>Requirement</th></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Screen Size</td><td>{monitor_reqs['screenSize']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Resolution</td><td>{monitor_reqs['resolution']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Panel Technology</td><td>{monitor_reqs['panelTech']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Brightness</td><td>{monitor_reqs['brightness']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Contrast Ratio</td><td>{monitor_reqs['contrastRatio']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Connectivity</td><td>{monitor_reqs['connectivity']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Adjustability</td><td>{monitor_reqs['adjustability']}</td></tr>", unsafe_allow_html=True)
            st.markdown(f"<tr><td>Warranty</td><td>{monitor_reqs['warranty']}</td></tr>", unsafe_allow_html=True)
            st.markdown("</table>", unsafe_allow_html=True)
        
        # Award criteria section
        if requirements.get('criteria'):
            criteria = requirements['criteria']
            st.markdown("#### Award Criteria")
            
            st.markdown("<div class='criteria-box'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Price Weight", f"{criteria['price']['weight']}%")
            with col2:
                st.metric("Quality Weight", f"{criteria['quality']['weight']}%")
            with col3:
                st.metric("Delivery Weight", f"{criteria['delivery']['weight']}%")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Action buttons
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Edit Requirements", use_container_width=True):
                st.info("Editing feature will be available in a future version.")
        
        with col2:
            if st.button("Confirm & Proceed to Matching", use_container_width=True):
                st.session_state.current_step = 3
                st.success("Requirements confirmed! Proceeding to supplier matching...")
                time.sleep(1)
                st.switch_page("pages/3_Match_Suppliers.py")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Failed to load RFQ data. Please try again or return to the previous step.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Upload", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
with col3:
    if st.button("Skip to Matching →", use_container_width=True):
        st.session_state.current_step = 3
        st.switch_page("pages/3_Match_Suppliers.py")