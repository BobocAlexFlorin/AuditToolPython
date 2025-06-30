import streamlit as st
import pandas as pd
import os
import ctypes
from datetime import datetime
import sqlite3
import shutil
import base64

DB_PATH = "audit_findings.db"
PROOF_UPLOAD_DIR = "proof_uploads"
os.makedirs(PROOF_UPLOAD_DIR, exist_ok=True)

# Helper to check if user is admin (Windows)
def is_user_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

# Get current Windows username
def get_windows_username():
    return os.getlogin()

# Generate ID in format TICU_[date]
def generate_id():
    return f"TICU_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Initialize session state for findings
def init_findings():
    if 'findings' not in st.session_state:
        st.session_state['findings'] = pd.DataFrame(columns=[
            'ID', 'Finding', 'Cause', 'Action', 'Responsible', 'Start Date', 'End Date', 'Status',
            'Efficiency Evaluation', 'Proof of Solution', 'Area'
        ])

def create_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                ID TEXT PRIMARY KEY,
                Finding TEXT,
                Cause TEXT,
                Action TEXT,
                Responsible TEXT,
                Start_Date TEXT,
                End_Date TEXT,
                Status TEXT,
                Efficiency_Evaluation TEXT,
                Proof_of_Solution TEXT,
                Area TEXT,
                SUBAREA TEXT,
                MACHINE TEXT
            )
        ''')

def load_findings():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM findings", conn)
    # Rename columns to match app's expected names
    df = df.rename(columns={
        'Start_Date': 'Start Date',
        'End_Date': 'End Date',
        'Efficiency_Evaluation': 'Efficiency Evaluation',
        'Proof_of_Solution': 'Proof of Solution'
    })
    return df

def save_finding(row):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT OR REPLACE INTO findings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['ID'], row['Finding'], row['Cause'], row['Action'], row['Responsible'],
            str(row['Start Date']), str(row['End Date']), row['Status'],
            row['Efficiency Evaluation'], row['Proof of Solution'], row['Area']
        ))

def update_finding(row):
    save_finding(row)

# Main app
def main():
    st.set_page_config(page_title="Curing Audit", layout="wide")
    st.title("Audit Curing")

    # --- Auth/Role Switcher ---
    st.sidebar.markdown("## Authentication")
    role = st.sidebar.selectbox("Select Role", ["Normal User", "Super User (Admin)"])
    is_admin = (role == "Super User (Admin)")

    username = get_windows_username()
    st.sidebar.info(f"Logged in as: {username} ({'Admin' if is_admin else 'User'})")

    init_findings()
    create_table()
    try:
        st.session_state['findings'] = load_findings()
    except Exception:
        st.session_state['findings'] = pd.DataFrame(columns=[
            'ID', 'Finding', 'Cause', 'Action', 'Responsible', 'Start Date', 'End Date', 'Status',
            'Efficiency Evaluation', 'Proof of Solution', 'Area'
        ])
    findings = st.session_state['findings']

    # --- Modern Dashboard Section ---
    st.header("📊 Dashboard")
    total_findings = len(findings)
    open_count = (findings['Status'] == 'Open').sum()
    in_progress_count = (findings['Status'] == 'In Progress').sum()
    closed_count = (findings['Status'] == 'Closed').sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Findings", total_findings)
    col2.metric("Open", open_count)
    col3.metric("In Progress", in_progress_count)
    col4.metric("Closed", closed_count)

    # Bar chart for findings by status
    st.subheader("Findings by Status")
    status_counts = findings['Status'].value_counts()
    st.bar_chart(status_counts)

    # Bar chart for findings by responsible user
    st.subheader("Findings by Responsible User")
    if not findings.empty:
        responsible_counts = findings['Responsible'].value_counts()
        st.bar_chart(responsible_counts)

    # Pie chart for findings by area (using matplotlib)
    st.subheader("Findings by Area")
    if not findings.empty and 'Area' in findings.columns:
        import matplotlib.pyplot as plt
        area_counts = findings['Area'].value_counts()
        fig, ax = plt.subplots(figsize=(3, 3))  # Smaller size
        wedges, texts, autotexts = ax.pie(
            area_counts,
            labels=area_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='w'),  # Donut style
            textprops={'fontsize': 10, 'color': 'white', 'weight': 'bold'}  # White, bold labels
        )
        ax.axis('equal')
        plt.setp(autotexts, size=9, weight="bold", color="white")
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig.gca().add_artist(centre_circle)
        fig.patch.set_alpha(0)
        st.pyplot(fig)

    # Responsible user stats
    user_findings = findings[findings['Responsible'] == username]
    user_open = (user_findings['Status'] == 'Open').sum()
    user_in_progress = (user_findings['Status'] == 'In Progress').sum()
    user_closed = (user_findings['Status'] == 'Closed').sum()
    st.subheader(f"Your Findings ({username})")
    st.write(f"Open: {user_open} | In Progress: {user_in_progress} | Closed: {user_closed}")

    # Admin: show per-user stats
    if is_admin:
        st.subheader("All Users - Findings by Status")
        if not findings.empty:
            user_stats = findings.groupby('Responsible')['Status'].value_counts().unstack(fill_value=0)
            user_stats = user_stats[['Open', 'In Progress', 'Closed']] if set(['Open','In Progress','Closed']).issubset(user_stats.columns) else user_stats
            st.dataframe(user_stats, use_container_width=True)
        else:
            st.info("No findings to show user stats.")
    st.divider()

    st.header("Add New Finding")
    with st.form("add_finding_form"):
        finding = st.text_input("Finding")
        cause = st.text_input("Cause")
        action = st.text_input("Action")
        responsible = st.text_input("Responsible", value=username)
        start_date = st.date_input("Start Date", value=datetime.today())
        end_date = st.date_input("End Date")
        status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
        efficiency = st.text_area("Efficiency Evaluation")
        proof = st.text_area("Proof of Solution")
        area = st.text_input("Area")
        submitted = st.form_submit_button("Add Finding")
        if submitted:
            new_id = generate_id()
            new_row = {
                'ID': new_id,
                'Finding': finding,
                'Cause': cause,
                'Action': action,
                'Responsible': responsible,
                'Start Date': start_date,
                'End Date': end_date,
                'Status': status,
                'Efficiency Evaluation': efficiency,
                'Proof of Solution': proof,
                'Area': area
            }
            st.session_state['findings'] = pd.concat([findings, pd.DataFrame([new_row])], ignore_index=True)
            save_finding(new_row)
            st.success(f"Finding added with ID: {new_id}")

    # --- Sidebar: Finding Shortcuts ---
    st.sidebar.markdown("## Jump to Finding")
    if not findings.empty:
        finding_ids = findings['ID'].tolist()
        selected_finding = st.sidebar.selectbox("Go to Finding", finding_ids, key="sidebar_finding_select")
        if selected_finding:
            st.session_state['jump_to_finding'] = selected_finding
    else:
        st.sidebar.info("No findings to jump to yet.")

    st.header("Audit Findings Table")
    findings = st.session_state['findings']
    jump_to = st.session_state.get('jump_to_finding', None)
    if not findings.empty:
        for idx, row in findings.iterrows():
            expanded = (jump_to == row['ID'])
            with st.expander(f"Finding {row['ID']}", expanded=expanded):
                if is_admin:
                    id_val = st.text_input(f"ID_{idx}", value=row['ID'], key=f"id_{idx}")
                else:
                    id_val = row['ID']
                finding_val = st.text_input(f"Finding_{idx}", value=row['Finding'], key=f"finding_{idx}", disabled=not is_admin)
                cause_val = st.text_input(f"Cause_{idx}", value=row['Cause'], key=f"cause_{idx}", disabled=not is_admin)
                action_val = st.text_input(f"Action_{idx}", value=row['Action'], key=f"action_{idx}", disabled=not is_admin)
                responsible_val = st.text_input(f"Responsible_{idx}", value=row['Responsible'], key=f"responsible_{idx}", disabled=not (is_admin or username==row['Responsible']))
                start_date_val = st.date_input(f"Start Date_{idx}", value=pd.to_datetime(row['Start Date']), key=f"start_{idx}", disabled=not is_admin)
                end_date_val = st.date_input(f"End Date_{idx}", value=pd.to_datetime(row['End Date']), key=f"end_{idx}", disabled=not is_admin)
                # Status always editable
                status_val = st.selectbox(f"Status_{idx}", ["Open", "In Progress", "Closed"], index=["Open", "In Progress", "Closed"].index(row['Status']), key=f"status_{idx}")
                # File uploader for proof
                uploaded_files = st.file_uploader(f"Upload Proof_{idx}", accept_multiple_files=True, key=f"proof_upload_{idx}")
                proof_files = row['Proof of Solution'] if isinstance(row['Proof of Solution'], str) else ""
                proof_list = proof_files.split(';') if proof_files else []
                if uploaded_files:
                    for file in uploaded_files:
                        file_path = os.path.join(PROOF_UPLOAD_DIR, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        if file.name not in proof_list:
                            proof_list.append(file.name)
                proof_val = ";".join(proof_list)
                # Proof preview and download
                if proof_list:
                    st.markdown("**Attached Proof Files:**")
                    for fname in proof_list:
                        file_path = os.path.join(PROOF_UPLOAD_DIR, fname)
                        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            with st.expander(f"View Image: {fname}"):
                                st.image(file_path, caption=fname, use_column_width=True)
                        elif fname.lower().endswith('.pdf'):
                            with st.expander(f"View PDF: {fname}"):
                                with open(file_path, "rb") as f:
                                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                        else:
                            st.markdown(f"- [Download {fname}]({PROOF_UPLOAD_DIR}/{fname})")
                efficiency_val = st.text_area(f"Efficiency_{idx}", value=row['Efficiency Evaluation'], key=f"eff_{idx}", disabled=not is_admin)
                area_val = st.text_input(f"Area_{idx}", value=row['Area'], key=f"area_{idx}", disabled=not is_admin)
                if st.button(f"Save_{idx}", key=f"save_{idx}"):
                    st.session_state['findings'].loc[idx] = [
                        id_val, finding_val, cause_val, action_val, responsible_val, start_date_val, end_date_val,
                        status_val, efficiency_val, proof_val, area_val
                    ]
                    update_row = {
                        'ID': id_val,
                        'Finding': finding_val,
                        'Cause': cause_val,
                        'Action': action_val,
                        'Responsible': responsible_val,
                        'Start Date': start_date_val,
                        'End Date': end_date_val,
                        'Status': status_val,
                        'Efficiency Evaluation': efficiency_val,
                        'Proof of Solution': proof_val,
                        'Area': area_val
                    }
                    update_finding(update_row)
                    st.success(f"Finding {id_val} updated.")
    else:
        st.info("No findings yet. Add a new finding above.")

if __name__ == "__main__":
    main()
