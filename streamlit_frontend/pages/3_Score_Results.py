
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
    }
    .high-score {
        border-left: 5px solid #4CAF50;
    }
    .medium-score {
        border-left: 5px solid #FF9800;
    }
    .low-score {
        border-left: 5px solid #F44336;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">Step 3: Score Results</div>', unsafe_allow_html=True)
st.markdown("Review the scoring results and select the best suppliers for your RFQ.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'supplier_matches' not in st.session_state:
    st.session_state.supplier_matches = None
if 'selected_matches' not in st.session_state:
    st.session_state.selected_matches = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

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

# Check if we have matches
if not st.session_state.supplier_matches:
    st.warning("No supplier matches found. Please go back to the matching step.")
    if st.button("Go to Match Suppliers", use_container_width=True):
        st.switch_page("pages/2_Match_Suppliers.py")
else:
    matches = st.session_state.supplier_matches
    
    # Display scoring summary
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Scoring Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Matches", len(matches))
    with col2:
        avg_score = sum(m["matchScore"] for m in matches) / len(matches)
        st.metric("Average Score", f"{avg_score:.1f}")
    with col3:
        best_score = max(m["matchScore"] for m in matches)
        st.metric("Best Score", f"{best_score:.1f}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display detailed results
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Detailed Results")
    
    # Sort matches by score
    sorted_matches = sorted(matches, key=lambda m: m["matchScore"], reverse=True)
    
    for i, match in enumerate(sorted_matches):
        supplier = match["supplier"]
        product = match["product"]
        score = match["matchScore"]
        details = match["matchDetails"]
        
        st.markdown(f'<div class="score-card {get_score_class(score)}">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
        
        with col1:
            st.markdown(f"**#{i+1}**")
            st.markdown(f"**Score: {score:.0f}**")
        
        with col2:
            st.markdown(f"**{supplier['name']}**")
            st.markdown(f"{product['name']}")
            st.markdown(f"Category: {product['category']}")
        
        with col3:
            st.markdown(f"**Price:** {format_currency(product['price'])}")
            st.markdown(f"**Total:** {format_currency(match['totalPrice'])}")
            st.markdown(f"**Delivery:** {supplier['deliveryTime']}")
        
        with col4:
            # Check if already selected
            is_selected = any(s["supplier"]["id"] == supplier["id"] and s["product"]["id"] == product["id"] 
                            for s in st.session_state.selected_matches)
            
            if is_selected:
                st.success("Selected ✓")
                if st.button("Deselect", key=f"deselect_{supplier['id']}_{product['id']}"):
                    st.session_state.selected_matches = [
                        s for s in st.session_state.selected_matches 
                        if not (s["supplier"]["id"] == supplier["id"] and s["product"]["id"] == product["id"])
                    ]
                    st.experimental_rerun()
            else:
                if st.button("Select", key=f"select_{supplier['id']}_{product['id']}"):
                    st.session_state.selected_matches.append(match)
                    st.experimental_rerun()
        
        # Score breakdown
        st.markdown("**Score Breakdown:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"Price: {details['price']:.0f}/100")
        with col2:
            st.markdown(f"Quality: {details['quality']:.0f}/100")
        with col3:
            st.markdown(f"Delivery: {details['delivery']:.0f}/100")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Selected suppliers section
    if st.session_state.selected_matches:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Selected Suppliers")
        
        total_cost = sum(match['totalPrice'] for match in st.session_state.selected_matches)
        st.markdown(f"**Total Cost:** {format_currency(total_cost)}")
        
        for i, match in enumerate(st.session_state.selected_matches):
            supplier = match["supplier"]
            product = match["product"]
            
            st.markdown(f"**{i+1}. {supplier['name']} - {product['name']}** (Score: {match['matchScore']:.0f})")
        
        # Proceed button
        if st.button("Proceed to Send Proposals", use_container_width=True):
            st.session_state.current_step = 5
            st.success("Proceeding to send proposals...")
            time.sleep(1)
            st.switch_page("pages/4_Send_Proposals.py")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Select at least one supplier to proceed to the next step.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Matching", use_container_width=True):
        st.switch_page("pages/2_Match_Suppliers.py")
with col3:
    if st.button("Skip to Proposals →", use_container_width=True):
        st.session_state.current_step = 5
        st.switch_page("pages/4_Send_Proposals.py")
