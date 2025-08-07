import streamlit as st
import requests
import json
import time
from datetime import datetime

# Constants
API_URL = "http://localhost:8000/api"

def fetch_rfq_data():
    """Fetch RFQ data from API"""
    if not st.session_state.rfq_id:
        return None
    
    try:
        response = requests.get(f"{API_URL}/rfqs/{st.session_state.rfq_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching RFQ data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def generate_proposal_email(proposal_id):
    """Generate email proposal for a specific proposal"""
    try:
        response = requests.post(f"{API_URL}/proposals/{proposal_id}/generate-email")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error generating email: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

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
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'final_selected_suppliers' not in st.session_state:
    st.session_state.final_selected_suppliers = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Title
st.markdown('<div class="main-title">Step 5: Send Proposals</div>', unsafe_allow_html=True)
st.markdown("Review and send customized proposals to your selected suppliers.")

# Check if we have required data
if not st.session_state.rfq_id:
    st.warning("No RFQ has been uploaded or created. Please go back to Step 1.")
    if st.button("Go to Upload RFQ", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
elif not st.session_state.final_selected_suppliers:
    st.warning("No suppliers have been selected. Please complete the scoring step first.")
    if st.button("Go to Score Results", use_container_width=True):
        st.switch_page("pages/4_Score_Results.py")
else:
    # Fetch RFQ data
    rfq_data = fetch_rfq_data()
    
    if rfq_data:
        requirements = rfq_data["extractedRequirements"]
        
        # Display RFQ summary
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### RFQ Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {requirements['title']}")
            st.markdown(f"**Description:** {requirements.get('description', 'N/A')}")
        
        with col2:
            st.markdown(f"**Categories:** {', '.join(requirements['categories'])}")
            st.markdown(f"**Selected Suppliers:** {len(st.session_state.final_selected_suppliers)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Generate and display proposals for each selected supplier
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Generated Proposals")
        
        for i, match in enumerate(st.session_state.final_selected_suppliers):
            supplier = match["supplier"]
            product = match["product"]
            
            st.markdown(f'<div class="email-card">', unsafe_allow_html=True)
            
            # Supplier header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{supplier['name']} - {product['name']}**")
                st.markdown(f"Match Score: {match['matchScore']:.0f}% | Total Price: ${match['totalPrice']:,.2f}")
            
            with col2:
                st.metric("Score", f"{match['matchScore']:.0f}%")
            
            # Email content (simplified for demo)
            email_to = f"sales@{supplier['name'].lower().replace(' ', '').replace(',', '').replace('.', '')}.com"
            email_subject = f"RFQ Response Required: {requirements['title']}"
            
            email_body = f"""Dear {supplier['name']} Team,

We are pleased to invite you to submit a quotation for our RFQ: {requirements['title']}.

Product Details:
- Product: {product['name']}
- Quantity: {requirements.get('laptops', {}).get('quantity', requirements.get('monitors', {}).get('quantity', 1))} units
- Unit Price: ${product['price']:,.2f}
- Total Estimated Value: ${match['totalPrice']:,.2f}

Your product has achieved a {match['matchScore']:.0f}% match score against our requirements, making you one of our preferred suppliers for this procurement.

Please confirm your availability and provide:
1. Formal quotation with final pricing
2. Delivery timeline
3. Warranty and support terms
4. Payment terms

We look forward to your response within 5 business days.

Best regards,
Procurement Team"""
            
            # Display email fields
            st.text_input("To:", value=email_to, key=f"to_{i}")
            st.text_input("Subject:", value=email_subject, key=f"subject_{i}")
            st.text_area("Message:", value=email_body, height=200, key=f"body_{i}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Send Email", key=f"send_{i}", use_container_width=True):
                    st.success(f"Proposal sent to {supplier['name']}!")
            with col2:
                if st.button("Save Draft", key=f"draft_{i}", use_container_width=True):
                    st.info(f"Draft saved for {supplier['name']}")
            with col3:
                if st.button("Download PDF", key=f"pdf_{i}", use_container_width=True):
                    st.info(f"PDF generated for {supplier['name']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Completion actions
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Complete Process")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Send All Proposals", use_container_width=True):
                # Simulate sending all proposals
                with st.spinner("Sending proposals..."):
                    time.sleep(2)
                st.success("All proposals have been sent successfully!")
                st.balloons()
                
                # Mark process as complete
                st.session_state.current_step = 6
                
        with col2:
            if st.button("Start New RFQ Process", use_container_width=True):
                # Clear session state and start over
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("Session cleared. Starting new process...")
                time.sleep(1)
                st.switch_page("pages/1_Upload_RFQ.py")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Failed to load RFQ data. Please try again or return to the previous step.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Scoring", use_container_width=True):
        st.switch_page("pages/4_Score_Results.py")
with col3:
    if st.button("Return to Home →", use_container_width=True):
        st.switch_page("Home.py")