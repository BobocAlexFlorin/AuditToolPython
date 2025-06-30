import streamlit as st
import pandas as pd
import os
import ctypes
from datetime import datetime

# --- Role-based authentication using Windows login ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

current_user = os.getlogin()
admin = is_admin()
role = "super-user" if admin else "user"

st.set_page_config(page_title="WeMake Audit App Demo", layout="wide")
st.title("WeMake Style Audit App Demo")
st.write(f"**Logged in as:** {current_user} ({role})")

# --- Session state for audit data ---
if "audit_data" not in st.session_state:
    st.session_state.audit_data = pd.DataFrame(columns=[
        "ID", "Finding", "Cause", "Action", "Responsible", "Start Date", "End Date", "Status", "Efficiency Evaluation", "Proof of Solution", "Area"
    ])

# --- Add new finding form ---
st.subheader("Add New Audit Finding")
with st.form("add_finding_form"):
    today_str = datetime.now().strftime("%Y%m%d")
    default_id = f"TICU_{today_str}"
    finding = st.text_input("Finding")
    cause = st.text_input("Cause")
    action = st.text_input("Action")
    responsible = st.text_input("Responsible")
    start_date = st.date_input("Start Date", value=datetime.now())
    end_date = st.date_input("End Date", value=datetime.now())
    status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
    efficiency = st.text_area("Efficiency Evaluation") if admin else ""
    proof = st.text_area("Proof of Solution")
    area = st.text_input("Area")
    custom_id = st.text_input("ID (editable by super-user)", value=default_id) if admin else default_id
    submitted = st.form_submit_button("Add Finding")
    if submitted:
        new_row = {
            "ID": custom_id,
            "Finding": finding,
            "Cause": cause,
            "Action": action,
            "Responsible": responsible,
            "Start Date": start_date,
            "End Date": end_date,
            "Status": status,
            "Efficiency Evaluation": efficiency,
            "Proof of Solution": proof,
            "Area": area
        }
        st.session_state.audit_data = pd.concat([
            st.session_state.audit_data, pd.DataFrame([new_row])
        ], ignore_index=True)
        st.success("Finding added!")

# --- Display and edit audit table ---
st.subheader("Audit Findings Table")
if st.session_state.audit_data.empty:
    st.info("No findings yet.")
else:
    edited_df = st.session_state.audit_data.copy()
    for idx, row in edited_df.iterrows():
        with st.expander(f"Edit Finding {row['ID']}"):
            if admin:
                edited_df.at[idx, "ID"] = st.text_input(f"ID_{idx}", value=row["ID"])
                edited_df.at[idx, "Efficiency Evaluation"] = st.text_area(f"Efficiency_{idx}", value=row["Efficiency Evaluation"])
            edited_df.at[idx, "Responsible"] = st.text_input(f"Responsible_{idx}", value=row["Responsible"])
            edited_df.at[idx, "Status"] = st.selectbox(f"Status_{idx}", ["Open", "In Progress", "Closed"], index=["Open", "In Progress", "Closed"].index(row["Status"]))
            edited_df.at[idx, "Proof of Solution"] = st.text_area(f"Proof_{idx}", value=row["Proof of Solution"])
            if st.button(f"Save_{idx}"):
                st.session_state.audit_data.iloc[idx] = edited_df.iloc[idx]
                st.success(f"Finding {row['ID']} updated!")
    st.dataframe(st.session_state.audit_data, use_container_width=True)

st.caption("Demo app. For production, add persistent storage and advanced authentication.")
