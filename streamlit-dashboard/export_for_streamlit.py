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

    # Exercise 5.3: Equipment status breakdown (donut) — simple GROUP BY, no recursion
    run("""
        SELECT ESTAT_DES as status, COUNT(*) as equipment_count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM STG_EHP__EQPM), 2) as pct
        FROM STG_EHP__EQPM
        GROUP BY ESTAT_DES ORDER BY equipment_count DESC
    """, "equipment_status_breakdown", conn)

    # Exercise 18: Salary equity gap summary (self-join on same dept + role) — donut
    run("""
        SELECT
            CASE
                WHEN ABS(s2.SAL_YR - s1.SAL_YR) <= 5000  THEN 'Equitable'
                WHEN ABS(s2.SAL_YR - s1.SAL_YR) <= 10000 THEN 'Moderate'
                ELSE 'Concern'
            END as gap_category,
            COUNT(*) as pair_count
        FROM STG_EHP__STFF s1
        JOIN STG_EHP__STFF s2 ON s1.DEP_ID = s2.DEP_ID AND s1.ROLE_DES = s2.ROLE_DES
        WHERE s1.STF_ID < s2.STF_ID
        GROUP BY gap_category
    """, "salary_equity_summary", conn)

    # ── Section C: Financial & Revenue Cycle ──────────────────────────────
    run("""
        SELECT BSTAT_DES AS bill_status, COUNT(*) AS bill_count,
               SUM(BILL_AMT) AS total_billed, AVG(BILL_AMT) AS avg_bill,
               ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(),1) AS pct_of_bills,
               ROUND(SUM(BILL_AMT)*100.0/SUM(SUM(BILL_AMT)) OVER(),1) AS pct_of_revenue
        FROM STG_EHP__BILL GROUP BY BSTAT_DES ORDER BY total_billed DESC
    """, "revenue_by_bill_status", conn)

    # Figure C-04: Monthly billing volume by status — simple GROUP BY, no joins
    run("""
        SELECT SUBSTR(BILL_DATE, 1, 7) AS year_month, BSTAT_DES AS bill_status,
               SUM(BILL_AMT) AS total_billed
        FROM STG_EHP__BILL
        WHERE BILL_DATE IS NOT NULL AND BILL_DATE != ''
        GROUP BY SUBSTR(BILL_DATE, 1, 7), BSTAT_DES
        ORDER BY year_month
    """, "monthly_billing_by_status", conn)

    # Figure C-06: Insurance coverage by visit type — EXISTS-based (avoids LEFT JOIN
    # fan-out double-counting when a patient has overlapping active policies).
    # Full population, no LIMIT — more stable than the notebook's LIMIT 1000 sample.
    run("""
        SELECT
            v.VTYPE_DES AS visit_type,
            CASE WHEN EXISTS (
                SELECT 1 FROM STG_EHP__INSR i
                WHERE i.PAT_ID = v.PAT_ID
                  AND i.ISTAT_DES = 'Active'
                  AND v.VIS_EN BETWEEN i.POL_ST AND i.POL_ED
            ) THEN 'Covered' ELSE 'Uninsured' END AS coverage_status,
            COUNT(*) AS visit_count
        FROM STG_EHP__VIST v
        WHERE v.VIS_EN IS NOT NULL AND v.VTYPE_DES IS NOT NULL
        GROUP BY v.VTYPE_DES, coverage_status
        ORDER BY v.VTYPE_DES, coverage_status
    """, "insurance_coverage_by_visit_type", conn)

    # ── Section D: Risk, Safety & Compliance ──────────────────────────────
    run("""
        SELECT MED_ID AS med_id, MED_NAME AS medicine_name, TYPE_DES AS type,
               EXP_MON AS months_to_expiry, COST_UN AS unit_cost
        FROM STG_EHP__MDCN WHERE EXP_MON <= 12 AND EXP_MON > 0
        ORDER BY EXP_MON ASC
    """, "medicines_expiring_soon", conn)

    # Exercise 33.2: Recursive visit-chain funnel (widened date window — 2025-only was
    # excluding most repeat visits that fall in adjacent years; using all-time data instead)
    run("""
        WITH RECURSIVE visit_chain AS (
            SELECT PAT_ID, visit_id, visit_date, visit_status, visit_sequence, first_visit_date
            FROM (
                SELECT v.PAT_ID, v.REFR_NO as visit_id, v.VIS_EN as visit_date,
                       v.VSTAT_DES as visit_status, 1 as visit_sequence, v.VIS_EN as first_visit_date
                FROM STG_EHP__VIST v
                WHERE v.VIS_EN IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM STG_EHP__VIST v2
                      WHERE v2.PAT_ID = v.PAT_ID AND v2.VIS_EN < v.VIS_EN
                  )
                ORDER BY v.VIS_EN ASC
                LIMIT 200
            )
            UNION ALL
            SELECT v.PAT_ID, v.REFR_NO, v.VIS_EN, v.VSTAT_DES, vc.visit_sequence + 1, vc.first_visit_date
            FROM visit_chain vc
            JOIN STG_EHP__VIST v ON vc.PAT_ID = v.PAT_ID
            WHERE v.VIS_EN > vc.visit_date AND vc.visit_sequence < 5
              AND NOT EXISTS (
                  SELECT 1 FROM STG_EHP__VIST v2
                  WHERE v2.PAT_ID = vc.PAT_ID AND v2.VIS_EN > vc.visit_date
                    AND v2.VIS_EN < v.VIS_EN
              )
        )
        SELECT visit_sequence, visit_status, COUNT(*) as visit_count
        FROM visit_chain
        GROUP BY visit_sequence, visit_status
        ORDER BY visit_sequence
    """, "visit_chain_funnel", conn)

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

    # Exercise 23: 30-day readmission rate vs national benchmark (CTE + self-join, no recursion)
    run("""
        WITH discharged_visits AS (
            SELECT
                COUNT(DISTINCT REFR_NO) AS total_discharges,
                COUNT(DISTINCT PAT_ID)  AS unique_patients
            FROM STG_EHP__VIST
            WHERE VSTAT_DES = 'Discharged'
        ),
        readmissions AS (
            SELECT
                COUNT(DISTINCT v1.REFR_NO) AS readmitted_visits,
                COUNT(DISTINCT v1.PAT_ID)  AS readmitted_patients
            FROM STG_EHP__VIST v1
            JOIN STG_EHP__VIST v2 ON v1.PAT_ID = v2.PAT_ID
            WHERE v1.VSTAT_DES = 'Discharged'
              AND v2.VIS_EN > v1.VIS_EX
              AND julianday(v2.VIS_EN) - julianday(v1.VIS_EX) <= 30
              AND v1.REFR_NO <> v2.REFR_NO
        )
        SELECT
            d.total_discharges,
            d.unique_patients                                            AS total_unique_patients,
            r.readmitted_visits,
            r.readmitted_patients                                        AS unique_readmitted_patients,
            ROUND(r.readmitted_visits   * 100.0 / d.total_discharges, 2) AS readmission_rate_pct,
            ROUND(r.readmitted_patients * 100.0 / d.unique_patients,  2) AS patient_readmission_rate_pct
        FROM discharged_visits d, readmissions r
    """, "readmission_rate_benchmark", conn)

    # Figure D-05: Vendor compliance status distribution — top-50-vendor cohort
    # (vendors with >=10 supplies, ranked by supply volume + lead time), matching notebook exactly
    run("""
        WITH top_vendors AS (
            SELECT v.VEN_ACC, v.VSTAT_DES AS vendor_status,
                   COUNT(DISTINCT s.SPL_ID) AS total_supplies,
                   AVG(julianday(s.RCVD_DATE) - julianday(s.MFG_DATE)) AS avg_lead
            FROM STG_EHP__VNDR v
            JOIN STG_EHP__SPLY s ON v.VEN_ACC = s.VEN_ACC
            WHERE s.MFG_DATE IS NOT NULL AND s.RCVD_DATE IS NOT NULL AND s.VRFC_DATE IS NOT NULL
            GROUP BY v.VEN_ACC, v.VSTAT_DES
            HAVING COUNT(DISTINCT s.SPL_ID) >= 10
            ORDER BY total_supplies DESC, avg_lead ASC
            LIMIT 50
        )
        SELECT vendor_status, COUNT(*) AS vendor_count,
               ROUND(COUNT(*)*100.0/50.0, 2) AS pct
        FROM top_vendors
        GROUP BY vendor_status
        ORDER BY vendor_count DESC
    """, "vendor_compliance_top50", conn)

    # Figure D-07 (swapped): Medication status, limited to items expiring within 12 months
    # (matches the same threshold as the already-working medicines_expiring_soon query,
    # which reliably returns 19,061 rows — narrower windows returned 0 rows in this dataset)
    run("""
        SELECT MSTAT_DES AS status, COUNT(*) AS medication_count,
               ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM STG_EHP__MDCN WHERE EXP_MON <= 12 AND EXP_MON > 0),2) AS pct
        FROM STG_EHP__MDCN
        WHERE EXP_MON <= 12 AND EXP_MON > 0
        GROUP BY MSTAT_DES ORDER BY medication_count DESC
    """, "medication_status_full", conn)

    # Figure E-08: Treatment status distribution via LEAD/LAG (Exercise 32, LIMIT 100,
    # first 5 treatments per patient from 2025 onward — matches notebook exactly)
    run("""
        WITH patient_treatments AS (
            SELECT
                t.REFR_NO, v.PAT_ID, t.TRTM_EN as treatment_date, t.TSTAT_DES as treatment_status,
                ROW_NUMBER() OVER (PARTITION BY v.PAT_ID ORDER BY t.TRTM_EN) as treatment_sequence
            FROM STG_EHP__TRTM t
            JOIN STG_EHP__VIST v ON t.REFR_NO = v.REFR_NO
            WHERE t.TRTM_EN >= DATE('2025-01-01')
        )
        SELECT
            treatment_status, treatment_date, PAT_ID,
            LEAD(treatment_date, 1) OVER (PARTITION BY PAT_ID ORDER BY treatment_date) as next_treatment_date
        FROM patient_treatments
        WHERE treatment_sequence <= 5
        ORDER BY PAT_ID, treatment_sequence
        LIMIT 100
    """, "treatment_status_leadlag", conn)

    conn.close()

    print(f"\nDone. CSVs are in: {OUT_DIR}")
    print("Next: copy the data/ folder + streamlit_app.py + requirements.txt into your repo and push.")


if __name__ == "__main__":
    main()
