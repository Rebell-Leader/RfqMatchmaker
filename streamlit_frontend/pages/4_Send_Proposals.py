import streamlit as st
import requests
import json

# Set page config
st.set_page_config(
    page_title="Send Proposals",
    page_icon="📧",
    layout="wide"
)

# Define API URL
API_URL = "http://localhost:8000/api"

# Create session state variables if they don't exist
if "rfq_id" not in st.session_state:
    st.session_state.rfq_id = None

if "step" not in st.session_state:
    st.session_state.step = 1

if "supplier_matches" not in st.session_state:
    st.session_state.supplier_matches = None

if "selected_suppliers" not in st.session_state:
    st.session_state.selected_suppliers = []

if "email_templates" not in st.session_state:
    st.session_state.email_templates = {}


def fetch_rfq_data():
    """Fetch RFQ data from API"""
    if not st.session_state.rfq_id:
        return None
    
    response = requests.get(f"{API_URL}/rfqs/{st.session_state.rfq_id}")
    if response.status_code == 200:
        return response.json()
    return None


def generate_email_proposal(proposal_id):
    """Generate email proposal for a specific supplier match"""
    response = requests.post(f"{API_URL}/proposals/{proposal_id}/generate-email")
    if response.status_code == 200:
        return response.json()
    return None


# App header
st.title("📧 Send Proposals")

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
if st.session_state.rfq_id and st.session_state.selected_suppliers:
    rfq_data = fetch_rfq_data()
    
    if rfq_data:
        st.subheader(f"RFQ: {rfq_data['title']}")
        
        # Get selected suppliers
        selected_suppliers = st.session_state.selected_suppliers
        
        if selected_suppliers:
            st.markdown(f"### Generate Email Proposals for {len(selected_suppliers)} Selected Suppliers")
            
            # Generate email proposals
            for match in selected_suppliers:
                supplier = match['supplier']
                product = match['product']
                
                st.markdown(f"### {supplier['name']} - {product['name']}")
                
                # Check if we already generated an email template for this match
                proposal_key = f"{supplier['id']}_{product['id']}"
                
                if proposal_key not in st.session_state.email_templates:
                    # Find the proposal ID
                    proposals_response = requests.get(f"{API_URL}/rfqs/{st.session_state.rfq_id}/proposals")
                    
                    if proposals_response.status_code == 200:
                        proposals = proposals_response.json()
                        
                        # Find the proposal for this product
                        proposal_id = None
                        for proposal in proposals:
                            if proposal['productId'] == product['id']:
                                proposal_id = proposal['id']
                                break
                        
                        if proposal_id:
                            # Generate email
                            with st.spinner(f"Generating email proposal for {supplier['name']}..."):
                                email_template = generate_email_proposal(proposal_id)
                                
                                if email_template:
                                    st.session_state.email_templates[proposal_key] = email_template
                                else:
                                    st.error(f"Failed to generate email for {supplier['name']}")
                                    
                                    # Create a default template
                                    st.session_state.email_templates[proposal_key] = {
                                        "to": supplier['contactEmail'],
                                        "subject": f"RFQ: {rfq_data['title']}",
                                        "body": f"""Dear {supplier['name']} Team,

We are interested in your {product['name']} for our {rfq_data['title']} project. 

Please provide a formal quotation.

Best regards,
Procurement Team"""
                                    }
                        else:
                            st.error(f"No proposal found for {supplier['name']} - {product['name']}")
                    else:
                        st.error("Failed to load proposals")
                
                # Display and edit email template
                if proposal_key in st.session_state.email_templates:
                    email_template = st.session_state.email_templates[proposal_key]
                    
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.image(supplier.get('logoUrl', 'https://via.placeholder.com/150'), width=100)
                        st.markdown(f"**{supplier['name']}**")
                        st.markdown(f"**Email:** {supplier['contactEmail']}")
                    
                    with col2:
                        # Email fields
                        to_email = st.text_input("To", value=email_template['to'], key=f"to_{proposal_key}")
                        cc_email = st.text_input("CC", value=email_template.get('cc', ''), key=f"cc_{proposal_key}")
                        subject = st.text_input("Subject", value=email_template['subject'], key=f"subject_{proposal_key}")
                        body = st.text_area("Body", value=email_template['body'], height=300, key=f"body_{proposal_key}")
                        
                        # Update template with edited values
                        email_template['to'] = to_email
                        email_template['cc'] = cc_email
                        email_template['subject'] = subject
                        email_template['body'] = body
                    
                    # Send email button (simulated)
                    if st.button("Send Email Proposal", key=f"send_{proposal_key}"):
                        st.success(f"Email proposal sent to {supplier['name']} at {email_template['to']}")
                        
                        # In a real implementation, this would send the actual email
                        # For this MVP, we just simulate the sending
                
                st.divider()
            
            # Completion message
            st.markdown("### 🎉 RFQ Process Complete!")
            st.markdown("""
            You have successfully:
            1. ✅ Uploaded and extracted requirements from an RFQ
            2. ✅ Reviewed the extracted requirements
            3. ✅ Matched suppliers based on your criteria
            4. ✅ Scored and selected the best suppliers
            5. ✅ Generated email proposals
            
            In a full implementation, you would be able to:
            - Track email status and responses
            - Manage supplier negotiations
            - Finalize orders
            - Generate purchase orders
            """)
            
            # Navigation buttons
            st.divider()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("← Back to Scores"):
                    st.session_state.step = 4
                    st.switch_page("pages/3_Score_Results.py")
            
            with col3:
                if st.button("Start a New RFQ"):
                    # Reset all session state variables
                    st.session_state.rfq_id = None
                    st.session_state.step = 1
                    st.session_state.supplier_matches = None
                    st.session_state.selected_suppliers = []
                    st.session_state.email_templates = {}
                    st.switch_page("Home.py")
        else:
            st.warning("No suppliers selected")
            if st.button("Back to Score Results"):
                st.session_state.step = 4
                st.switch_page("pages/3_Score_Results.py")
    else:
        st.error("Failed to load RFQ data")
        if st.button("Back to Home"):
            st.session_state.step = 1
            st.switch_page("Home.py")
else:
    st.warning("No suppliers selected. Please complete the previous steps first.")
    if st.button("Go to Score Results"):
        st.session_state.step = 4
        st.switch_page("pages/3_Score_Results.py")

# Footer
st.divider()
st.caption("RFQ Supplier Matching Platform - Powered by AI")