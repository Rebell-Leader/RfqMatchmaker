import streamlit as st
import requests
import json
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(
    page_title="Score Results",
    page_icon="📊",
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


def fetch_rfq_data():
    """Fetch RFQ data from API"""
    if not st.session_state.rfq_id:
        return None
    
    response = requests.get(f"{API_URL}/rfqs/{st.session_state.rfq_id}")
    if response.status_code == 200:
        return response.json()
    return None


# App header
st.title("📊 Score Results")

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
if st.session_state.rfq_id and st.session_state.supplier_matches:
    rfq_data = fetch_rfq_data()
    
    if rfq_data and st.session_state.supplier_matches:
        st.subheader(f"RFQ: {rfq_data['title']}")
        
        # Get matches
        matches = st.session_state.supplier_matches.get('matches', [])
        
        if matches:
            # Get categories
            categories = rfq_data.get('extractedRequirements', {}).get('categories', [])
            
            # Group suppliers by category
            suppliers_by_category = {}
            
            for category in categories:
                suppliers_by_category[category] = [m for m in matches if m['product']['category'] == category]
            
            # Create tabs for each category
            if categories:
                tabs = st.tabs(categories)
                
                for i, category in enumerate(categories):
                    with tabs[i]:
                        category_matches = suppliers_by_category[category]
                        
                        if category_matches:
                            st.markdown(f"### Top Suppliers for {category}")
                            
                            # Create a comparison table
                            comparison_data = []
                            
                            for match in category_matches:
                                supplier = match['supplier']
                                product = match['product']
                                
                                comparison_data.append({
                                    "Supplier": supplier['name'],
                                    "Product": product['name'],
                                    "Match Score": f"{match['matchScore']:.1f}%",
                                    "Price Score": f"{match['matchDetails']['price']:.1f}%",
                                    "Quality Score": f"{match['matchDetails']['quality']:.1f}%",
                                    "Delivery Score": f"{match['matchDetails']['delivery']:.1f}%",
                                    "Unit Price": f"${product['price']:.2f}",
                                    "Total Price": f"${match['totalPrice']:.2f}",
                                    "Delivery Time": supplier['deliveryTime'],
                                    "data": match  # Store the original data for later use
                                })
                            
                            # Create DataFrame for display
                            df = pd.DataFrame(comparison_data)
                            display_df = df.drop(columns=['data'])
                            
                            st.dataframe(display_df, use_container_width=True)
                            
                            # Create a radar chart for the top 3 suppliers
                            st.markdown("### Comparison Chart (Top 3 Suppliers)")
                            
                            # Sort by match score and get top 3
                            top_matches = sorted(category_matches, key=lambda x: x['matchScore'], reverse=True)[:3]
                            
                            # Create a chart using Streamlit
                            chart_data = pd.DataFrame({
                                'Metric': ['Price', 'Quality', 'Delivery'],
                                top_matches[0]['supplier']['name']: [
                                    top_matches[0]['matchDetails']['price'],
                                    top_matches[0]['matchDetails']['quality'],
                                    top_matches[0]['matchDetails']['delivery']
                                ]
                            })
                            
                            # Add data for other suppliers
                            for i in range(1, len(top_matches)):
                                chart_data[top_matches[i]['supplier']['name']] = [
                                    top_matches[i]['matchDetails']['price'],
                                    top_matches[i]['matchDetails']['quality'],
                                    top_matches[i]['matchDetails']['delivery']
                                ]
                            
                            # Set the 'Metric' column as the index
                            chart_data = chart_data.set_index('Metric')
                            
                            # Display the chart
                            st.bar_chart(chart_data)
                            
                            # Select suppliers
                            st.markdown("### Select Suppliers for Proposals")
                            
                            for i, match in enumerate(category_matches):
                                supplier = match['supplier']
                                product = match['product']
                                
                                key = f"{category}_{supplier['id']}_{product['id']}"
                                
                                selected = st.checkbox(
                                    f"Select {supplier['name']} - {product['name']} (Match: {match['matchScore']:.1f}%)",
                                    key=key
                                )
                                
                                # Update selected suppliers list
                                if selected:
                                    if match not in st.session_state.selected_suppliers:
                                        st.session_state.selected_suppliers.append(match)
                                else:
                                    if match in st.session_state.selected_suppliers:
                                        st.session_state.selected_suppliers.remove(match)
                            
                        else:
                            st.warning(f"No suppliers found for {category}")
            else:
                # If no categories, display all matches
                st.markdown("### Top Suppliers")
                
                # Create a comparison table
                comparison_data = []
                
                for match in matches:
                    supplier = match['supplier']
                    product = match['product']
                    
                    comparison_data.append({
                        "Supplier": supplier['name'],
                        "Product": product['name'],
                        "Category": product['category'],
                        "Match Score": f"{match['matchScore']:.1f}%",
                        "Price Score": f"{match['matchDetails']['price']:.1f}%",
                        "Quality Score": f"{match['matchDetails']['quality']:.1f}%",
                        "Delivery Score": f"{match['matchDetails']['delivery']:.1f}%",
                        "Unit Price": f"${product['price']:.2f}",
                        "Total Price": f"${match['totalPrice']:.2f}",
                        "Delivery Time": supplier['deliveryTime'],
                        "data": match  # Store the original data for later use
                    })
                
                # Create DataFrame for display
                df = pd.DataFrame(comparison_data)
                display_df = df.drop(columns=['data'])
                
                st.dataframe(display_df, use_container_width=True)
                
                # Select suppliers
                st.markdown("### Select Suppliers for Proposals")
                
                for i, match in enumerate(matches):
                    supplier = match['supplier']
                    product = match['product']
                    
                    key = f"all_{supplier['id']}_{product['id']}"
                    
                    selected = st.checkbox(
                        f"Select {supplier['name']} - {product['name']} (Match: {match['matchScore']:.1f}%)",
                        key=key
                    )
                    
                    # Update selected suppliers list
                    if selected:
                        if match not in st.session_state.selected_suppliers:
                            st.session_state.selected_suppliers.append(match)
                    else:
                        if match in st.session_state.selected_suppliers:
                            st.session_state.selected_suppliers.remove(match)
            
            # Display selected suppliers summary
            if st.session_state.selected_suppliers:
                st.divider()
                st.markdown(f"### Selected Suppliers: {len(st.session_state.selected_suppliers)}")
                
                for match in st.session_state.selected_suppliers:
                    supplier = match['supplier']
                    product = match['product']
                    
                    st.markdown(f"- {supplier['name']} - {product['name']} (Match: {match['matchScore']:.1f}%)")
            
            # Navigation buttons
            st.divider()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("← Back to Matches"):
                    st.session_state.step = 3
                    st.switch_page("pages/2_Match_Suppliers.py")
            
            with col3:
                if st.session_state.selected_suppliers:
                    if st.button("Next: Send Proposals →"):
                        st.session_state.step = 5
                        st.switch_page("pages/4_Send_Proposals.py")
                else:
                    st.warning("Please select at least one supplier to continue")
        else:
            st.warning("No supplier matches found")
            if st.button("Back to Match Suppliers"):
                st.session_state.step = 3
                st.switch_page("pages/2_Match_Suppliers.py")
    else:
        st.error("Failed to load data")
        if st.button("Back to Home"):
            st.session_state.step = 1
            st.switch_page("Home.py")
else:
    st.warning("No matches available. Please complete the previous steps first.")
    if st.button("Go to Match Suppliers"):
        st.session_state.step = 3
        st.switch_page("pages/2_Match_Suppliers.py")

# Footer
st.divider()
st.caption("RFQ Supplier Matching Platform - Powered by AI")