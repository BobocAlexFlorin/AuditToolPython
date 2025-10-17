import streamlit as st
from datetime import datetime
from utils.auth import get_user_auth
from utils.audit_manager import AuditManager
from utils.email_utils import send_responsible_email

st.set_page_config(page_title="New Audit", layout="wide")

# Area categories and subcategories
AREAS = {
    "Quality": ["Assembly", "Packaging", "Quality Control"],
    "Maintenance": ["Preventive", "Corrective", "Predictive"],
    "Curing": ["Warehouse", "Transportation", "Inventory"],
    "Office": ["Admin", "HR", "IT"]
}

def main():
    authenticated, user_role, username = get_user_auth()
    
    if not authenticated:
        st.warning("Please login first!")
        return
    
    st.title("🆕 Start New Audit")
    
    audit_manager = AuditManager("audit.db")
    
    with st.form("new_audit_form"):
        st.subheader("Basic Information")
        title = st.text_input("Audit Title", placeholder="Enter a descriptive title")
        description = st.text_area("Description", placeholder="Describe the purpose of this audit")
        
        col1, col2 = st.columns(2)
        with col1:
            area = st.selectbox("Area", options=list(AREAS.keys()))
            subarea = st.selectbox("Subarea", options=AREAS[area])
        with col2:
            machine = st.text_input("Machine/Equipment", placeholder="If applicable")
        
        st.subheader("Schedule")
        start_date = st.date_input("Start Date", value=datetime.today(), key="start_date")
        # No end_date input here; it will be set automatically on close
        
        st.subheader("Team")
        auditors = st.multiselect(
            "Select Auditors",
            options=["uig99939", "uih10432", "user3"],  # Replace with actual user list
            default=[username]
        )
        participants = st.multiselect(
            "Select Participants",
            options=["uig99939", "uih10432", "user3"],  # Replace with actual user list
        )
        user_list = auditors + participants
        responsible = st.selectbox("Responsible", options=user_list if user_list else [username])
        
        submitted = st.form_submit_button("Create Audit")
        if submitted:
            audit_data = {
                'title': title,
                'description': description,
                'start_date': start_date.isoformat(),
                'created_by': username,
                'area': area,
                'subarea': subarea,
                'machine': machine,
                'responsible': responsible
            }
            audit_id = audit_manager.create_audit(audit_data)
            st.success(f"Audit created! ID: {audit_id}")
            
                # Send email to responsible
            if send_responsible_email(responsible, title):
                st.info(f"Notification sent to {responsible}.")
            else:
                st.warning(f"Could not send notification to {responsible}.")

if __name__ == "__main__":
    main()
