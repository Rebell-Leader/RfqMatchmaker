import streamlit as st
import requests
import json

# Mock functions (replace with actual implementations)
def fetch_rfq_data():
    # This function should fetch RFQ data based on st.session_state.rfq_id
    # For now, returning mock data
    return {
        "id": st.session_state.rfq_id,
        "title": "Sample RFQ Title",
        "description": "This is a sample RFQ description.",
        "suppliers": [
            {"name": "Supplier A", "id": 1},
            {"name": "Supplier B", "id": 2},
            {"name": "Supplier C", "id": 3},
        ]
    }

def send_proposals_to_suppliers(rfq_id, selected_suppliers):
    # This function should send proposals to the selected suppliers
    # For now, printing and returning a success message
    print(f"Sending proposals for RFQ {rfq_id} to suppliers: {selected_suppliers}")
    return {"message": "Proposals sent successfully!"}

# --- Page Configuration ---
st.set_page_config(page_title="Send Proposals", layout="wide")

st.title("Send Proposals")

# --- Workflow Logic ---
# Ensure RFQ ID and selected suppliers are available
if st.session_state.rfq_id and st.session_state.get('final_selected_suppliers'):
    rfq_data = fetch_rfq_data()

    if rfq_data:
        st.subheader(f"RFQ: {rfq_data['title']}")

        # Get selected suppliers from score results
        selected_suppliers = st.session_state.final_selected_suppliers

        st.write(f"You have selected {len(selected_suppliers)} suppliers to send proposals to:")
        for supplier_id in selected_suppliers:
            # Find supplier name from rfq_data for display
            supplier_name = "Unknown Supplier"
            for supplier in rfq_data.get("suppliers", []):
                if supplier["id"] == supplier_id:
                    supplier_name = supplier["name"]
                    break
            st.write(f"- {supplier_name} (ID: {supplier_id})")

        st.markdown("---")

        # Confirmation and Sending Proposals
        if st.button("Send Proposals"):
            try:
                response = send_proposals_to_suppliers(st.session_state.rfq_id, selected_suppliers)
                st.success(response.get("message", "Proposals sent successfully!"))

                # Clear session state related to this step and navigate to the next
                if 'rfq_id' in st.session_state:
                    del st.session_state.rfq_id
                if 'final_selected_suppliers' in st.session_state:
                    del st.session_state.final_selected_suppliers
                if 'step' in st.session_state:
                    del st.session_state.step

                st.info("You will be redirected to the next step automatically.")
                # Add a small delay or a button to proceed if auto-redirect is not desired
                # For example:
                if st.button("Go to Dashboard"):
                    st.switch_page("pages/0_Dashboard.py")

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while sending proposals: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

        # Navigation buttons
        if st.button("Back to Score Results"):
            st.switch_page("pages/4_Score_Results.py")

    else:
        st.error("Could not fetch RFQ data. Please try again.")
        if st.button("Back to Score Results"):
            st.switch_page("pages/4_Score_Results.py")

else:
    st.warning("No RFQ selected or suppliers not scored. Please complete the previous steps first.")
    if st.button("Go to Score Results"):
        st.switch_page("pages/4_Score_Results.py")