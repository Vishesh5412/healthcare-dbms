import streamlit as st
from database import get_mongo_client, log_audit_event
from bson.objectid import ObjectId
import pdf_utils

def get_patients_collection():
    return get_mongo_client()["clinical_db"]["patients"]

def get_summaries_collection():
    return get_mongo_client()["clinical_db"]["summaries"]

def view_patient_context():
    st.title("Patient Context")
    
    patients_coll = get_patients_collection()
    summaries_coll = get_summaries_collection()

    tab1, tab2 = st.tabs(["Lookup by ID", "Advanced Search"])

    with tab1:
        st.markdown("### Real-time Patient Lookup")
        entered_patient_id = st.text_input("Enter Patient ID (e.g., P-12345-X)")

        if entered_patient_id:
            # Audit log
            log_audit_event(st.session_state.user["username"], "Clinical", "Searched Patient", entered_patient_id)
            
            patient_projection = {
                "_id": 0, "patient_name": 1, "age": 1, "disease": 1, "medication": 1, "patient_id": 1
            }
            patient = patients_coll.find_one({"patient_id": entered_patient_id}, patient_projection)
            
            if patient:
                st.subheader("Patient Information")
                st.markdown(f"**Name:** {patient.get('patient_name', 'N/A')}")
                st.markdown(f"**Age:** {patient.get('age', 'N/A')}")
                st.markdown(f"**Disease:** {patient.get('disease', 'N/A')}")
                st.markdown(f"**Medication:** {patient.get('medication', 'N/A')}")
                    
                st.markdown("---")
                st.subheader("Clinical Summaries")
                
                clinical_summaries = list(summaries_coll.find({
                    "Patient_ID": patient.get("patient_id"),
                    "Context_Type": "Clinical"
                }, {"_id": 0, "Content_Data": 1, "Purpose_Name": 1, "Generated_Timestamp": 1}))
                
                if clinical_summaries:
                    for idx, summary in enumerate(clinical_summaries):
                        purpose = summary.get("Purpose_Name", "General")
                        timestamp = summary.get("Generated_Timestamp", "")
                        content = summary.get("Content_Data", "No content available.")
                        
                        title = f"Summary: {purpose} ({timestamp})" if timestamp else f"Summary: {purpose}"
                        with st.expander(title, expanded=True):
                            st.markdown(content)
                            pdf_bytes = pdf_utils.generate_pdf(patient.get("patient_id"), purpose, content)
                            st.download_button(
                                label="📥 Export as PDF",
                                data=pdf_bytes,
                                file_name=f"clinical_summary_{patient.get('patient_id')}_{idx}.pdf",
                                mime="application/pdf"
                            )
                else:
                    st.info("No clinical summaries found for this patient.")
            else:
                st.error(f"Patient record for ID '{entered_patient_id}' not found.")

    with tab2:
        st.markdown("### Advanced Patient Filter")
        st.markdown("Demonstrates complex NoSQL/SQL `WHERE` equivalents (`$in`, `$gte`, `$lte`).")
        
        col1, col2 = st.columns(2)
        with col1:
            all_diseases = patients_coll.distinct("disease")
            selected_diseases = st.multiselect("Filter by Disease", all_diseases)
        with col2:
            min_age, max_age = st.slider("Filter by Age Range", 0, 100, (0, 100))
            
        if st.button("Run Complex Query"):
            query = {"age": {"$gte": min_age, "$lte": max_age}}
            if selected_diseases:
                query["disease"] = {"$in": selected_diseases}
                
            results = list(patients_coll.find(query, {"_id": 0, "patient_name": 1, "patient_id": 1, "age": 1, "disease": 1, "medication": 1}))
            
            # Audit log general search
            log_audit_event(st.session_state.user["username"], "Clinical", "Advanced Search", "Multiple")
            
            if results:
                st.success(f"Found {len(results)} matching patients.")
                st.dataframe(results, use_container_width=True)
            else:
                st.warning("No patients match these criteria.")

def view_generate_summary():
    st.title("Generate Summary")
    
    st.markdown("### Generate Referral")
    entered_patient_id = st.text_input("Enter Patient ID for Referral (e.g., P-12345-X)")
    
    # Referral Action
    if st.button("Generate Referral-Specific Summary"):
        if entered_patient_id:
            patients_coll = get_patients_collection()
            patient = patients_coll.find_one({"patient_id": entered_patient_id}, {"_id": 0, "patient_name": 1, "disease": 1, "medication": 1})
            
            if patient:
                patient_name = patient.get("patient_name", "The patient")
                disease = patient.get("disease", "an unspecified condition")
                medication = patient.get("medication", "no active medication")
                
                st.success("Successfully generated referral summary.")
                narrative = (
                    f"**Referral Draft for {entered_patient_id}:**\n\n"
                    f"Dear Specialist,\n\n"
                    f"{patient_name} is presenting with {disease}, exhibiting symptoms and biological indicators consistent "
                    f"with recent metabolic and risk panels. Current disease management includes {medication}. "
                    f"I am referring this patient for further rigorous clinical workup and continued specialist monitoring."
                )
                st.markdown(narrative)
            else:
                st.error(f"Patient record for ID '{entered_patient_id}' not found. Cannot synthesize referral.")
        else:
            st.warning("Please enter a valid Patient ID to generate the referral.")
