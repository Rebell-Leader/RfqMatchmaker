import streamlit as st
import requests
import json
import time
import pandas as pd
import numpy as np
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
        transition: transform 0.2s;
    }
    .score-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .score-header {
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 5px;
    }
    .score-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }
    .score-label {
        font-weight: 500;
    }
    .score-value {
        font-weight: 700;
    }
    .high-score {
        color: #4CAF50;
    }
    .medium-score {
        color: #FF9800;
    }
    .low-score {
        color: #F44336;
    }
    .chart-container {
        height: 400px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">Step 4: Score Results</div>', unsafe_allow_html=True)
st.markdown("Review and compare the scores of selected supplier matches.")

# Initialize session state
if 'rfq_id' not in st.session_state:
    st.session_state.rfq_id = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'supplier_matches' not in st.session_state:
    st.session_state.supplier_matches = None
if 'selected_matches' not in st.session_state:
    st.session_state.selected_matches = None
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
        
        # Score comparison charts
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Score Comparison")
        
        # Prepare data for charts
        suppliers = [f"{m['supplier']['name']} - {m['product']['name']}" for m in selected_matches]
        scores = [m['matchScore'] for m in selected_matches]
        price_scores = [m['matchDetails']['price'] for m in selected_matches]
        quality_scores = [m['matchDetails']['quality'] for m in selected_matches]
        delivery_scores = [m['matchDetails']['delivery'] for m in selected_matches]
        prices = [m['totalPrice'] for m in selected_matches]
        
        # Create DataFrame for visualization
        data = pd.DataFrame({
            'Supplier': suppliers,
            'Total Score': scores,
            'Price Score': price_scores,
            'Quality Score': quality_scores,
            'Delivery Score': delivery_scores,
            'Total Price': prices
        })
        
        # Display total score chart
        st.markdown("#### Overall Match Score")
        st.bar_chart(data.set_index('Supplier')['Total Score'], height=300)
        
        # Display detailed score components
        st.markdown("#### Score Components")
        
        score_df = data[['Supplier', 'Price Score', 'Quality Score', 'Delivery Score']]
        score_df = score_df.set_index('Supplier')
        st.bar_chart(score_df, height=300)
        
        # Display price comparison
        st.markdown("#### Price Comparison")
        st.bar_chart(data.set_index('Supplier')['Total Price'], height=300)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Detailed scores for each supplier
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Detailed Scores")
        
        # Create table
        score_table = pd.DataFrame({
            'Supplier': suppliers,
            'Product': [m['product']['name'] for m in selected_matches],
            'Total Score': [f"{s:.1f}" for s in scores],
            'Price Score': [f"{s:.1f}" for s in price_scores],
            'Quality Score': [f"{s:.1f}" for s in quality_scores],
            'Delivery Score': [f"{s:.1f}" for s in delivery_scores],
            'Unit Price': [format_currency(m['product']['price']) for m in selected_matches],
            'Total Price': [format_currency(m['totalPrice']) for m in selected_matches],
            'Delivery Time': [m['supplier']['deliveryTime'] for m in selected_matches]
        })
        
        st.dataframe(score_table, use_container_width=True)
        
        # Recommendation based on highest score
        best_match_idx = scores.index(max(scores))
        best_match = selected_matches[best_match_idx]
        
        st.markdown("### Recommendation")
        st.markdown(f"Based on your requirements and award criteria, we recommend:")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(best_match['supplier']['logoUrl'], width=150)
        
        with col2:
            st.markdown(f"**{best_match['supplier']['name']} - {best_match['product']['name']}**")
            st.markdown(f"Match Score: **{best_match['matchScore']:.1f}**")
            st.markdown(f"Total Price: **{format_currency(best_match['totalPrice'])}**")
            st.markdown(f"Delivery Time: **{best_match['supplier']['deliveryTime']}**")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Action buttons
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Choose Different Suppliers", use_container_width=True):
                st.switch_page("pages/3_Match_Suppliers.py")
        
        with col2:
            if st.button("Generate Proposals", use_container_width=True):
                st.session_state.current_step = 5
                st.success("Proceeding to proposal generation...")
                time.sleep(1)
                st.switch_page("pages/5_Send_Proposals.py")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Failed to load RFQ data. Please try again or return to the previous step.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Matching", use_container_width=True):
        st.switch_page("pages/3_Match_Suppliers.py")
with col3:
    if st.button("Skip to Proposals →", use_container_width=True):
        st.session_state.current_step = 5
        st.switch_page("pages/5_Send_Proposals.py")