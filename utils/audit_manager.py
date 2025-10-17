import streamlit as st
import sqlite3
from datetime import datetime
from typing import List, Dict

class AuditManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_tables()
    
    def setup_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            # Audits table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audits (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    status TEXT,
                    created_by TEXT,
                    area TEXT,
                    subarea TEXT,
                    machine TEXT
                )
            ''')
            
            # Audit participants
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_participants (
                    audit_id TEXT,
                    username TEXT,
                    role TEXT,
                    FOREIGN KEY (audit_id) REFERENCES audits(id),
                    PRIMARY KEY (audit_id, username, role)
                )
            ''')
            
            conn.execute('''
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        audit_id TEXT,
        cause TEXT,
        corrective_action TEXT,
        proof_path TEXT,
        efficiency_evaluation TEXT,
        FOREIGN KEY (audit_id) REFERENCES audits(id)
    )
''')
            
    def set_efficiency_evaluation(self, finding_id: str, evaluation: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE findings SET efficiency_evaluation = ? WHERE id = ?
            ''', (evaluation, finding_id))
    
    def create_audit(self, audit_data: Dict) -> str:
        """Create a new audit and return its ID."""
        audit_id = f"AUDIT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO audits VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_id,
                audit_data['title'],
                audit_data['description'],
                audit_data['start_date'],
                None,  # end_date is None at creation
                'Open',
                audit_data['created_by'],
                audit_data['area'],
                audit_data['subarea'],
                audit_data['machine']
            ))
            # Add responsible
            conn.execute('''
                INSERT INTO audit_participants VALUES (?, ?, ?)
            ''', (audit_id, audit_data['responsible'], 'responsible'))
            # Add other participants if needed...
        return audit_id
    
    def get_all_audits(self):
        """Return all audits as a list of dicts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audits")
            columns = [desc[0] for desc in cursor.description]
            audits = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return audits
    
    def get_findings_for_audit(self, audit_id: str):
        """Return all findings for a given audit as a list of dicts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, cause, corrective_action, proof_path, efficiency_evaluation FROM findings WHERE audit_id = ?",
                (audit_id,)
            )
            columns = [desc[0] for desc in cursor.description]
            findings = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return findings
    
    def add_efficiency_evaluation_column(db_path="audit.db"):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(findings)")
            columns = [info[1] for info in cursor.fetchall()]
            if "efficiency_evaluation" not in columns:
                cursor.execute("ALTER TABLE findings ADD COLUMN efficiency_evaluation TEXT")
                print("Added efficiency_evaluation column to findings table.")

    add_efficiency_evaluation_column()
    
    def close_audit(self, audit_id: str) -> bool:
        """Close an audit and set end_date to today."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE audits SET status = ?, end_date = ? WHERE id = ?
                ''', ('Closed', datetime.now().strftime('%Y-%m-%d'), audit_id))
            return True
        except Exception as e:
            st.error(f"Error closing audit: {str(e)}")
            return False
        
        
    def add_finding(self, audit_id: str, cause: str, corrective_action: str, proof_path: str):
        finding_id = f"FIND_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO findings (id, audit_id, cause, corrective_action, proof_path, efficiency_evaluation)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (finding_id, audit_id, cause, corrective_action, proof_path, None))  # None for efficiency_evaluation
        return finding_id
    
    def get_all_audits(self):
        """Return all audits as a list of dicts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audits")
            columns = [desc[0] for desc in cursor.description]
            audits = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return audits
    
    def get_audit_details(self, audit_id: str) -> Dict:
        """Get all details about an audit."""
        with sqlite3.connect(self.db_path) as conn:
            # Get audit info
            audit = conn.execute('''
                SELECT * FROM audits WHERE id = ?
            ''', (audit_id,)).fetchone()
            
            # Get participants
            participants = conn.execute('''
                SELECT username, role FROM audit_participants WHERE audit_id = ?
            ''', (audit_id,)).fetchall()
            
            if audit:
                return {
                    'id': audit[0],
                    'title': audit[1],
                    'description': audit[2],
                    'start_date': audit[3],
                    'end_date': audit[4],
                    'status': audit[5],
                    'created_by': audit[6],
                    'area': audit[7],
                    'subarea': audit[8],
                    'machine': audit[9],
                    'participants': participants
                }
        return None
