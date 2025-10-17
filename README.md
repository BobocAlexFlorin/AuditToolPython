# AuditTool — Streamlit Audit Management

AuditTool is a lightweight, internal audit management web app built with Streamlit and SQLite.  
It supports role-based workflows (audit creator, responsible owner, auditors), file-based proof uploads, findings tracking, and a simple emailing notification for responsible assignments. The app is designed for fast adoption in operational teams that need a simple, auditable process for inspections, nonconformances, corrective actions, and post-action efficiency evaluation.

## Elevator pitch
AuditTool streamlines audits from creation to closure: creators open an audit and assign responsibility; responsible users complete the audit, add findings and proof (documents, images, videos); creators evaluate the corrective efficiency; once evaluated the record is locked and exportable. Fast to deploy, minimal dependencies, and easy to extend.

## Key features
- Audit lifecycle: create → assign responsible → close → add findings → creator grades efficiency → lock & export.
- Role-driven UI:
  - Creator: create audits (ID, title, description, start date, area, subarea, machine), grade findings’ efficiency.
  - Responsible: close audit (auto end-date), add findings (cause, corrective action, proof uploads) after closing.
  - Auditors/participants: view assigned audits and attachments.
- File proof support: .docx, .xlsx, images, video (stored to disk, paths in DB).
- Basic email notification to responsible upon assignment (configurable / test-friendly).
- SQLite persistence with migration helper (adds columns for schema changes).
- Simple export/download of finished audit reports.

## Typical user flow
1. Creator logs in, creates audit (assigns responsible).
2. Responsible receives notification, performs audit, then closes it (end date recorded automatically).
3. After closing, responsible uploads findings with cause, corrective actions and proof files.
4. Creator reviews findings and submits an efficiency evaluation for each finding.
5. Once all findings are evaluated, the audit and findings become read-only and a downloadable report is available.

## Technology stack
- Frontend: Streamlit (Python)
- Database: SQLite (single-file DB for portability)
- Email: Python smtplib (simple, configurable)
- Deploy/test: Local, internal server, or a container

## Data model (summary)
- audits: id, title, description, start_date, end_date, status, created_by, area, subarea, machine
- audit_participants: audit_id, username, role (e.g., responsible)
- findings: id, audit_id, cause, corrective_action, proof_path, efficiency_evaluation

## Security & access
- App uses Windows username detection (os.getlogin) by default for internal use; demo user-switcher provided for testing.
- Email map is configurable; production should use secure SMTP (TLS) and real user directory (AD/Azure).
- For production, integrate with SSO/AD or reverse proxy authentication for stronger security.

## How to run (Windows)
1. Open a terminal in the project folder:
   cd c:\Users\uig99939\source\repos\AuditToolPython
2. Create / activate virtualenv (if needed):
   - PowerShell:
     ```
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - cmd.exe:
     ```
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   or at minimum:
   ```
   pip install streamlit pandas
   ```
4. Run the app (choose page or main script):
   ```
   streamlit run pages/3_View_Audits.py
   ```
   or
   ```
   streamlit run audit_app_working2.py
   ```
5. Stop server: Ctrl+C

## Developer notes
- Database migrations: a helper runs a one-time check and ALTER TABLE to add new columns (e.g., `efficiency_evaluation`) for existing DBs.
- Use unique Streamlit widget keys when widgets are repeated in loops or dynamic UIs.
- Methods in utils/audit_manager.py:
  - create_audit(audit_data), close_audit(audit_id), add_finding(...), get_findings_for_audit(audit_id), get_all_audits(), get_audit_details(audit_id), set_efficiency_evaluation(finding_id, evaluation)
- Email helper lives in `utils/email_utils.py`. Update USER_EMAILS and SMTP settings for production.

## Demo / meeting checklist
- Show audit creation (creator perspective).
- Assign responsible user and show email notification (simulate with localhost SMTP).
- Switch to responsible (user-switcher) → close audit; show end-date auto-set.
- Add findings and upload proof files.
- Switch to creator → perform efficiency evaluation; show locking behavior.
- Export/download final audit report.

## Roadmap / future work
- Integrate AD/Azure SSO (OAuth/OIDC) for secure enterprise login.
- Store files in blob storage (S3/MinIO/SharePoint) and add access control.
- Role & permission management UI and audit history/versions.
- Automated reporting & dashboards (KPIs, trends).
- Unit tests and CI pipeline.

## Contribution / contact
- Contributions welcome — open an issue or pull request.
- For internal demos, contact the project owner (alexandru-florin.boboc@conti.de).
