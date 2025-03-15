import streamlit as st
import requests
import json
import time
from datetime import datetime

# Constants
API_URL = "http://localhost:8000/api"

# Set page configuration
st.set_page_config(
    page_title="Send Proposals | RFQ Processor",
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
    .email-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .email-header {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .email-field {
        margin-bottom: 5px;
    }
    .email-label {
        font-weight: 700;
        display: inline-block;
        width: 80px;
    }
    .email-body {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 15px;
        background-color: white;
        font-family: Arial, sans-serif;
        white-space: pre-wrap;
    }
    .supplier-logo {
        width: 80px;
        height: 80px;
        object-fit: contain;
        border-radius: 50%;
        border: 1px solid #e0e0e0;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">Step 5: Send Proposals</div>', unsafe_allow_html=True)
st.markdown("Generate and customize email proposals for the selected suppliers.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'selected_matches' not in st.session_state:
    st.session_state.selected_matches = None
if 'email_templates' not in st.session_state:
    st.session_state.email_templates = {}
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

# Function to generate email proposal
def generate_email_proposal(proposal_id):
    """Generate email proposal for a specific supplier match"""
    try:
        response = requests.post(f"{API_URL}/proposals/{proposal_id}/generate-email")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error(f"Error generating email: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Check if we have an RFQ ID and selected matches
if not st.session_state.rfq_id:
    st.warning("No RFQ has been uploaded or created. Please go back to Step 1.")
    if st.button("Go to Upload RFQ", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
elif not st.session_state.selected_matches:
    st.warning("No supplier matches have been selected. Please go back to Step 3.")
    if st.button("Go to Match Suppliers", use_container_width=True):
        st.switch_page("pages/3_Match_Suppliers.py")
else:
    # Fetch RFQ data if not already in session state
    if not st.session_state.requirements:
        rfq_data = fetch_rfq_data()
    else:
        rfq_data = {"extractedRequirements": st.session_state.requirements}
    
    if rfq_data and st.session_state.selected_matches:
        requirements = rfq_data["extractedRequirements"]
        selected_matches = st.session_state.selected_matches
        
        # Display RFQ summary
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### RFQ Summary")
        
        st.markdown(f"**Title:** {requirements['title']}")
        st.markdown(f"**Selected Suppliers:** {len(selected_matches)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Generate email proposals
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Generate Email Proposals")
        
        if st.button("Generate All Email Proposals", use_container_width=True):
            with st.spinner("Generating email proposals..."):
                for match in selected_matches:
                    supplier_id = match["supplier"]["id"]
                    product_id = match["product"]["id"]
                    key = f"{supplier_id}_{product_id}"
                    
                    # Mock proposal ID (in a real app, this would come from the API)
                    # For this MVP, we'll use a combination of supplier_id and product_id
                    proposal_id = int(f"{supplier_id}{product_id}")
                    
                    # Generate email proposal
                    email_template = generate_email_proposal(proposal_id)
                    
                    if email_template:
                        st.session_state.email_templates[key] = email_template
                
                st.success(f"Generated {len(st.session_state.email_templates)} email proposals!")
                st.session_state.current_step = 5
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display email templates
        if st.session_state.email_templates:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Email Proposals")
            
            tabs = st.tabs([f"{m['supplier']['name']} - {m['product']['name']}" for m in selected_matches])
            
            for i, (tab, match) in enumerate(zip(tabs, selected_matches)):
                supplier = match["supplier"]
                product = match["product"]
                key = f"{supplier['id']}_{product['id']}"
                
                with tab:
                    if key in st.session_state.email_templates:
                        email = st.session_state.email_templates[key]
                        
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            st.image(supplier["logoUrl"], width=80)
                        
                        with col2:
                            st.markdown(f"**{supplier['name']} - {product['name']}**")
                            st.markdown(f"Contact: {supplier['contactEmail']} | {supplier['contactPhone']}")
                        
                        st.markdown('<div class="email-card">', unsafe_allow_html=True)
                        
                        # Email header
                        st.markdown('<div class="email-header">', unsafe_allow_html=True)
                        st.markdown(f'<div class="email-field"><span class="email-label">To:</span> {email["to"]}</div>', unsafe_allow_html=True)
                        if email.get("cc"):
                            st.markdown(f'<div class="email-field"><span class="email-label">Cc:</span> {email["cc"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="email-field"><span class="email-label">Subject:</span> {email["subject"]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Email body
                        st.markdown('<div class="email-body">', unsafe_allow_html=True)
                        st.markdown(email["body"].replace("\n", "<br>"), unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Edit email template
                        with st.expander("Edit Email"):
                            to_email = st.text_input("To", value=email["to"], key=f"to_{key}")
                            cc_email = st.text_input("Cc", value=email.get("cc", ""), key=f"cc_{key}")
                            subject = st.text_input("Subject", value=email["subject"], key=f"subject_{key}")
                            body = st.text_area("Body", value=email["body"], height=400, key=f"body_{key}")
                            
                            if st.button("Update Email", key=f"update_{key}"):
                                # Update email template in session state
                                st.session_state.email_templates[key] = {
                                    "to": to_email,
                                    "cc": cc_email if cc_email else None,
                                    "subject": subject,
                                    "body": body
                                }
                                st.success("Email updated!")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Preview", key=f"preview_{key}"):
                                st.info("Email preview functionality will be available in a future version.")
                        
                        with col2:
                            if st.button("Send", key=f"send_{key}"):
                                st.success(f"Email proposal sent to {email['to']}!")
                                # In a real app, this would actually send the email
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning(f"No email template generated yet for {supplier['name']} - {product['name']}.")
                        
                        # Generate single email button
                        if st.button("Generate Email", key=f"gen_{supplier['id']}_{product['id']}"):
                            with st.spinner("Generating email proposal..."):
                                # Mock proposal ID (in a real app, this would come from the API)
                                proposal_id = int(f"{supplier['id']}{product['id']}")
                                
                                # Generate email proposal
                                email_template = generate_email_proposal(proposal_id)
                                
                                if email_template:
                                    st.session_state.email_templates[key] = email_template
                                    st.success("Email proposal generated!")
                                    st.experimental_rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Bulk actions
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Bulk Actions")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Download All Proposals", use_container_width=True):
                    st.info("Download functionality will be available in a future version.")
            
            with col2:
                if st.button("Send All Proposals", use_container_width=True):
                    for key, email in st.session_state.email_templates.items():
                        st.success(f"Email proposal sent to {email['to']}!")
                    # In a real app, this would actually send the emails
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No email proposals have been generated yet. Click 'Generate All Email Proposals' to create them.")
    else:
        st.error("Failed to load RFQ data. Please try again or return to the previous step.")

# Process completion
if st.session_state.email_templates and len(st.session_state.email_templates) > 0:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Process Complete")
    st.success("Congratulations! You have successfully completed the RFQ processing workflow.")
    
    if st.button("Start New RFQ Process", use_container_width=True):
        # Reset session state
        st.session_state.rfq_id = None
        st.session_state.requirements = None
        st.session_state.supplier_matches = None
        st.session_state.selected_matches = None
        st.session_state.email_templates = {}
        st.session_state.current_step = 1
        
        # Navigate to home page
        st.switch_page("Home.py")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Navigation buttons
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("← Back to Score Results", use_container_width=True):
        st.switch_page("pages/4_Score_Results.py")
with col2:
    if st.button("Go to Home", use_container_width=True):
        st.switch_page("Home.py")