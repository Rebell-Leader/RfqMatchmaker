import streamlit as st
import requests
import json

# Set page config
st.set_page_config(
    page_title="Match Suppliers",
    page_icon="🔍",
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


def fetch_rfq_data():
    """Fetch RFQ data from API"""
    if not st.session_state.rfq_id:
        return None
    
    response = requests.get(f"{API_URL}/rfqs/{st.session_state.rfq_id}")
    if response.status_code == 200:
        return response.json()
    return None


def match_suppliers():
    """Match suppliers based on RFQ requirements"""
    if not st.session_state.rfq_id:
        return None
    
    response = requests.post(f"{API_URL}/rfqs/{st.session_state.rfq_id}/match-suppliers")
    if response.status_code == 200:
        return response.json()
    return None


# App header
st.title("🔍 Match Suppliers")

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
        
        # Display RFQ summary
        st.markdown("### RFQ Summary")
        
        requirements = rfq_data.get('extractedRequirements', {})
        
        # Create columns for summary display
        col1, col2 = st.columns(2)
        
        # Display categories
        with col1:
            st.markdown("**Categories:**")
            categories = requirements.get('categories', [])
            if categories:
                for category in categories:
                    st.markdown(f"- {category}")
            else:
                st.warning("No categories extracted")
        
        # Display award criteria
        with col2:
            st.markdown("**Award Criteria:**")
            criteria = requirements.get('criteria', {})
            if criteria:
                price_weight = criteria.get('price', {}).get('weight', 0)
                quality_weight = criteria.get('quality', {}).get('weight', 0)
                delivery_weight = criteria.get('delivery', {}).get('weight', 0)
                
                st.markdown(f"- Price: {price_weight}%")
                st.markdown(f"- Quality: {quality_weight}%")
                st.markdown(f"- Delivery: {delivery_weight}%")
            else:
                st.warning("No award criteria extracted")
        
        st.divider()
        
        # Match suppliers button
        if st.session_state.supplier_matches is None:
            if st.button("Find Matching Suppliers"):
                with st.spinner("Matching suppliers..."):
                    matches = match_suppliers()
                    if matches:
                        st.session_state.supplier_matches = matches
                        st.rerun()
                    else:
                        st.error("Failed to match suppliers")
        
        # Display supplier matches
        if st.session_state.supplier_matches:
            matches = st.session_state.supplier_matches.get('matches', [])
            
            if matches:
                st.success(f"Found {len(matches)} matching suppliers!")
                
                # Filter by category
                categories = requirements.get('categories', [])
                if categories:
                    selected_category = st.selectbox("Filter by Category", ["All"] + categories)
                    
                    if selected_category != "All":
                        filtered_matches = [m for m in matches if m['product']['category'] == selected_category]
                    else:
                        filtered_matches = matches
                else:
                    filtered_matches = matches
                
                # Sort options
                sort_by = st.selectbox("Sort by", ["Match Score", "Price", "Quality Score", "Delivery Score"])
                
                if sort_by == "Match Score":
                    filtered_matches = sorted(filtered_matches, key=lambda x: x['matchScore'], reverse=True)
                elif sort_by == "Price":
                    filtered_matches = sorted(filtered_matches, key=lambda x: x['totalPrice'])
                elif sort_by == "Quality Score":
                    filtered_matches = sorted(filtered_matches, key=lambda x: x['matchDetails']['quality'], reverse=True)
                elif sort_by == "Delivery Score":
                    filtered_matches = sorted(filtered_matches, key=lambda x: x['matchDetails']['delivery'], reverse=True)
                
                # Display matches
                st.markdown("### Matching Suppliers")
                
                for match in filtered_matches:
                    supplier = match['supplier']
                    product = match['product']
                    match_score = match['matchScore']
                    match_details = match['matchDetails']
                    total_price = match['totalPrice']
                    
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        # Display supplier logo if available
                        st.image(supplier.get('logoUrl', 'https://via.placeholder.com/150'), width=100)
                        st.markdown(f"**Match Score: {match_score:.1f}%**")
                    
                    with col2:
                        st.markdown(f"### {supplier['name']}")
                        st.markdown(f"**Product:** {product['name']} - **Category:** {product['category']}")
                        st.markdown(f"**Unit Price:** ${product['price']:.2f} - **Total Price:** ${total_price:.2f}")
                        st.markdown(f"**Delivery Time:** {supplier['deliveryTime']}")
                        
                        # Display score details
                        score_col1, score_col2, score_col3 = st.columns(3)
                        
                        with score_col1:
                            st.metric("Price Score", f"{match_details['price']:.1f}%")
                        
                        with score_col2:
                            st.metric("Quality Score", f"{match_details['quality']:.1f}%")
                        
                        with score_col3:
                            st.metric("Delivery Score", f"{match_details['delivery']:.1f}%")
                    
                    # Expander for product details
                    with st.expander("View Product Details"):
                        st.markdown(f"**Description:** {product['description']}")
                        
                        st.markdown("**Specifications:**")
                        for key, value in product.get('specifications', {}).items():
                            st.markdown(f"- **{key.capitalize()}:** {value}")
                        
                        st.markdown(f"**Warranty:** {product['warranty']}")
                    
                    st.divider()
                
                # Navigation buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if st.button("← Back to Review"):
                        st.session_state.step = 2
                        st.switch_page("pages/1_Review_Requirements.py")
                
                with col3:
                    if st.button("Next: Review Scores →"):
                        st.session_state.step = 4
                        st.switch_page("pages/3_Score_Results.py")
            else:
                st.warning("No matching suppliers found")
                if st.button("Try Again"):
                    st.session_state.supplier_matches = None
                    st.rerun()
    
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