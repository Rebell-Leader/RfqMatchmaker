import streamlit as st
import requests
import json
import time
from datetime import datetime

# Constants
API_URL = "http://localhost:8000/api"

# Set page configuration
st.set_page_config(
    page_title="Match Suppliers | RFQ Processor",
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
    .supplier-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .supplier-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .supplier-logo {
        width: 100px;
        height: 100px;
        object-fit: contain;
        border-radius: 50%;
        border: 1px solid #e0e0e0;
        padding: 5px;
    }
    .score-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: #1E88E5;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0 auto;
    }
    .high-score {
        background-color: #4CAF50;
    }
    .medium-score {
        background-color: #FF9800;
    }
    .low-score {
        background-color: #F44336;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">Step 3: Match Suppliers</div>', unsafe_allow_html=True)
st.markdown("Match your RFQ requirements with potential suppliers and find the best product options.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'supplier_matches' not in st.session_state:
    st.session_state.supplier_matches = None
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

# Function to match suppliers
def match_suppliers():
    """Match suppliers based on RFQ requirements"""
    if not st.session_state.rfq_id:
        return None
    
    try:
        response = requests.post(f"{API_URL}/rfqs/{st.session_state.rfq_id}/match-suppliers")
        if response.status_code == 200:
            data = response.json()
            st.session_state.supplier_matches = data["matches"]
            return data["matches"]
        else:
            st.error(f"Error matching suppliers: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Function to format currency
def format_currency(amount):
    """Format a number as currency"""
    return f"${amount:,.2f}"

# Function to get CSS class for score
def get_score_class(score):
    """Get CSS class based on score"""
    if score >= 80:
        return "high-score"
    elif score >= 60:
        return "medium-score"
    else:
        return "low-score"

# Check if we have an RFQ ID
if not st.session_state.rfq_id:
    st.warning("No RFQ has been uploaded or created. Please go back to Step 1.")
    if st.button("Go to Upload RFQ", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
else:
    # Fetch RFQ data if not already in session state
    if not st.session_state.requirements:
        rfq_data = fetch_rfq_data()
    else:
        rfq_data = {"extractedRequirements": st.session_state.requirements}
    
    if rfq_data:
        requirements = rfq_data["extractedRequirements"]
        
        # Display RFQ summary
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### RFQ Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {requirements['title']}")
            st.markdown(f"**Categories:** {', '.join(requirements['categories'])}")
        
        with col2:
            st.markdown("**Award Criteria:**")
            criteria = requirements['criteria']
            st.markdown(f"- Price: {criteria['price']['weight']}%")
            st.markdown(f"- Quality: {criteria['quality']['weight']}%")
            st.markdown(f"- Delivery: {criteria['delivery']['weight']}%")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Match suppliers button
        if not st.session_state.supplier_matches:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.button("Find Matching Suppliers", use_container_width=True):
                with st.spinner("Matching suppliers with your requirements..."):
                    matches = match_suppliers()
                    if matches:
                        st.success(f"Found {len(matches)} potential supplier matches!")
                        # Force refresh
                        st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Display supplier matches
            matches = st.session_state.supplier_matches
            
            # Add filters
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Filter Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                category_filter = st.selectbox("Category", 
                    options=["All"] + list(set([m["product"]["category"] for m in matches])))
            
            with col2:
                sort_by = st.selectbox("Sort by", 
                    options=["Match Score", "Price (Low to High)", "Price (High to Low)"])
            
            with col3:
                min_score = st.slider("Minimum Score", 0, 100, 0)
            
            # Apply filters
            filtered_matches = matches
            if category_filter != "All":
                filtered_matches = [m for m in filtered_matches if m["product"]["category"] == category_filter]
            
            filtered_matches = [m for m in filtered_matches if m["matchScore"] >= min_score]
            
            # Apply sorting
            if sort_by == "Price (Low to High)":
                filtered_matches = sorted(filtered_matches, key=lambda m: m["totalPrice"])
            elif sort_by == "Price (High to Low)":
                filtered_matches = sorted(filtered_matches, key=lambda m: m["totalPrice"], reverse=True)
            else:  # Default: Match Score
                filtered_matches = sorted(filtered_matches, key=lambda m: m["matchScore"], reverse=True)
            
            st.markdown(f"Showing {len(filtered_matches)} of {len(matches)} matches")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display matches
            if filtered_matches:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### Supplier Matches")
                
                for match in filtered_matches:
                    supplier = match["supplier"]
                    product = match["product"]
                    score = match["matchScore"]
                    details = match["matchDetails"]
                    
                    st.markdown('<div class="supplier-card">', unsafe_allow_html=True)
                    cols = st.columns([1, 3, 2])
                    
                    with cols[0]:
                        st.image(supplier["logoUrl"], width=100, caption=supplier["name"])
                        st.markdown(f"<div class='score-circle {get_score_class(score)}'>{score:.0f}</div>", unsafe_allow_html=True)
                    
                    with cols[1]:
                        st.markdown(f"**{product['name']}**")
                        st.markdown(f"Category: {product['category']}")
                        st.markdown(f"Description: {product['description']}")
                        st.markdown(f"Warranty: {product['warranty']}")
                        
                        # Display key specifications
                        specs = product["specifications"]
                        if product["category"] == "Laptops":
                            st.markdown(f"OS: {specs.get('os', 'N/A')} | Processor: {specs.get('processor', 'N/A')} | Memory: {specs.get('memory', 'N/A')} | Storage: {specs.get('storage', 'N/A')}")
                        elif product["category"] == "Monitors":
                            st.markdown(f"Size: {specs.get('screenSize', 'N/A')} | Resolution: {specs.get('resolution', 'N/A')} | Panel: {specs.get('panelTech', 'N/A')}")
                    
                    with cols[2]:
                        st.markdown(f"**Unit Price:** {format_currency(product['price'])}")
                        
                        # Get quantity from requirements
                        quantity = 0
                        if product["category"] == "Laptops" and requirements.get("laptops"):
                            quantity = requirements["laptops"]["quantity"]
                        elif product["category"] == "Monitors" and requirements.get("monitors"):
                            quantity = requirements["monitors"]["quantity"]
                        
                        st.markdown(f"**Quantity:** {quantity}")
                        st.markdown(f"**Total Price:** {format_currency(match['totalPrice'])}")
                        st.markdown(f"**Delivery Time:** {supplier['deliveryTime']}")
                        
                        # Score details
                        st.markdown("**Score Details:**")
                        st.markdown(f"- Price: {details['price']:.0f}/100")
                        st.markdown(f"- Quality: {details['quality']:.0f}/100")
                        st.markdown(f"- Delivery: {details['delivery']:.0f}/100")
                        
                        # Select button
                        if st.button("Select", key=f"select_{supplier['id']}_{product['id']}"):
                            if "selected_matches" not in st.session_state:
                                st.session_state.selected_matches = []
                            
                            # Add to selected matches if not already there
                            if not any(s["supplier"]["id"] == supplier["id"] and s["product"]["id"] == product["id"] for s in st.session_state.selected_matches):
                                st.session_state.selected_matches.append(match)
                                st.success(f"{supplier['name']} - {product['name']} added to selected suppliers!")
                            else:
                                st.info(f"{supplier['name']} - {product['name']} is already selected.")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Selected suppliers section
                if "selected_matches" in st.session_state and st.session_state.selected_matches:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Selected Suppliers")
                    
                    for i, match in enumerate(st.session_state.selected_matches):
                        supplier = match["supplier"]
                        product = match["product"]
                        
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.markdown(f"**{i+1}. {supplier['name']} - {product['name']}**")
                        with col2:
                            st.markdown(f"Match Score: {match['matchScore']:.0f}")
                        with col3:
                            if st.button("Remove", key=f"remove_{supplier['id']}_{product['id']}"):
                                st.session_state.selected_matches.remove(match)
                                st.experimental_rerun()
                    
                    # Proceed button
                    if st.button("Proceed to Score Results", use_container_width=True):
                        st.session_state.current_step = 4
                        st.success("Proceeding to score results...")
                        time.sleep(1)
                        st.switch_page("pages/4_Score_Results.py")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("Select at least one supplier to proceed to the next step.")
            else:
                st.warning("No matches found with the current filters. Please adjust your criteria.")
    else:
        st.error("Failed to load RFQ data. Please try again or return to the previous step.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Requirements", use_container_width=True):
        st.switch_page("pages/2_Review_Requirements.py")
with col3:
    if st.button("Skip to Results →", use_container_width=True):
        st.session_state.current_step = 4
        st.switch_page("pages/4_Score_Results.py")