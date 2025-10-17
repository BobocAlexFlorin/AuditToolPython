import streamlit as st
import pandas as pd
from utils.auth import get_user_auth
from utils.audit_manager import AuditManager

st.set_page_config(page_title="View Audits", layout="wide")

def main():
    authenticated, user_role, username = get_user_auth()
    if not authenticated:
        st.warning("Please login first!")
        return
    st.title("📋 All Audits")
    audit_manager = AuditManager("audit.db")
    audits = audit_manager.get_all_audits()
    if not audits:
        st.info("No audits found.")
        return
    df = pd.DataFrame(audits)
    # Search/filter
    search = st.text_input("Search audits by title/area/participant...")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
    st.dataframe(df, use_container_width=True)
    # Expandable details
    for idx, row in df.iterrows():
        with st.expander(f"Audit: {row['title']} (ID: {row['id']})"):
            st.write(row)
            # Fetch full audit details for permissions and findings
            audit = audit_manager.get_audit_details(row['id'])
            responsible_username = next((u for u, r in audit['participants'] if r == 'responsible'), None)
            if username == responsible_username and audit['status'] == 'Open':
                if st.button(f"Close Audit {row['id']}"):
                    audit_manager.close_audit(audit['id'])
                    st.success("Audit closed. You can now add findings.")
            if username == responsible_username and audit['status'] == 'Closed':
                with st.form(f"add_finding_{row['id']}"):
                    cause = st.text_area("Cause")
                    corrective_action = st.text_area("Corrective Action")
                    proof_file = st.file_uploader("Upload Proof", type=["docx", "xlsx", "png", "jpg", "jpeg", "mp4", "avi"])
                    if st.form_submit_button("Add Finding"):
                        proof_path = None
                        if proof_file:
                            proof_path = f"proof_uploads/{audit['id']}_{proof_file.name}"
                            with open(proof_path, "wb") as f:
                                f.write(proof_file.read())
                        audit_manager.add_finding(audit['id'], cause, corrective_action, proof_path)
                        st.success("Finding added!")
            findings = audit_manager.get_findings_for_audit(audit['id'])  # You may need to implement this method
            for finding in findings:
                st.write(f"Finding: {finding['cause']}")
                st.write(f"Corrective Action: {finding['corrective_action']}")
                st.write(f"Proof: {finding['proof_path']}")
                st.write(f"Efficiency Evaluation: {finding.get('efficiency_evaluation', 'Not graded yet')}")
                
                # Only audit creator can grade, and only if not already graded
                if username == audit['created_by'] and not finding.get('efficiency_evaluation'):
                    with st.form(f"eff_eval_{finding['id']}"):
                        evaluation = st.selectbox("Efficiency Evaluation", ["Efficient", "Partially Efficient", "Not Efficient"])
                        if st.form_submit_button("Submit Evaluation"):
                            audit_manager.set_efficiency_evaluation(finding['id'], evaluation)
                            st.success("Efficiency evaluation saved. This finding is now locked.")

if __name__ == "__main__":
    main()
