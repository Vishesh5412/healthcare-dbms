import hashlib
import random

def pseudonymize(patient_id: str) -> str:
    """Hash the patient ID using SHA-256."""
    return hashlib.sha256(patient_id.encode('utf-8')).hexdigest()

def aggregate_age(age: int) -> str:
    """Convert an exact age into a 10-year bucket."""
    lower_bound = (age // 10) * 10
    upper_bound = lower_bound + 9
    return f"{lower_bound}-{upper_bound}"

def perturb_billing(billing_string: str) -> str:
    """Add +/- 10% random noise to billing string."""
    try:
        clean_str = billing_string.replace(",", "").replace("$", "").strip()
        val = float(clean_str)
        noise_factor = random.uniform(0.9, 1.1)
        perturbed = val * noise_factor
        return f"{perturbed:,.2f}"
    except (ValueError, TypeError):
        return billing_string

def anonymize_patient_record(patient: dict) -> dict:
    """Apply anonymization rules to a full patient dict."""
    anon = patient.copy()
    
    if "patient_id" in anon:
        anon["patient_id_hash"] = pseudonymize(anon["patient_id"])
        anon.pop("patient_id", None)
        
    if "age" in anon:
        anon["age_bucket"] = aggregate_age(int(anon["age"]))
        anon.pop("age", None)
        
    if "billing_info" in anon:
        anon["billing_info_perturbed"] = perturb_billing(anon["billing_info"])
        anon.pop("billing_info", None)
        
    # Strip direct identifiers
    anon.pop("patient_name", None)
    anon.pop("contact_no", None)
    anon.pop("_id", None) # Remove mongo internal ID if present
    
    # Keep only state/country/ZIP from address if possible
    if "address" in anon:
        address = str(anon["address"])
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 2:
            anon["address_approx"] = ", ".join(parts[-2:])
        else:
            anon["address_approx"] = "Unknown"
        anon.pop("address", None)
        
    return anon
