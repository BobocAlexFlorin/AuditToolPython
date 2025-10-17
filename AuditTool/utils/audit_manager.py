import streamlit as st
import sqlite3
from datetime import datetime
from typing import List, Dict

class AuditManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_tables()
        
        
    def get_all_audits(self):
        """Return a list of all audits as dicts."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, area, status, created_by FROM audits")
        rows = cursor.fetchall()
        audits = []
        for row in rows:
            audits.append({
                "id": row[0],
                "title": row[1],
                "area": row[2],
                "status": row[3],
                "created_by": row[4]
            })
        conn.close()
        return audits
    
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_id TEXT,
                    cause TEXT,
                    corrective_action TEXT,
                    proof_path TEXT,
                    efficiency_evaluation TEXT,
                    FOREIGN KEY (audit_id) REFERENCES audits(id)
                )
            ''')
    
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
                audit_data['end_date'],
                'Open',
                audit_data['created_by'],
                audit_data['area'],
                audit_data['subarea'],
                audit_data['machine']
            ))
            
            # Add participants
            for username, role in audit_data['participants']:
                conn.execute('''
                    INSERT INTO audit_participants VALUES (?, ?, ?)
                ''', (audit_id, username, role))
        
        return audit_id
    
    def get_findings_for_audit(self, audit_id: str) -> list:
        """Return all findings for a given audit."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, cause, corrective_action, proof_path, efficiency_evaluation
                FROM findings
                WHERE audit_id = ?
            ''', (audit_id,))
            findings = []
            for row in cursor.fetchall():
                findings.append({
                    'id': row[0],
                    'cause': row[1],
                    'corrective_action': row[2],
                    'proof_path': row[3],
                    'efficiency_evaluation': row[4]
                })
        return findings
    
    def close_audit(self, audit_id: str) -> bool:
        """Close an audit. Returns True if successful."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE audits SET status = ? WHERE id = ?
                ''', ('Closed', audit_id))
            return True
        except Exception as e:
            st.error(f"Error closing audit: {str(e)}")
            return False
    
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
