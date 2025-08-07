
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
    page_icon="📧",
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
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">Step 5: Send Proposals</div>', unsafe_allow_html=True)
st.markdown("Generate and send email proposals to selected suppliers.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'selected_matches' not in st.session_state:
    st.session_state.selected_matches = []
if 'email_templates' not in st.session_state:
    st.session_state.email_templates = {}
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Function to generate email proposal
def generate_email_proposal(proposal_id):
    """Generate email proposal for a specific supplier match"""
    try:
        response = requests.post(f"{API_URL}/proposals/{proposal_id}/generate-email")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error generating email: {str(e)}")
        return None

# Check if we have selected matches
if not st.session_state.selected_matches:
    st.warning("No suppliers selected. Please go back to the scoring step.")
    if st.button("Go to Score Results", use_container_width=True):
        st.switch_page("pages/3_Score_Results.py")
else:
    selected_matches = st.session_state.selected_matches
    
    # Display summary
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Proposal Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Selected Suppliers", len(selected_matches))
    with col2:
        total_cost = sum(match['totalPrice'] for match in selected_matches)
        st.metric("Total Project Cost", f"${total_cost:,.2f}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Generate email proposals
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Email Proposals")
    
    for i, match in enumerate(selected_matches):
        supplier = match["supplier"]
        product = match["product"]
        
        st.markdown(f'<div class="email-card">', unsafe_allow_html=True)
        st.markdown(f"#### {i+1}. {supplier['name']} - {product['name']}")
        
        # Check if we already generated an email template for this match
        proposal_key = f"{supplier['id']}_{product['id']}"
        
        if proposal_key not in st.session_state.email_templates:
            # Create a default email template
            st.session_state.email_templates[proposal_key] = {
                "to": supplier.get('contactEmail', 'supplier@example.com'),
                "subject": f"RFQ Proposal Request - {product['name']}",
                "body": f"""Dear {supplier['name']} Team,

We are pleased to invite you to submit a proposal for our RFQ requirement.

Product Required: {product['name']}
Category: {product['category']}
Estimated Quantity: Based on our requirements

Your product has been identified as a potential match for our needs with a compatibility score of {match['matchScore']:.0f}%.

Please provide:
1. Detailed technical specifications
2. Pricing information
3. Delivery timeline
4. Warranty terms
5. Support services

We look forward to receiving your proposal.

Best regards,
Procurement Team"""
            }
        
        # Display and edit email template
        email_template = st.session_state.email_templates[proposal_key]
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(supplier.get('logoUrl', 'https://via.placeholder.com/150'), width=100)
            st.markdown(f"**{supplier['name']}**")
            st.markdown(f"**Email:** {supplier.get('contactEmail', 'N/A')}")
            st.markdown(f"**Score:** {match['matchScore']:.0f}%")
        
        with col2:
            # Email fields
            to_email = st.text_input("To", value=email_template['to'], key=f"to_{proposal_key}")
            subject = st.text_input("Subject", value=email_template['subject'], key=f"subject_{proposal_key}")
            body = st.text_area("Body", value=email_template['body'], height=300, key=f"body_{proposal_key}")
            
            # Update template with edited values
            email_template['to'] = to_email
            email_template['subject'] = subject
            email_template['body'] = body
        
        # Send email button (simulated)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Send Email Proposal", key=f"send_{proposal_key}"):
                st.success(f"Email proposal sent to {supplier['name']} at {email_template['to']}")
        
        with col2:
            if st.button("Download as PDF", key=f"pdf_{proposal_key}"):
                st.info("PDF download feature will be available in a future version.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Completion message
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎉 RFQ Process Complete!")
    st.markdown("""
    You have successfully:
    1. ✅ Uploaded and extracted requirements from an RFQ
    2. ✅ Reviewed the extracted requirements
    3. ✅ Matched suppliers based on your criteria
    4. ✅ Scored and selected the best suppliers
    5. ✅ Generated email proposals
    
    **Next Steps:**
    - Track email responses
    - Negotiate terms with suppliers
    - Finalize purchase orders
    - Manage delivery schedules
    """)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Start New RFQ Process", use_container_width=True):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/1_Upload_RFQ.py")
    
    with col2:
        if st.button("Export Summary Report", use_container_width=True):
            st.info("Report export feature will be available in a future version.")
    
    with col3:
        if st.button("Go to Dashboard", use_container_width=True):
            st.switch_page("Home.py")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Scores", use_container_width=True):
        st.switch_page("pages/3_Score_Results.py")
with col3:
    if st.button("Return to Home →", use_container_width=True):
        st.switch_page("Home.py")
