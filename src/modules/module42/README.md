# 🏥 Secure Clinical Summary View Generator (Module 42)

A robust, context-aware database application built with Streamlit and MongoDB. This project perfectly demonstrates NoSQL database architectures, Role-Based Access Control (RBAC), and dynamic querying for electronic health records.

## ✨ Key Features Implemented

1. **Role-Based Access Control (RBAC)**
   - Secure JWT token-based authentication and Bcrypt password hashing.
   - Distinct views and access levels for Clinical, Research, Administrative, and Legal roles.

2. **Advanced Data Security & Anonymization**
   - **Pseudonymization:** Real patient IDs are masked using SHA-256 hashing for the Research role.
   - **Aggregation:** Age data is generalized into 10-year buckets (e.g., "50-59").
   - **Perturbation:** Billing amounts are randomized by ±15% to hide exact financial records.

3. **Security Audit Heatmap**
   - A MongoDB aggregation pipeline tracks every time a patient record is queried or downloaded.
   - Visualized in the Admin Dashboard to prove strict access control compliance.

4. **Advanced Patient Filtering**
   - Uses complex NoSQL equivalents of `WHERE` clauses (`$in`, `$gte`, `$lte`) to let Clinical users dynamically search by multiple diseases and age ranges.

5. **1-Click PDF Extraction**
   - Clinical summaries and Legal Subpoenas can be generated and exported natively to PDF.

---

## 🔑 Login Credentials

The system is seeded with 4 distinct roles to test the Context-Aware capabilities:

| Role             | Username               | Password          | What they can do                                      |
|------------------|------------------------|-------------------|-------------------------------------------------------|
| **Clinical**     | `clinical_user`        | `clinical123`     | Views raw patient data, advanced search, PDF export   |
| **Research**     | `research_user`        | `research123`     | Only sees hashed/anonymized data, sees aggregate charts|
| **Administrative**| `administrative_user` | `administrative123`| Manages users, billing proxy, views audit heatmap     |
| **Legal**        | `legal_user`           | `legal123`        | Extracts specific subpoena fields and legal PDFs      |

---

## 🚀 How to Run Locally

### 1. Install Dependencies
Make sure you have Python 3.9+ installed.
```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB
Create a `.env` file in the root directory (or use `.streamlit/secrets.toml`) and paste your MongoDB URI:
```env
MONGO_URI="mongodb+srv://<username>:<password>@cluster0...mongodb.net/"
```

### 3. Seed the Database
Before running the app, populate the database with realistic medical data, users, and mock audit logs:
```bash
python seed_db.py
```

### 4. Start the Application
```bash
streamlit run app.py
```
Open the local URL provided in the terminal (usually `http://localhost:8501`).

---

## 📂 Project Structure
```text
├── app.py                # Main Streamlit application and routing
├── auth.py               # JWT authentication and cookie logic
├── database.py           # MongoDB connection and Audit Logger
├── seed_db.py            # DML script to generate patients, users, and audit data
├── pdf_utils.py          # PDF generation utility (fpdf2)
├── anonymization.py      # Core logic for masking/hashing Research data
├── requirements.txt      # Python dependencies
└── views/                # Role-specific dashboard pages
    ├── administrative.py 
    ├── clinical.py       
    ├── legal.py          
    └── research.py       
```
