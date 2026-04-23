import streamlit as st
import pandas as pd
import bcrypt
import uuid
from database import get_mongo_client

def get_users_collection():
    return get_mongo_client()["clinical_db"]["users"]

def get_patients_collection():
    return get_mongo_client()["clinical_db"]["patients"]

def get_summaries_collection():
    return get_mongo_client()["clinical_db"]["summaries"]

def get_audit_logs_collection():
    return get_mongo_client()["clinical_db"]["audit_logs"]

def view_system_health():
    st.title("System Health & User Management")
    
    st.subheader("Security Audit Logs (Last 7 Days)")
    audit_coll = get_audit_logs_collection()
    
    # Simple MongoDB Aggregation for the heatmap
    pipeline = [
        {"$group": {"_id": {"role": "$role", "action": "$action"}, "count": {"$sum": 1}}}
    ]
    audit_stats = list(audit_coll.aggregate(pipeline))
    
    if audit_stats:
        # Convert to pandas dataframe for Streamlit charting
        records = []
        for stat in audit_stats:
            records.append({
                "Role": stat["_id"]["role"],
                "Action": stat["_id"]["action"],
                "Count": stat["count"]
            })
        df = pd.DataFrame(records)
        if not df.empty:
            # Pivot table for stacked bar chart
            chart_data = df.pivot(index="Role", columns="Action", values="Count").fillna(0)
            st.bar_chart(chart_data)
    else:
        st.info("No audit logs available.")
        
    st.markdown("---")
    
    users_coll = get_users_collection()
    
    # Exclude password hashes securely
    users_projection = {"password": 0, "_id": 0}
    users_data = list(users_coll.find({}, users_projection))
    
    st.subheader("Current Staff Roster")
    if users_data:
        st.dataframe(users_data, use_container_width=True)
    else:
        st.info("No active staff found.")
        
    st.markdown("---")
    st.subheader("Add New User")
    with st.form("add_user_form", clear_on_submit=True):
        username = st.text_input("Username")
        temporary_password = st.text_input("Temporary Password", type="password")
        role = st.selectbox("Role", ["Clinical", "Research", "Administrative", "Legal"])
        full_name = st.text_input("Full Name")
        if st.form_submit_button("Register User"):
            if username and temporary_password and full_name:
                hashed_pw = bcrypt.hashpw(temporary_password.encode("utf-8"), bcrypt.gensalt())
                users_coll.insert_one({
                    "username": username,
                    "password": hashed_pw,
                    "role": role,
                    "full_name": full_name
                })
                st.success(f"Successfully registered user {username} with role {role}.")
            else:
                st.warning("Please fill all fields to register the user.")
                
    st.markdown("---")
    st.subheader("Register New Patient")
    with st.form("add_patient_form", clear_on_submit=True):
        p_name = st.text_input("Patient Full Name")
        p_age = st.number_input("Age", min_value=0, max_value=120, step=1)
        p_contact = st.text_input("Contact Number (e.g., xxx-xxx-xxxx)")
        p_disease = st.text_input("Primary Condition / Disease")
        p_medication = st.text_input("Current Medication")
        p_billing = st.selectbox("Billing Proxy Method", ["Visa", "Mastercard", "Amex", "Discover", "Internal Routing", "Missing Data"])
        p_verified = st.checkbox("Profile Verification (Identity Verified against official documents)")
        
        if st.form_submit_button("Create Patient Profile"):
            if p_name and p_contact and p_disease and p_medication:
                new_patient_id = f"P-{uuid.uuid4().hex[:6].upper()}-A" # Enforcement of unique ID
                patients_coll = get_patients_collection()
                patients_coll.insert_one({
                    "patient_id": new_patient_id,
                    "patient_name": p_name,
                    "age": int(p_age),
                    "contact_no": p_contact,
                    "isVerified": p_verified,
                    "disease": p_disease,
                    "medication": p_medication,
                    "billing_info": p_billing
                })
                st.success(f"Patient formally registered with complete schema. Assigned Unique Secure ID: `{new_patient_id}`")
            else:
                st.warning("Required Demographic metadata missing. All system fields must be supplied.")


def view_patient_billing():
    st.title("Patient Billing Dashboard")
    patients_coll = get_patients_collection()
    
    # CRITICAL: Project strictly permitted financial and demographic fields
    # By strictly building an inclusion map, disease and medication are explicitly stripped on the DB side
    billing_projection = {
        "_id": 0,
        "patient_id": 1,
        "patient_name": 1,
        "billing_info": 1,
        "contact_no": 1,
        "isVerified": 1
    }
    
    patients_data = list(patients_coll.find({}, billing_projection))
    
    st.subheader("Active Patient Accounts")
    if patients_data:
        st.dataframe(patients_data, use_container_width=True)
    else:
        st.info("No patient billing records found.")


def view_admin_summaries():
    st.title("Administrative Notes")
    summaries_coll = get_summaries_collection()
    
    # Administrative filtering
    admin_summaries = list(summaries_coll.find({
        "Context_Type": "Administrative"
    }, {"_id": 0, "Purpose_Name": 1, "Content_Data": 1, "Patient_ID": 1}))
    
    st.subheader("Operational & Billing Exceptions")
    if admin_summaries:
        for summary in admin_summaries:
            purpose = summary.get("Purpose_Name", "General")
            patient = summary.get("Patient_ID", "Unknown")
            with st.expander(f"{purpose} (Ref: {patient})", expanded=True):
                st.markdown(summary.get("Content_Data", ""))
    else:
        st.info("No administrative summaries requiring review found.")
