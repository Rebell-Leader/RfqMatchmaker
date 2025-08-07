import streamlit as st
import requests
import json
import time
from datetime import datetime

# Constants
API_URL = "http://localhost:8000/api"

# Set page configuration
st.set_page_config(
    page_title="Score Results | RFQ Processor",
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
    .score-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
    }
    .score-high {
        border-left: 5px solid #4CAF50;
        background-color: #f8fff8;
    }
    .score-medium {
        border-left: 5px solid #FF9800;
        background-color: #fff8f0;
    }
    .score-low {
        border-left: 5px solid #F44336;
        background-color: #fff5f5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'supplier_matches' not in st.session_state:
    st.session_state.supplier_matches = None
if 'selected_matches' not in st.session_state:
    st.session_state.selected_matches = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Title
st.markdown('<div class="main-title">Step 4: Score Results</div>', unsafe_allow_html=True)
st.markdown("Review the scored supplier matches and select the best options for your RFQ.")

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

def format_currency(amount):
    """Format a number as currency"""
    return f"${amount:,.2f}"

def get_score_class(score):
    """Get CSS class based on score"""
    if score >= 80:
        return "score-high"
    elif score >= 60:
        return "score-medium"
    else:
        return "score-low"

# Check if we have matches from previous step
if not st.session_state.rfq_id:
    st.warning("No RFQ has been uploaded or created. Please go back to Step 1.")
    if st.button("Go to Upload RFQ", use_container_width=True):
        st.switch_page("pages/1_Upload_RFQ.py")
elif not st.session_state.supplier_matches:
    st.warning("No supplier matches found. Please complete the supplier matching step first.")
    if st.button("Go to Match Suppliers", use_container_width=True):
        st.switch_page("pages/3_Match_Suppliers.py")
else:
    # Fetch RFQ data if not already in session state
    if not st.session_state.requirements:
        rfq_data = fetch_rfq_data()
    else:
        rfq_data = {"extractedRequirements": st.session_state.requirements}

    if rfq_data:
        requirements = rfq_data["extractedRequirements"]
        matches = st.session_state.supplier_matches

        # Display RFQ summary
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### RFQ Summary")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Title:** {requirements['title']}")
            st.markdown(f"**Total Matches Found:** {len(matches)}")

        with col2:
            criteria = requirements['criteria']
            st.markdown("**Scoring Criteria:**")
            st.markdown(f"- Price: {criteria['price']['weight']}%")
            st.markdown(f"- Quality: {criteria['quality']['weight']}%")
            st.markdown(f"- Delivery: {criteria['delivery']['weight']}%")

        st.markdown("</div>", unsafe_allow_html=True)

        # Filters and sorting
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Filter and Sort Results")

        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox("Category", 
                options=["All"] + list(set([m["product"]["category"] for m in matches])))

        with col2:
            sort_by = st.selectbox("Sort by", 
                options=["Match Score", "Price (Low to High)", "Price (High to Low)", "Quality Score", "Delivery Score"])

        with col3:
            min_score = st.slider("Minimum Score", 0, 100, 60)

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
        elif sort_by == "Quality Score":
            filtered_matches = sorted(filtered_matches, key=lambda m: m["matchDetails"]["quality"], reverse=True)
        elif sort_by == "Delivery Score":
            filtered_matches = sorted(filtered_matches, key=lambda m: m["matchDetails"]["delivery"], reverse=True)
        else:  # Default: Match Score
            filtered_matches = sorted(filtered_matches, key=lambda m: m["matchScore"], reverse=True)

        st.markdown(f"Showing {len(filtered_matches)} of {len(matches)} matches")
        st.markdown("</div>", unsafe_allow_html=True)

        # Display scored results
        if filtered_matches:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Scored Supplier Results")

            # Track selections
            if "final_selected_suppliers" not in st.session_state:
                st.session_state.final_selected_suppliers = []

            for i, match in enumerate(filtered_matches):
                supplier = match["supplier"]
                product = match["product"]
                score = match["matchScore"]
                details = match["matchDetails"]

                # Determine score class
                score_class = get_score_class(score)

                st.markdown(f'<div class="score-card {score_class}">', unsafe_allow_html=True)

                cols = st.columns([1, 4, 2, 1])

                with cols[0]:
                    st.image(supplier["logoUrl"], width=80)
                    st.markdown(f"**Score: {score:.0f}**")

                with cols[1]:
                    st.markdown(f"**{supplier['name']} - {product['name']}**")
                    st.markdown(f"Category: {product['category']}")
                    st.markdown(f"Description: {product['description'][:100]}...")

                    # Score breakdown
                    st.markdown("**Score Breakdown:**")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Price", f"{details['price']:.0f}/100")
                    with col_b:
                        st.metric("Quality", f"{details['quality']:.0f}/100")
                    with col_c:
                        st.metric("Delivery", f"{details['delivery']:.0f}/100")

                with cols[2]:
                    st.markdown(f"**Unit Price:** {format_currency(product['price'])}")
                    st.markdown(f"**Total Price:** {format_currency(match['totalPrice'])}")
                    st.markdown(f"**Delivery:** {supplier['deliveryTime']}")
                    st.markdown(f"**Warranty:** {product['warranty']}")

                with cols[3]:
                    # Selection checkbox
                    is_selected = any(s["supplier"]["id"] == supplier["id"] and s["product"]["id"] == product["id"] for s in st.session_state.final_selected_suppliers)

                    selected = st.checkbox("Select", value=is_selected, key=f"select_final_{supplier['id']}_{product['id']}")

                    if selected and not is_selected:
                        st.session_state.final_selected_suppliers.append(match)
                    elif not selected and is_selected:
                        st.session_state.final_selected_suppliers = [s for s in st.session_state.final_selected_suppliers 
                                                                     if not (s["supplier"]["id"] == supplier["id"] and s["product"]["id"] == product["id"])]

                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Selected suppliers summary
            if st.session_state.final_selected_suppliers:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### Selected Suppliers for Proposals")

                total_cost = sum(match["totalPrice"] for match in st.session_state.final_selected_suppliers)
                avg_score = sum(match["matchScore"] for match in st.session_state.final_selected_suppliers) / len(st.session_state.final_selected_suppliers)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Selected Suppliers", len(st.session_state.final_selected_suppliers))
                with col2:
                    st.metric("Total Estimated Cost", format_currency(total_cost))
                with col3:
                    st.metric("Average Score", f"{avg_score:.1f}")

                # List selected suppliers
                for i, match in enumerate(st.session_state.final_selected_suppliers):
                    supplier = match["supplier"]
                    product = match["product"]
                    st.markdown(f"{i+1}. **{supplier['name']}** - {product['name']} (Score: {match['matchScore']:.0f})")

                # Proceed button
                if st.button("Generate Proposals for Selected Suppliers", use_container_width=True):
                    st.session_state.current_step = 5
                    st.success("Proceeding to proposal generation...")
                    time.sleep(1)
                    st.switch_page("pages/5_Send_Proposals.py")

                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Select at least one supplier to proceed to proposal generation.")
        else:
            st.warning("No matches found with the current filters. Please adjust your criteria.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Matching", use_container_width=True):
        st.switch_page("pages/3_Match_Suppliers.py")
with col3:
    if st.button("Skip to Proposals →", use_container_width=True):
        st.session_state.current_step = 5
        st.switch_page("pages/5_Send_Proposals.py")