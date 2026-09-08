"""
================================================================================
EXPORT FOR STREAMLIT — run this ONCE on your local machine
================================================================================
This does NOT touch your notebook. It connects directly to your existing
healthcare.db and dumps ~15 small, already-aggregated result sets as CSVs
into a `data/` folder. Those CSVs (a few KB–MB total) are what gets committed
to GitHub and read by streamlit_app.py — your 1.2GB database never leaves
your machine.

USAGE:
    1. Update DB_PATH below to match Cell 3 of your notebook.
    2. python export_for_streamlit.py
    3. A `data/` folder appears next to this script, full of .csv files.
    4. Copy that `data/` folder + streamlit_app.py + requirements.txt into
       your healthcare-analytics repo and push to GitHub.
================================================================================
"""

import os
import sqlite3
import pandas as pd

# ── UPDATE THIS to match DB_PATH in your notebook's Cell 3 ───────────────────
DB_PATH = r"C:\Users\ADMIN\Desktop\HC\healthcare.db"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT_DIR, exist_ok=True)


def run(query, name, conn):
    """Run a query, save to data/<name>.csv, print row count."""
    try:
        df = pd.read_sql_query(query, conn)
        df.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"  ✅ {name:<28} {len(df):>8,} rows")
    except Exception as e:
        print(f"  ❌ {name:<28} FAILED: {e}")


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH} — update DB_PATH above.")

    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to {DB_PATH}")
    print(f"Writing CSVs to {OUT_DIR}\n")

    # ── Section A: Patient & Care Quality ─────────────────────────────────
    run("""
        SELECT B_TYPE AS blood_type, COUNT(*) AS patient_count,
               ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM STG_EHP__PATN),2) AS pct
        FROM STG_EHP__PATN GROUP BY B_TYPE ORDER BY patient_count DESC
    """, "blood_type_distribution", conn)

    run("""
        SELECT B_TYPE AS blood_type, GEN_DES AS gender, COUNT(*) AS total_patients
        FROM STG_EHP__PATN GROUP BY B_TYPE, GEN_DES
    """, "blood_type_by_gender", conn)

    run("""
        SELECT PAT_ID AS pat_id, DT_BRT AS dob FROM STG_EHP__PATN
    """, "patient_dob_raw", conn)  # age bucketed client-side in the app

    run("""
        SELECT VSTAT_DES AS visit_status, COUNT(*) AS total_visits,
               ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM STG_EHP__VIST),2) AS pct
        FROM STG_EHP__VIST GROUP BY VSTAT_DES ORDER BY total_visits DESC
    """, "visit_status_breakdown", conn)

    run("""
        SELECT p.SVR_DES AS severity, COUNT(*) AS count
        FROM STG_EHP__PTAL p GROUP BY p.SVR_DES ORDER BY count DESC
    """, "allergy_severity", conn)

    # ── Section B: Operations & Capacity ──────────────────────────────────
    run("""
        SELECT ATYPE_DES AS appointment_type, COUNT(*) AS total_appointments,
               ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM STG_EHP__APPT),2) AS pct
        FROM STG_EHP__APPT GROUP BY ATYPE_DES ORDER BY total_appointments DESC
    """, "appointment_type_distribution", conn)

    run("""
        SELECT SUBSTR(APT_TIME,1,7) AS year_month, COUNT(*) AS total_appointments
        FROM STG_EHP__APPT WHERE APT_TIME IS NOT NULL AND APT_TIME != ''
        GROUP BY SUBSTR(APT_TIME,1,7) ORDER BY year_month
    """, "monthly_appointment_trend", conn)

    run("""
        SELECT d.DEP_NAME AS department, COUNT(s.STF_ID) AS total_staff,
               AVG(s.SAL_YR) AS avg_salary, SUM(s.SAL_YR) AS total_payroll
        FROM STG_EHP__DPMT d LEFT JOIN STG_EHP__STFF s ON d.DEP_ID = s.DEP_ID
        GROUP BY d.DEP_NAME HAVING COUNT(s.STF_ID) > 0
        ORDER BY total_staff DESC
    """, "staff_by_department", conn)

    run("""
        SELECT d.DEP_NAME AS department, d.DEP_LOC AS location
        FROM STG_EHP__DPMT d ORDER BY d.DEP_LOC
    """, "department_locations", conn)

    # ── Section C: Financial & Revenue Cycle ──────────────────────────────
    run("""
        SELECT BSTAT_DES AS bill_status, COUNT(*) AS bill_count,
               SUM(BILL_AMT) AS total_billed, AVG(BILL_AMT) AS avg_bill,
               ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(),1) AS pct_of_bills,
               ROUND(SUM(BILL_AMT)*100.0/SUM(SUM(BILL_AMT)) OVER(),1) AS pct_of_revenue
        FROM STG_EHP__BILL GROUP BY BSTAT_DES ORDER BY total_billed DESC
    """, "revenue_by_bill_status", conn)

    # ── Section D: Risk, Safety & Compliance ──────────────────────────────
    run("""
        SELECT MED_ID AS med_id, MED_NAME AS medicine_name, TYPE_DES AS type,
               EXP_MON AS months_to_expiry, COST_UN AS unit_cost
        FROM STG_EHP__MDCN WHERE EXP_MON <= 12 AND EXP_MON > 0
        ORDER BY EXP_MON ASC
    """, "medicines_expiring_soon", conn)

    # 30-day readmissions — self-join on visits (VIS_EN = visit entry/check-in timestamp)
    run("""
        WITH visits AS (
            SELECT PAT_ID, REFR_NO, VIS_EN
            FROM STG_EHP__VIST WHERE VIS_EN IS NOT NULL AND VIS_EN != ''
        )
        SELECT
            CASE
                WHEN julianday(v2.VIS_EN) - julianday(v1.VIS_EN) <= 30 THEN 'Within 30 days'
                WHEN julianday(v2.VIS_EN) - julianday(v1.VIS_EN) <= 90 THEN '31-90 days'
                ELSE '90+ days'
            END AS readmission_window,
            COUNT(*) AS count
        FROM visits v1
        JOIN visits v2 ON v1.PAT_ID = v2.PAT_ID AND v2.VIS_EN > v1.VIS_EN
        GROUP BY readmission_window
    """, "readmission_windows", conn)

    # ── Section E/F: Executive summary KPIs (single-row table) ───────────
    run("""
        SELECT
            (SELECT COUNT(*) FROM STG_EHP__PATN) AS total_patients,
            (SELECT COUNT(*) FROM STG_EHP__VIST) AS total_visits,
            (SELECT COUNT(*) FROM STG_EHP__APPT) AS total_appointments,
            (SELECT COUNT(*) FROM STG_EHP__STFF WHERE STAT_CD = 0) AS active_staff,
            (SELECT SUM(BILL_AMT) FROM STG_EHP__BILL) AS total_revenue,
            (SELECT COUNT(*) FROM STG_EHP__DPMT) AS total_departments
    """, "executive_kpis", conn)

    conn.close()
    print(f"\nDone. CSVs are in: {OUT_DIR}")
    print("Next: copy the data/ folder + streamlit_app.py + requirements.txt into your repo and push.")


if __name__ == "__main__":
    main()
