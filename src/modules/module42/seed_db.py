import datetime
import bcrypt
import random
from database import get_mongo_client

def hash_pw(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

# ── Realistic patient data ────────────────────────────────────────────────────
PATIENTS = [
    {"patient_id": "P-10021-A", "patient_name": "James Harrington",  "age": 58, "disease": "Hypertension",          "medication": "Amlodipine 5mg",         "billing_info": "Visa",       "contact_no": "312-554-0921", "isVerified": True},
    {"patient_id": "P-10022-B", "patient_name": "Sarah Mitchell",    "age": 34, "disease": "Type 2 Diabetes",       "medication": "Metformin 500mg",         "billing_info": "Mastercard", "contact_no": "415-223-7741", "isVerified": True},
    {"patient_id": "P-10023-C", "patient_name": "David Okonkwo",     "age": 47, "disease": "Asthma",                "medication": "Salbutamol Inhaler",      "billing_info": "Amex",       "contact_no": "718-334-5582", "isVerified": False},
    {"patient_id": "P-10024-D", "patient_name": "Priya Nair",        "age": 62, "disease": "Coronary Artery Disease","medication": "Atorvastatin 40mg",      "billing_info": "Discover",   "contact_no": "512-667-3390", "isVerified": True},
    {"patient_id": "P-10025-E", "patient_name": "Michael Torres",    "age": 29, "disease": "Anxiety Disorder",      "medication": "Sertraline 50mg",         "billing_info": "Visa",       "contact_no": "617-445-8812", "isVerified": True},
    {"patient_id": "P-10026-F", "patient_name": "Linda Zhao",        "age": 71, "disease": "Osteoarthritis",        "medication": "Celecoxib 200mg",         "billing_info": "Mastercard", "contact_no": "404-772-1023", "isVerified": True},
    {"patient_id": "P-10027-G", "patient_name": "Robert Flemming",   "age": 55, "disease": "Chronic Kidney Disease","medication": "Lisinopril 10mg",         "billing_info": "Visa",       "contact_no": "202-381-9944", "isVerified": False},
    {"patient_id": "P-10028-H", "patient_name": "Angela Brooks",     "age": 41, "disease": "Hypothyroidism",        "medication": "Levothyroxine 75mcg",     "billing_info": "Amex",       "contact_no": "305-559-2281", "isVerified": True},
    {"patient_id": "P-10029-I", "patient_name": "Carlos Mendez",     "age": 38, "disease": "Migraine",              "medication": "Sumatriptan 50mg",        "billing_info": "Discover",   "contact_no": "213-448-6630", "isVerified": True},
    {"patient_id": "P-10030-J", "patient_name": "Emily Watson",      "age": 66, "disease": "COPD",                  "medication": "Tiotropium Bromide 18mcg","billing_info": "Visa",       "contact_no": "503-334-7721", "isVerified": True},
]


# ── Realistic clinical summaries per context ──────────────────────────────────
CLINICAL_SUMMARIES = {
    "P-10021-A": [
        ("Treatment",       "Patient James Harrington presents with Stage 2 hypertension (BP: 158/96 mmHg). Amlodipine 5mg prescribed once daily. Patient advised to reduce sodium intake, increase physical activity to 30 minutes daily, and avoid smoking. Follow-up scheduled in 4 weeks to re-evaluate blood pressure response."),
        ("Routine Checkup", "Routine cardiovascular examination completed. ECG results within normal range. Patient reports occasional dizziness in the mornings, possibly orthostatic. No changes to current medication regimen. Lipid panel ordered for next visit."),
    ],
    "P-10022-B": [
        ("Treatment",       "Sarah Mitchell diagnosed with Type 2 Diabetes Mellitus (HbA1c: 7.8%). Metformin 500mg initiated twice daily with meals. Dietary counselling provided — emphasis on low glycaemic index foods. Self-monitoring blood glucose twice daily advised. Referral to endocrinology for specialist review."),
        ("Consultation",    "Patient expressed concerns regarding weight gain since diabetes diagnosis. Nutritional assessment performed. BMI recorded at 28.4 (overweight). Calorie-deficit diet plan provided. Blood glucose trending downward — Metformin dosage to remain unchanged for next 8 weeks."),
    ],
    "P-10023-C": [
        ("Treatment",       "David Okonkwo presents with moderate persistent asthma. Salbutamol inhaler (100mcg/dose) prescribed for acute episodes. Inhaler technique reviewed and corrected during consultation. Spirometry results: FEV1/FVC ratio 0.68, indicating airway obstruction. Corticosteroid preventer inhaler added to therapy plan."),
        ("Routine Checkup", "Peak flow reading stable at 480 L/min. Patient reports 2 nocturnal episodes over past month. Trigger assessment completed — dust mites and pet dander identified as primary triggers. Bedding hygiene recommendations provided."),
    ],
    "P-10024-D": [
        ("Treatment",       "Priya Nair diagnosed with stable Coronary Artery Disease confirmed by recent angiography. Atorvastatin 40mg initiated nightly. Aspirin 75mg added as antiplatelet therapy. Patient counselled on cardiac rehabilitation programme. Exercise stress test scheduled for 6-week follow-up."),
        ("Consultation",    "Cardiology consultation completed. Left ventricular ejection fraction (LVEF) at 52% — mildly reduced. Beta-blocker therapy (Metoprolol 25mg) added. Patient educated on symptom recognition for angina progression and emergency protocols."),
    ],
    "P-10025-E": [
        ("Treatment",       "Michael Torres presents with Generalised Anxiety Disorder (GAD-7 score: 14 — moderate-severe). Sertraline 50mg initiated with plan to titrate to 100mg after 4 weeks if tolerated. CBT referral placed. Sleep hygiene education provided. Review in 6 weeks."),
        ("Consultation",    "Patient reports improvement in anxiety symptoms (GAD-7 score reduced to 9). Sertraline dose increased to 100mg. Patient engaged positively with CBT sessions. Continued monitoring for SSRI side effects, particularly nausea and insomnia."),
    ],
    "P-10026-F": [
        ("Treatment",       "Linda Zhao presents with bilateral knee osteoarthritis (Kellgren-Lawrence Grade III on X-ray). Celecoxib 200mg once daily prescribed for pain management. Physiotherapy referral arranged. Weight management programme recommended to reduce joint load. NSAID gastroprotection assessed — PPI added."),
        ("Routine Checkup", "Patient reports 40% reduction in knee pain following physiotherapy. Celecoxib continued. Renal function and liver enzymes within acceptable range. Discussed knee replacement surgery as long-term option if conservative management fails."),
    ],
    "P-10027-G": [
        ("Treatment",       "Robert Flemming has CKD Stage 3b (eGFR: 32 mL/min/1.73m²). Lisinopril 10mg initiated for nephroprotection and blood pressure control. Dietary protein restriction (<0.8g/kg/day) advised. Potassium and phosphate dietary guidance given. Nephrology outpatient referral submitted."),
        ("Consultation",    "Nephrology review completed. eGFR stable at 31. Haemoglobin 10.2 g/dL — mild anaemia of chronic disease confirmed. Iron studies ordered. Erythropoiesis-stimulating agent therapy discussed pending further results."),
    ],
    "P-10028-H": [
        ("Treatment",       "Angela Brooks diagnosed with primary hypothyroidism (TSH: 8.9 mIU/L, Free T4: 9.2 pmol/L). Levothyroxine 75mcg commenced once daily, fasting, 30 minutes before breakfast. Patient educated on medication interactions (avoid calcium/iron supplements within 4 hours). Repeat TFTs in 6 weeks."),
        ("Routine Checkup", "TSH now reduced to 3.1 mIU/L — within target range. Patient reports improvement in fatigue and cold intolerance. Levothyroxine dose maintained. Annual thyroid function tests scheduled."),
    ],
    "P-10029-I": [
        ("Treatment",       "Carlos Mendez presents with episodic migraine with aura (4–5 attacks/month). Sumatriptan 50mg prescribed for acute attacks. Triggers identified: irregular sleep, caffeine withdrawal, and dehydration. Patient advised to maintain a migraine diary. Prophylactic therapy (Topiramate) discussed if frequency persists."),
        ("Consultation",    "Patient migraine frequency reduced to 2 attacks/month since lifestyle modifications. Sumatriptan usage within recommended limits (≤9 days/month). Neurological examination normal. Continue current management and review in 3 months."),
    ],
    "P-10030-J": [
        ("Treatment",       "Emily Watson with COPD GOLD Stage III (FEV1: 38% predicted). Tiotropium Bromide 18mcg once daily (dry powder inhaler) initiated. Pulmonary rehabilitation programme referral submitted. Influenza and pneumococcal vaccinations administered. Smoking cessation support provided — Varenicline prescribed."),
        ("Routine Checkup", "6-Minute Walk Test: 310 metres — moderate functional limitation. Patient reports reduced dyspnoea since starting Tiotropium. SpO2 at rest: 93% — supplemental oxygen assessment to be considered if <88% on exertion. Continue current COPD management plan."),
    ],
}

RESEARCH_SUMMARIES = [
    ("P-10021-A", "Cohort Study",          "Patient within the hypertension management cohort. Calcium channel blocker response being monitored over 12-month period. Baseline cardiovascular risk score (SCORE2): 8.4%. Blood pressure mean over 3 readings at enrolment: 155/94 mmHg. Enrolled in lifestyle modification arm."),
    ("P-10022-B", "Clinical Trial",        "Subject enrolled in GLYCO-CONTROL Trial (NCT-20240819). Randomised to Metformin standard arm. Fasting plasma glucose at baseline: 9.2 mmol/L. Week 12 HbA1c: 7.1% (improvement noted). No adverse events reported. Compliance rate: 94%."),
    ("P-10023-C", "Epidemiological Study", "Asthma exacerbation frequency tracked over 6-month study window. 3 ED visits recorded in preceding year. Post-intervention (inhaler education + trigger avoidance), zero ED visits in study period. Contributing to urban air quality and asthma severity correlation analysis."),
    ("P-10024-D", "Cohort Study",          "CAD secondary prevention cohort — statin therapy optimisation study. LDL-C at enrolment: 3.6 mmol/L. After 8 weeks on Atorvastatin 40mg, LDL-C reduced to 1.9 mmol/L (47% reduction). MACE risk stratification: high-risk. Continued monitoring for hepatotoxicity markers."),
    ("P-10025-E", "Clinical Trial",        "Participant in ANXIO-PHARM RCT evaluating SSRI efficacy in GAD. Randomised to 100mg Sertraline arm. PHQ-9 score at baseline: 13. Week-8 score: 6 (significant improvement). Dropout risk assessed as low. Adverse event log: mild transient nausea in weeks 1–2."),
    ("P-10026-F", "Epidemiological Study", "Part of musculoskeletal disease burden study. Osteoarthritis severity correlating with BMI, age, and occupational exposure. WOMAC index score at baseline: 52/96. Post-physiotherapy WOMAC: 34/96. Functional mobility significantly improved at 12-week mark."),
    ("P-10027-G", "Cohort Study",          "CKD progression monitoring study. Enrolment eGFR: 32 mL/min/1.73m². Proteinuria (urine ACR): 48 mg/mmol — significantly elevated. ACEI therapy impact on rate of GFR decline being assessed over 24 months. Dietary compliance questionnaire completed — moderate adherence."),
    ("P-10028-H", "Clinical Trial",        "Hypothyroid replacement trial — Levothyroxine dose optimisation study. TSH target range: 1.0–3.0 mIU/L. Patient achieved target at week 6 on 75mcg dose. Quality of life improvement recorded using ThyPRO questionnaire scores — 34% improvement in fatigue subscale."),
    ("P-10029-I", "Epidemiological Study", "Migraine prevalence and trigger mapping cohort. Monthly headache days (MHDs): reduced from 5.2 to 2.1 after behavioural intervention. MIDAS (Migraine Disability Assessment) Grade reduced from III to I. Contributing to population-level migraine burden estimation."),
    ("P-10030-J", "Cohort Study",          "COPD natural history cohort — rate of FEV1 decline and hospitalisation frequency analysis. Annual FEV1 decline: 42 mL/year (above expected). COPD Assessment Test (CAT) score: 22 (high impact). Exacerbation frequency: 2/year. Candidate for biologics trial pending further assessment."),
]

ADMINISTRATIVE_SUMMARIES = [
    ("P-10021-A", "Insurance Verification", "Insurance verification completed for James Harrington. Policy: BlueCross PPO. Coverage confirmed for hypertension management, including medication and specialist referrals. Annual deductible: $1,200 — met. Pre-authorisation for echocardiogram approved."),
    ("P-10022-B", "Billing Issue",          "Billing discrepancy identified for Sarah Mitchell. Claim #CLM-2024-7732 for endocrinology consult initially denied — incorrect procedure code submitted (99213 vs 99214). Claim resubmitted with corrected code and supporting documentation. Resolution pending 15 business days."),
    ("P-10023-C", "Scheduling",             "David Okonkwo scheduled for pulmonology follow-up — Slot: 3rd May 2026, 10:30 AM. Inhaler device and spacer training session booked with respiratory nurse. Patient notified via registered mobile number. Transport assistance requested and arranged."),
    ("P-10024-D", "Insurance Verification", "Priya Nair — cardiac rehabilitation programme pre-authorisation submitted to insurer (Aetna HMO). 12-session programme approved. Start date: 22nd April 2026. Co-pay: $30 per session. Cardiology outpatient follow-up claims submitted for processing."),
    ("P-10025-E", "Billing Issue",          "Outstanding balance of $340 for Michael Torres (CBT sessions x4). Patient on financial assistance programme — 60% fee reduction applied. Final balance revised to $136. Payment plan arranged: $34/month over 4 months. Patient acknowledgement form signed."),
    ("P-10026-F", "Scheduling",             "Linda Zhao — knee replacement surgical assessment appointment confirmed: 8th May 2026, 2:00 PM with Dr. R. Patel (Orthopaedics). Pre-operative bloods, ECG, and chest X-ray ordered. Anaesthesiology pre-assessment referral submitted."),
    ("P-10027-G", "Insurance Verification", "Robert Flemming — Nephrology outpatient and CKD-specific dietary counselling covered under Medicare Part B. Erythropoiesis-stimulating agent prior authorisation submitted. ESRD risk classification: Stage 3b, high progression risk — flagged for care management programme enrolment."),
    ("P-10028-H", "Scheduling",             "Angela Brooks — follow-up thyroid function test scheduled: 28th April 2026. Lab slip issued for TSH, Free T4, and Anti-TPO antibody panel. Annual review with GP added to patient's care calendar. Reminder SMS sent."),
    ("P-10029-I", "Billing Issue",          "Carlos Mendez — pharmacy benefit query raised regarding Sumatriptan refill frequency. PBM (pharmacy benefit manager) confirmed: 9 units/30 days covered under formulary Tier 2. Co-pay: $25. Patient counselled on medication overuse headache risk at current utilisation frequency."),
    ("P-10030-J", "Scheduling",             "Emily Watson — pulmonary rehabilitation referral accepted. Programme start: 2nd May 2026. 18-session group-based programme (3x/week for 6 weeks). Spirometry and 6MWT to be repeated at programme completion. Supplemental oxygen assessment to be conducted mid-programme."),
]

LEGAL_SUMMARIES = [
    ("P-10021-A", "Internal Audit",   "Medical records audit for James Harrington completed. All hypertension treatment notes, prescription logs, and follow-up entries verified for completeness and accuracy. No discrepancies identified. Records compliant with HIPAA documentation standards. Audit trail archived."),
    ("P-10022-B", "Subpoena Response","Legal disclosure prepared for Sarah Mitchell in response to personal injury civil claim. Medical records from 2023–2025 released to requesting legal counsel per court-approved subpoena (Case No. CV-2025-3341). Records cover diabetes management history. Patient notified per legal protocol."),
    ("P-10023-C", "Court Order",      "Court-ordered release of David Okonkwo's asthma treatment records for disability benefit appeal (Case Ref: DWP-2025-7821). Records provided include spirometry reports, prescription history, and GP letters confirming chronic respiratory condition. Release authorised by appointed legal guardian."),
    ("P-10024-D", "Internal Audit",   "Cardiology treatment records for Priya Nair reviewed for quality assurance audit. All clinical entries verified: angiography reports, cardiology consultation notes, medication logs, and rehabilitation referrals are complete and timestamped. No gaps in clinical documentation identified."),
    ("P-10025-E", "Subpoena Response","Psychiatric records for Michael Torres released in child custody legal proceedings (Family Court Case FC-2026-112). Records limited to GAD diagnosis, treatment compliance, and clinician assessments of functional capacity. Records vetted by hospital legal team prior to disclosure."),
]

def main():
    client = get_mongo_client()
    db = client["clinical_db"]
    users_coll    = db["users"]
    patients_coll = db["patients"]
    summaries_coll = db["summaries"]

    # Clear existing data
    users_coll.delete_many({})
    patients_coll.delete_many({})
    summaries_coll.delete_many({})
    print("[OK] Cleared existing data.")

    # 1. Seed users
    roles = ["Clinical", "Research", "Administrative", "Legal"]
    users = []
    full_names = ["Dr. Amelia Chen", "Dr. Kevin Walsh", "Sandra Obi", "Marcus Reid"]
    for role, name in zip(roles, full_names):
        users.append({
            "username":  f"{role.lower()}_user",
            "password":  hash_pw(f"{role.lower()}123"),
            "role":      role,
            "full_name": name
        })
    users_coll.insert_many(users)

    # 2. Seed patients
    patients_coll.insert_many(PATIENTS)

    # 3. Seed summaries
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    summaries = []

    for patient_id, summary_list in CLINICAL_SUMMARIES.items():
        for purpose, content in summary_list:
            summaries.append({
                "Patient_ID":           patient_id,
                "Content_Data":         content,
                "Context_Type":         "Clinical",
                "Purpose_Name":         purpose,
                "Generated_Timestamp":  now_utc.isoformat()
            })

    for patient_id, (purpose, content) in [(s[0], (s[1], s[2])) for s in RESEARCH_SUMMARIES]:
        summaries.append({
            "Patient_ID":           patient_id,
            "Content_Data":         content,
            "Context_Type":         "Research",
            "Purpose_Name":         purpose,
            "Generated_Timestamp":  now_utc.isoformat()
        })

    for patient_id, (purpose, content) in [(s[0], (s[1], s[2])) for s in ADMINISTRATIVE_SUMMARIES]:
        summaries.append({
            "Patient_ID":           patient_id,
            "Content_Data":         content,
            "Context_Type":         "Administrative",
            "Purpose_Name":         purpose,
            "Generated_Timestamp":  now_utc.isoformat()
        })

    for patient_id, (purpose, content) in [(s[0], (s[1], s[2])) for s in LEGAL_SUMMARIES]:
        summaries.append({
            "Patient_ID":           patient_id,
            "Content_Data":         content,
            "Context_Type":         "Legal",
            "Purpose_Name":         purpose,
            "Generated_Timestamp":  now_utc.isoformat()
        })

    summaries_coll.insert_many(summaries)

    # ── Seed mock audit logs for heatmap ─────────────────────────────────────
    print("Generating mock audit logs for presentation heatmap...")
    audit_coll = db["audit_logs"]
    audit_coll.delete_many({})
    
    import random
    from datetime import timedelta
    
    audit_logs = []
    actions = ["Searched Patient", "Viewed Summaries", "Generated Summary", "Exported PDF"]
    for _ in range(85):
        # random day in the last 7 days
        days_ago = random.randint(0, 7)
        mock_date = now_utc - timedelta(days=days_ago, hours=random.randint(0,23))
        
        mock_role = random.choice(roles)
        mock_user = f"{mock_role.lower()}_user"
        mock_action = random.choice(actions)
        mock_patient = random.choice(PATIENTS)["patient_id"]
        
        audit_logs.append({
            "timestamp": mock_date,
            "username": mock_user,
            "role": mock_role,
            "action": mock_action,
            "patient_id": mock_patient
        })
    
    audit_coll.insert_many(audit_logs)

    print(f"\n[OK] Seeded {len(PATIENTS)} patients, {len(summaries)} realistic summaries, {len(users)} users, {len(audit_logs)} audit logs.\n")
    print("-" * 55)
    print(f"{'Role':<16} | {'Username':<22} | {'Password'}")
    print("-" * 55)
    for role in roles:
        print(f"{role:<16} | {role.lower()+'_user':<22} | {role.lower()}123")
    print("-" * 55)
    print("\nPatient IDs:")
    for p in PATIENTS:
        print(f"  {p['patient_id']}  —  {p['patient_name']}  ({p['disease']})")

if __name__ == "__main__":
    main()
