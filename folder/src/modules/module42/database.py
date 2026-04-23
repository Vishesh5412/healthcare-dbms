import os
from pymongo import MongoClient
import streamlit as st
from dotenv import load_dotenv

# Priority: Streamlit secrets (cloud) → env var (.env file)
def _get_uri():
    try:
        return st.secrets["MONGO_URI"]
    except Exception:
        pass
    
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI is not set. Please add it to your .env file or Streamlit secrets.")
    return uri

MONGO_URI = _get_uri()

@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGO_URI)

def get_users_collection():
    return get_mongo_client()["clinical_db"]["users"]

def get_audit_logs_collection():
    return get_mongo_client()["clinical_db"]["audit_logs"]

def log_audit_event(username, role, action, patient_id=None):
    from datetime import datetime, timezone
    coll = get_audit_logs_collection()
    coll.insert_one({
        "timestamp": datetime.now(timezone.utc),
        "username": username,
        "role": role,
        "action": action,
        "patient_id": patient_id
    })
