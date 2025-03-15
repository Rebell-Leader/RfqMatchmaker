import streamlit as st
import requests
import json
import os
import time
import pandas as pd
from datetime import datetime

# Constants
API_URL = "http://localhost:8000/api"

# Set page configuration
st.set_page_config(
    page_title="Upload RFQ | RFQ Processor",
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
    .upload-area {
        border: 2px dashed #1E88E5;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">Step 1: Upload RFQ</div>', unsafe_allow_html=True)
st.markdown("Upload an RFQ document or enter requirements manually. Our AI will extract key specifications.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Function to upload RFQ file
def upload_rfq_file(file):
    try:
        # Create API request with file upload
        files = {'file': (file.name, file.getvalue(), 'text/plain')}
        response = requests.post(f"{API_URL}/rfqs/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.rfq_id = data["id"]
            st.session_state.current_step = 2
            return True, data["message"]
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

# Function to create RFQ manually
def create_rfq_manually(title, description, specifications):
    try:
        # Create API request with manual data
        data = {
            "title": title,
            "description": description,
            "specifications": specifications
        }
        
        response = requests.post(f"{API_URL}/rfqs", json=data)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.rfq_id = data["id"]
            st.session_state.current_step = 2
            return True, data["message"]
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

# Main content layout with tabs
tab1, tab2 = st.tabs(["Upload RFQ File", "Enter Requirements Manually"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Upload RFQ Document")
    st.markdown("Upload your Request for Quotation (RFQ) document. We support .txt, .docx, and .pdf files.")
    
    # File uploader
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx", "pdf"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        st.success(f"File {uploaded_file.name} uploaded successfully!")
        
        # Show file preview
        if uploaded_file.type == "text/plain":
            # Read as text
            file_contents = uploaded_file.getvalue().decode("utf-8")
            with st.expander("File Preview"):
                st.text(file_contents)
        
        # Upload button
        if st.button("Process RFQ", key="process_upload", use_container_width=True):
            with st.spinner("Processing RFQ..."):
                success, message = upload_rfq_file(uploaded_file)
                if success:
                    st.success(message)
                    # Navigate to next page after delay
                    time.sleep(2)
                    st.switch_page("pages/2_Review_Requirements.py")
                else:
                    st.error(message)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sample RFQ
    with st.expander("Use Sample RFQ"):
        st.markdown("For testing purposes, you can use our sample RFQ document.")
        if st.button("Use Sample RFQ", key="use_sample"):
            # Load sample RFQ file
            try:
                sample_path = "uploads/sample_rfq.txt"
                if os.path.exists(sample_path):
                    with open(sample_path, "r") as f:
                        sample_content = f.read()
                    
                    # Display sample content
                    st.text(sample_content)
                    
                    # Create file-like object
                    class SampleFile:
                        def __init__(self, content):
                            self.content = content
                            self.name = "sample_rfq.txt"
                        
                        def getvalue(self):
                            return self.content.encode("utf-8")
                    
                    sample_file = SampleFile(sample_content)
                    
                    # Process sample RFQ
                    with st.spinner("Processing sample RFQ..."):
                        success, message = upload_rfq_file(sample_file)
                        if success:
                            st.success(message)
                            # Navigate to next page after delay
                            time.sleep(2)
                            st.switch_page("pages/2_Review_Requirements.py")
                        else:
                            st.error(message)
                else:
                    st.error("Sample RFQ file not found.")
            except Exception as e:
                st.error(f"Error loading sample RFQ: {str(e)}")

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Enter Requirements Manually")
    st.markdown("Enter the RFQ requirements manually using the form below.")
    
    # Manual input form
    title = st.text_input("RFQ Title", placeholder="e.g., Supply and Delivery of Laptops and Monitors")
    description = st.text_area("Description", placeholder="Brief description of the RFQ...")
    
    # Specifications form
    st.markdown("#### Technical Specifications")
    
    # Categories
    categories = st.multiselect(
        "Product Categories", 
        options=["Laptops", "Monitors", "Printers", "Servers", "Networking", "Other"],
        default=["Laptops"]
    )
    
    specs_text = ""
    
    # Laptop specs if selected
    if "Laptops" in categories:
        st.markdown("##### Laptop Specifications")
        laptop_col1, laptop_col2 = st.columns(2)
        
        with laptop_col1:
            laptop_quantity = st.number_input("Quantity", min_value=1, value=30)
            laptop_os = st.text_input("Operating System", value="Windows 11 Pro")
            laptop_processor = st.text_input("Processor", value="Intel Core i5 11th gen")
            laptop_memory = st.text_input("Memory", value="16GB DDR4")
            laptop_storage = st.text_input("Storage", value="512GB SSD")
        
        with laptop_col2:
            laptop_display = st.text_input("Display", value="14-inch FHD (1920 x 1080)")
            laptop_battery = st.text_input("Battery", value="8+ hours")
            laptop_durability = st.text_input("Durability", value="MIL-STD-810H tested")
            laptop_connectivity = st.text_input("Connectivity", value="Wi-Fi 6, Bluetooth 5.0")
            laptop_warranty = st.text_input("Warranty", value="3 years onsite")
        
        # Add to specs text
        specs_text += f"Laptop Requirements:\n"
        specs_text += f"- Quantity: {laptop_quantity} units\n"
        specs_text += f"- Operating System: {laptop_os}\n"
        specs_text += f"- Processor: {laptop_processor}\n"
        specs_text += f"- Memory: {laptop_memory}\n"
        specs_text += f"- Storage: {laptop_storage}\n"
        specs_text += f"- Display: {laptop_display}\n"
        specs_text += f"- Battery: {laptop_battery}\n"
        specs_text += f"- Durability: {laptop_durability}\n"
        specs_text += f"- Connectivity: {laptop_connectivity}\n"
        specs_text += f"- Warranty: {laptop_warranty}\n\n"
    
    # Monitor specs if selected
    if "Monitors" in categories:
        st.markdown("##### Monitor Specifications")
        monitor_col1, monitor_col2 = st.columns(2)
        
        with monitor_col1:
            monitor_quantity = st.number_input("Quantity", min_value=1, value=30, key="monitor_quantity")
            monitor_size = st.text_input("Screen Size", value="27 inches")
            monitor_resolution = st.text_input("Resolution", value="2K QHD (2560 x 1440)")
            monitor_panel = st.text_input("Panel Technology", value="IPS")
            monitor_brightness = st.text_input("Brightness", value="300 cd/m² or higher")
        
        with monitor_col2:
            monitor_contrast = st.text_input("Contrast Ratio", value="1000:1 or higher")
            monitor_connectivity = st.text_input("Connectivity", value="HDMI, DisplayPort, USB-C")
            monitor_adjustability = st.text_input("Adjustability", value="Height, tilt, swivel adjustable")
            monitor_warranty = st.text_input("Warranty", value="3 years standard")
        
        # Add to specs text
        specs_text += f"Monitor Requirements:\n"
        specs_text += f"- Quantity: {monitor_quantity} units\n"
        specs_text += f"- Screen Size: {monitor_size}\n"
        specs_text += f"- Resolution: {monitor_resolution}\n"
        specs_text += f"- Panel Technology: {monitor_panel}\n"
        specs_text += f"- Brightness: {monitor_brightness}\n"
        specs_text += f"- Contrast Ratio: {monitor_contrast}\n"
        specs_text += f"- Connectivity: {monitor_connectivity}\n"
        specs_text += f"- Adjustability: {monitor_adjustability}\n"
        specs_text += f"- Warranty: {monitor_warranty}\n\n"
    
    # Award criteria
    st.markdown("##### Award Criteria")
    price_weight = st.slider("Price Weight (%)", min_value=0, max_value=100, value=50)
    quality_weight = st.slider("Quality Weight (%)", min_value=0, max_value=100, value=30)
    delivery_weight = st.slider("Delivery Weight (%)", min_value=0, max_value=100, value=20)
    
    # Add to specs text
    specs_text += f"Award Criteria:\n"
    specs_text += f"- Price: {price_weight}%\n"
    specs_text += f"- Quality: {quality_weight}%\n"
    specs_text += f"- Delivery: {delivery_weight}%\n"
    
    # Preview specifications
    with st.expander("Preview Specifications"):
        st.code(specs_text)
    
    # Submit button
    if st.button("Process Requirements", key="process_manual", use_container_width=True):
        if not title:
            st.error("Please enter an RFQ title.")
        elif not categories:
            st.error("Please select at least one product category.")
        else:
            with st.spinner("Processing requirements..."):
                success, message = create_rfq_manually(title, description, specs_text)
                if success:
                    st.success(message)
                    # Navigate to next page after delay
                    time.sleep(2)
                    st.switch_page("pages/2_Review_Requirements.py")
                else:
                    st.error(message)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("Home.py")
with col3:
    if st.button("Skip to Review →", use_container_width=True):
        st.switch_page("pages/2_Review_Requirements.py")