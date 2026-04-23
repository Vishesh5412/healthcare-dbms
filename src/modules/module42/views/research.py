import hashlib
import random
import pandas as pd
import streamlit as st
from database import get_mongo_client

# ---------------------------------------------------------------------------
# Anonymization Helper Functions
# ---------------------------------------------------------------------------
def pseudonymize(patient_id: str) -> str:
    """Uses hashlib to return a SHA-256 hash of the ID."""
    return hashlib.sha256(patient_id.encode('utf-8')).hexdigest()

def aggregate_age(age) -> str:
    """Takes an integer and returns a string bucket (e.g., '20-29')."""
    try:
        val = int(age)
        lower_bound = (val // 10) * 10
        return f"{lower_bound}-{lower_bound + 9}"
    except (ValueError, TypeError):
        return "Unknown"

def perturb_billing(billing_str: str) -> str:
    """Takes a billing string, converts to float, adds random +/- 5% noise, returns as string."""
    try:
        clean_str = str(billing_str).replace(",", "").replace("$", "").strip()
        val = float(clean_str)
        noise_factor = random.uniform(0.95, 1.05)
        perturbed = val * noise_factor
        return f"{perturbed:,.2f}"
    except (ValueError, TypeError):
        return str(billing_str)

# ---------------------------------------------------------------------------
# Database Getters
# ---------------------------------------------------------------------------
def get_patients_collection():
    return get_mongo_client()["clinical_db"]["patients"]

def get_summaries_collection():
    return get_mongo_client()["clinical_db"]["summaries"]

# ---------------------------------------------------------------------------
# View Logic
# ---------------------------------------------------------------------------
def view_query_anonymized_data():
    st.title("Secure Research Data View")

    patients_coll = get_patients_collection()
    summaries_coll = get_summaries_collection()

    # Strict Database Projection (CRITICAL)
    # Explicitly including safe keys automatically excludes raw PII variables physically from the server response
    safe_projection = {
        "_id": 0,
        "patient_id": 1,
        "age": 1,
        "disease": 1,
        "billing_info": 1
    }
    
    raw_patients = list(patients_coll.find({}, safe_projection))
    
    data_rows = []
    
    # Data Transformation Pipeline
    if raw_patients:
        for patient in raw_patients:
            # Apply anonymization techniques immediately
            safe_row = {
                "Hashed ID": pseudonymize(patient.get("patient_id", "")),
                "Age Bucket": aggregate_age(patient.get("age")),
                "Perturbed Billing": perturb_billing(patient.get("billing_info")),
                "Disease": patient.get("disease", "Unknown")
            }
            data_rows.append(safe_row)
            
    if data_rows:
        # Pushing straight to Pandas DataFrame
        df = pd.DataFrame(data_rows)
        
        st.subheader("Anonymized Dataset")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Disease Demographics")
        disease_counts = df["Disease"].value_counts()
        st.bar_chart(disease_counts)
        
        st.subheader("Epidemiological Age Stratification")
        age_counts = df["Age Bucket"].value_counts().sort_index()
        st.bar_chart(age_counts)
        
        st.subheader("Socioeconomic Resource Distribution (Billing Proxy)")
        billing_counts = df["Perturbed Billing"].value_counts()
        st.bar_chart(billing_counts)
    else:
        st.info("No patient datasets found or database connection blocked.")

    st.markdown("---")
    st.subheader("Research Phase Summaries")
    
    # Research Summaries Filter
    research_summaries = list(summaries_coll.find({
        "Context_Type": "Research"
    }, {"_id": 0, "Patient_ID": 1, "Purpose_Name": 1, "Content_Data": 1}))
    
    if research_summaries:
        for summary in research_summaries:
            purpose = summary.get("Purpose_Name", "Research Context")
            content = summary.get("Content_Data", "")
            with st.expander(f"Study: {purpose}"):
                st.markdown(content)
    else:
        st.info("No targeted explicit Research Summaries generated yet.")

def view_aggregated_summaries():
    st.title("Aggregated Summaries")
    
    patients_coll = get_patients_collection()
    
    raw_patients = list(patients_coll.find({}, {"_id": 0, "age": 1, "disease": 1, "isVerified": 1}))
    
    if raw_patients:
        df = pd.DataFrame(raw_patients)
        
        total_cohort = len(df)
        avg_age = df["age"].mean() if "age" in df else 0
        verified_count = df["isVerified"].sum() if "isVerified" in df else 0
        verified_pct = (verified_count / total_cohort * 100) if total_cohort > 0 else 0
        
        st.markdown("### Population Health Patterns")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Cohort Size", f"{total_cohort}")
        col2.metric("Mean Cohort Age", f"{avg_age:.1f} yrs")
        col3.metric("Verified Profiles", f"{verified_pct:.1f}%")
        
        st.markdown("#### High-Level Data Trends (Conditions)")
        if "disease" in df:
            disease_stats = df["disease"].value_counts().reset_index()
            disease_stats.columns = ["Primary Diagnoses", "Total Aggregated Cases"]
            st.dataframe(disease_stats, hide_index=True, use_container_width=True)
            
        st.info("Additional cohort-wide risk metrics will be plotted and analyzed dynamically as statistical power thresholds are achieved within the demographic base.")
    else:
        st.warning("No adequate cohort data available for statistical aggregation.")
