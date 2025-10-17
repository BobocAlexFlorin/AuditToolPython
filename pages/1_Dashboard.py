import streamlit as st
import pandas as pd
from utils.auth import get_user_auth
from utils.audit_manager import AuditManager
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard", layout="wide")

def main():
    authenticated, user_role, username = get_user_auth()
    
    if not authenticated:
        st.warning("Please login first!")
        return
    
    st.title("📊 Audit Dashboard")
    
    # Initialize audit manager
    audit_manager = AuditManager("audit.db")
    audits = audit_manager.get_all_audits()
    
    if not audits:
        st.info("No audits found.")
        return
    
    df = pd.DataFrame(audits)
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Audits", len(df))
    col2.metric("Open Audits", (df['status']=='Open').sum() if 'status' in df else 0)
    col3.metric("Closed Audits", (df['status']=='Closed').sum() if 'status' in df else 0)
    col4.metric("Your Audits", (df['created_by']==username).sum() if 'created_by' in df else 0)
    
    # Bar chart by area
    if 'area' in df:
        st.subheader("Audits by Area")
        st.bar_chart(df['area'].value_counts())
    
    # Pie chart by status
    if 'status' in df:
        st.subheader("Audit Status Distribution")
        status_counts = df['status'].value_counts()
        fig, ax = plt.subplots(figsize=(3,3))
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4))
        ax.axis('equal')
        st.pyplot(fig)
    
    # Recent audits
    st.subheader("Recent Audits")
    if 'start_date' in df:
        recent = df.sort_values('start_date', ascending=False).head(5)
        st.table(recent[['title','area','start_date','status']] if 'status' in recent else recent[['title','area','start_date']])
    
    # Cool stuff: audits per month
    if 'start_date' in df:
        st.subheader("Audits per Month")
        df['month'] = pd.to_datetime(df['start_date']).dt.to_period('M')
        st.line_chart(df['month'].value_counts().sort_index())

if __name__ == "__main__":
    main()