import streamlit as st
from database import get_mongo_client, log_audit_event
import pdf_utils

def get_patients_collection():
    return get_mongo_client()["clinical_db"]["patients"]

def get_summaries_collection():
    return get_mongo_client()["clinical_db"]["summaries"]

def view_legal_summaries():
    st.title("Legal Data Access")

    patients_coll = get_patients_collection()
    summaries_coll = get_summaries_collection()

    st.markdown("### Advanced Legal Discovery")
    entered_patient_id = st.text_input("Enter Patient ID for Discovery Query (e.g., P-12345-X)")
    keyword_filter = st.text_input("Keyword Search / Filter (Optional)", help="Dynamically filters returned discovery records.")

    if entered_patient_id:
        # Audit Log for Subpoena search
        log_audit_event(st.session_state.user["username"], "Legal", "Discovery Search", entered_patient_id)
        
        st.markdown("##### Precision Extraction Filters")
        available_keys = ["patient_id", "patient_name", "age", "disease", "medication", "billing_info", "contact_no", "isVerified"]
        keys_to_extract = st.multiselect(
            "Select Exact Keys for Discovery Extraction",
            available_keys,
            default=["patient_id", "patient_name", "contact_no"]
        )

        if keys_to_extract:
            demographic_projection = {"_id": 0}
            for k in keys_to_extract:
                demographic_projection[k] = 1

            patient = patients_coll.find_one({"patient_id": entered_patient_id}, demographic_projection)

            if patient:
                st.subheader("Extracted Legal Profile Parameters")
                st.json(patient)

                st.markdown("---")
                st.subheader("Legal Records")

                selected_string_id = patient.get("patient_id", entered_patient_id)

                # Strict Context Filtering — only Legal summaries returned
                legal_summaries = list(summaries_coll.find(
                    {"Patient_ID": selected_string_id, "Context_Type": "Legal"},
                    {"_id": 0, "Purpose_Name": 1, "Content_Data": 1}
                ))

                if legal_summaries:
                    displayed = 0
                    for idx, summary in enumerate(legal_summaries):
                        content = summary.get("Content_Data", "No content available.")
                        if keyword_filter and keyword_filter.lower() not in content.lower():
                            continue
                        displayed += 1
                        purpose = summary.get("Purpose_Name", "General Legal Context")
                        with st.expander(f"Record: {purpose}", expanded=True):
                            st.markdown(content)
                            pdf_bytes = pdf_utils.generate_pdf(selected_string_id, purpose, content)
                            st.download_button(
                                label="📥 Export Subpoena as PDF",
                                data=pdf_bytes,
                                file_name=f"subpoena_record_{selected_string_id}_{idx}.pdf",
                                mime="application/pdf"
                            )
                    if displayed == 0:
                        st.warning("No legal notes matched the keyword filter, but profile extraction was retrieved above.")
                else:
                    st.info("No legal summaries exist for this patient. Profile extraction retrieved above.")
            else:
                st.error(f"Patient record for ID '{entered_patient_id}' not found in databases.")
        else:
            st.warning("Please select at least one key to extract.")
    else:
        st.info("Enter a Patient ID for precise extraction workflows.")
