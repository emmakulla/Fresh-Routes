import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import datetime

# Initialize sidebar
SideBarLinks()



st.title("Add New Produce")

# API endpoint
API_URL = "http://web-api:4000/Produce/Produce"

# Create a form for NGO details
with st.form("add_produce_form"):
    st.subheader("Required Produce Information")

    # Required fields
    produce_name = st.text_input("Produce Name *")
    harvest_date = st.text_input("Harvest Date *")
    quantity_available = st.text_input("Quantity *" )
    unit_available = st.text_input("Unit *")

    # Form submission button
    submitted = st.form_submit_button("Add Location")

    if submitted:
        # Validate required fields
        if not all([produce_name, harvest_date, quantity_available, unit_available]):
            st.error("Please fill in all required fields marked with *")
        else:
            # Prepare the data for API
            ngo_data = {
                "produce_name": produce_name,
                "harvest_date": harvest_date,
                "quantity_available": quantity_available,
                "unit_available": unit_available,
                "owner_id": st.session_state['user_id']
            }

            try:
                # Send POST request to API
                response = requests.post(API_URL, json=ngo_data)

                if response.status_code == 201:
                    st.success("Produce added successfully!")
                    # Clear the form
                    st.rerun()
                else:
                    st.error(
                        f"Failed to add Produce: {response.json().get('error', 'Unknown error')}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {str(e)}")
                st.info("Please ensure the API server is running")
