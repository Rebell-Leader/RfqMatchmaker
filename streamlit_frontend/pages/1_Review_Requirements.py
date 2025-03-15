import streamlit as st
import requests
import json

# Set page config
st.set_page_config(
    page_title="Review RFQ Requirements",
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


def fetch_rfq_data():
    """Fetch RFQ data from API"""
    if not st.session_state.rfq_id:
        return None
    
    response = requests.get(f"{API_URL}/rfqs/{st.session_state.rfq_id}")
    if response.status_code == 200:
        return response.json()
    return None


# App header
st.title("📝 Review RFQ Requirements")

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
if st.session_state.rfq_id:
    rfq_data = fetch_rfq_data()
    
    if rfq_data:
        st.subheader(f"RFQ: {rfq_data['title']}")
        
        if rfq_data.get('description'):
            st.markdown(f"**Description:** {rfq_data['description']}")
        
        # Display extracted requirements
        requirements = rfq_data.get('extractedRequirements', {})
        
        st.header("Extracted Requirements")
        
        # Categories
        st.subheader("Product Categories")
        categories = requirements.get('categories', [])
        if categories:
            for category in categories:
                st.markdown(f"- {category}")
        else:
            st.warning("No categories extracted")
        
        # Award Criteria
        st.subheader("Award Criteria")
        criteria = requirements.get('criteria', {})
        
        # Create a bar chart for criteria weights
        if criteria:
            weights = {
                'Price': criteria.get('price', {}).get('weight', 0),
                'Quality': criteria.get('quality', {}).get('weight', 0),
                'Delivery': criteria.get('delivery', {}).get('weight', 0)
            }
            
            st.bar_chart(weights)
        else:
            st.warning("No award criteria extracted")
        
        # Laptop Requirements
        if 'laptops' in requirements and requirements['laptops']:
            st.subheader("Laptop Requirements")
            laptops = requirements['laptops']
            
            laptop_data = {
                "Quantity": laptops.get('quantity', 'Not specified'),
                "OS": laptops.get('os', 'Not specified'),
                "Processor": laptops.get('processor', 'Not specified'),
                "Memory": laptops.get('memory', 'Not specified'),
                "Storage": laptops.get('storage', 'Not specified'),
                "Display": laptops.get('display', 'Not specified'),
                "Battery": laptops.get('battery', 'Not specified'),
                "Durability": laptops.get('durability', 'Not specified'),
                "Connectivity": laptops.get('connectivity', 'Not specified'),
                "Warranty": laptops.get('warranty', 'Not specified')
            }
            
            # Create a two-column layout for laptop specs
            col1, col2 = st.columns(2)
            
            for i, (key, value) in enumerate(laptop_data.items()):
                if i % 2 == 0:
                    col1.markdown(f"**{key}:** {value}")
                else:
                    col2.markdown(f"**{key}:** {value}")
        
        # Monitor Requirements
        if 'monitors' in requirements and requirements['monitors']:
            st.subheader("Monitor Requirements")
            monitors = requirements['monitors']
            
            monitor_data = {
                "Quantity": monitors.get('quantity', 'Not specified'),
                "Screen Size": monitors.get('screenSize', 'Not specified'),
                "Resolution": monitors.get('resolution', 'Not specified'),
                "Panel Technology": monitors.get('panelTech', 'Not specified'),
                "Brightness": monitors.get('brightness', 'Not specified'),
                "Contrast Ratio": monitors.get('contrastRatio', 'Not specified'),
                "Connectivity": monitors.get('connectivity', 'Not specified'),
                "Adjustability": monitors.get('adjustability', 'Not specified'),
                "Warranty": monitors.get('warranty', 'Not specified')
            }
            
            # Create a two-column layout for monitor specs
            col1, col2 = st.columns(2)
            
            for i, (key, value) in enumerate(monitor_data.items()):
                if i % 2 == 0:
                    col1.markdown(f"**{key}:** {value}")
                else:
                    col2.markdown(f"**{key}:** {value}")
        
        # Original RFQ Content
        with st.expander("View Original RFQ Content"):
            st.text(rfq_data.get('originalContent', 'No content available'))
        
        # Navigation buttons
        st.divider()
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Back to Upload"):
                st.session_state.step = 1
                st.switch_page("Home.py")
        
        with col3:
            if st.button("Next: Match Suppliers →"):
                st.session_state.step = 3
                st.switch_page("pages/2_Match_Suppliers.py")
    
    else:
        st.error("Failed to load RFQ data")
        if st.button("Back to Home"):
            st.session_state.step = 1
            st.switch_page("Home.py")
else:
    st.warning("No RFQ selected. Please upload or create an RFQ first.")
    if st.button("Go to Upload"):
        st.session_state.step = 1
        st.switch_page("Home.py")

# Footer
st.divider()
st.caption("RFQ Supplier Matching Platform - Powered by AI")