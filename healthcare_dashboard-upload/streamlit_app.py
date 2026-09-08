"""
Healthcare Analytics — Interactive Streamlit Dashboard
Reads pre-aggregated CSVs from ./data (produced by export_for_streamlit.py)
so the app stays lightweight enough to run on Streamlit Community Cloud.
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
)


@st.cache_data
def load_csv(name):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def missing_data_notice(name):
    st.info(
        f"`{name}.csv` not found in the data folder yet. "
        f"Run `export_for_streamlit.py` locally and commit the `data/` folder to see this chart."
    )


# ── Header ─────────────────────────────────────────────────────────────────
st.title("🏥 Healthcare Data Analysis Dashboard")
st.caption(
    "Synthetic dataset · 17 tables · 7M+ rows · Built with SQLite + Python + Streamlit — "
    "[View the full SQL notebook & report on GitHub](https://github.com/Mehmoodkhans/healthcare-analytics)"
)

# ── Executive KPIs ────────────────────────────────────────────────────────
kpis = load_csv("executive_kpis")
if kpis is not None and len(kpis) > 0:
    row = kpis.iloc[0]
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Patients", f"{row['total_patients']:,.0f}")
    c2.metric("Visits", f"{row['total_visits']:,.0f}")
    c3.metric("Appointments", f"{row['total_appointments']:,.0f}")
    c4.metric("Active Staff", f"{row['active_staff']:,.0f}")
    c5.metric("Departments", f"{row['total_departments']:,.0f}")
    c6.metric("Total Revenue", f"${row['total_revenue']:,.0f}")
else:
    missing_data_notice("executive_kpis")

st.divider()

tab_a, tab_b, tab_c, tab_d = st.tabs(
    ["👥 Patient & Care Quality", "🏢 Operations & Capacity", "💰 Financial & Revenue Cycle", "⚠️ Risk & Safety"]
)

# ── Section A: Patient & Care Quality ────────────────────────────────────
with tab_a:
    col1, col2 = st.columns(2)

    with col1:
        df = load_csv("blood_type_distribution")
        if df is not None:
            fig = px.bar(
                df, x="blood_type", y="patient_count",
                title="Patient Count by Blood Type",
                labels={"blood_type": "Blood Type", "patient_count": "Patients"},
                color="patient_count", color_continuous_scale="Blues",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            missing_data_notice("blood_type_distribution")

    with col2:
        df = load_csv("blood_type_by_gender")
        if df is not None:
            fig = px.bar(
                df, x="blood_type", y="total_patients", color="gender",
                barmode="group", title="Blood Type × Gender",
                labels={"blood_type": "Blood Type", "total_patients": "Patients"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            missing_data_notice("blood_type_by_gender")

    col3, col4 = st.columns(2)

    with col3:
        df = load_csv("patient_dob_raw")
        if df is not None:
            df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
            df["age"] = ((pd.Timestamp.now() - df["dob"]).dt.days / 365.25)
            df = df[(df["age"] >= 0) & (df["age"] <= 120)]

            def bucket(a):
                if a < 18: return "0-17"
                if a < 35: return "18-34"
                if a < 50: return "35-49"
                if a < 65: return "50-64"
                return "65+"

            df["age_group"] = df["age"].apply(bucket)
            counts = df["age_group"].value_counts().reindex(["0-17", "18-34", "35-49", "50-64", "65+"]).reset_index()
            counts.columns = ["age_group", "count"]
            fig = px.pie(counts, names="age_group", values="count", title="Patients by Age Group", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            missing_data_notice("patient_dob_raw")

    with col4:
        df = load_csv("visit_status_breakdown")
        if df is not None:
            fig = px.bar(
                df.sort_values("total_visits"), x="total_visits", y="visit_status",
                orientation="h", title="Visit Status Breakdown",
                labels={"total_visits": "Visits", "visit_status": "Status"},
                color="total_visits", color_continuous_scale="Teal",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            missing_data_notice("visit_status_breakdown")

    df = load_csv("allergy_severity")
    if df is not None:
        fig = px.bar(df, x="severity", y="count", title="Allergy Records by Severity", color="severity")
        st.plotly_chart(fig, use_container_width=True)
    else:
        missing_data_notice("allergy_severity")

# ── Section B: Operations & Capacity ─────────────────────────────────────
with tab_b:
    col1, col2 = st.columns(2)

    with col1:
        df = load_csv("appointment_type_distribution")
        if df is not None:
            fig = px.pie(df, names="appointment_type", values="total_appointments", title="Appointment Type Mix")
            st.plotly_chart(fig, use_container_width=True)
        else:
            missing_data_notice("appointment_type_distribution")

    with col2:
        df = load_csv("staff_by_department")
        if df is not None:
            fig = px.bar(
                df.sort_values("total_staff"), x="total_staff", y="department",
                orientation="h", title="Staff Headcount by Department",
                color="avg_salary", color_continuous_scale="Purples",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            missing_data_notice("staff_by_department")

    df = load_csv("monthly_appointment_trend")
    if df is not None:
        fig = px.line(
            df.sort_values("year_month"), x="year_month", y="total_appointments",
            markers=True, title="Monthly Appointment Volume Trend",
            labels={"year_month": "Month", "total_appointments": "Appointments"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        missing_data_notice("monthly_appointment_trend")

# ── Section C: Financial & Revenue Cycle ─────────────────────────────────
with tab_c:
    df = load_csv("revenue_by_bill_status")
    if df is not None:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                df.sort_values("total_billed"), x="total_billed", y="bill_status",
                orientation="h", title="Total Billed by Status ($)",
                labels={"total_billed": "Total Billed ($)", "bill_status": "Status"},
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.pie(df, names="bill_status", values="pct_of_revenue", title="Share of Revenue by Bill Status")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)
    else:
        missing_data_notice("revenue_by_bill_status")

# ── Section D: Risk, Safety & Compliance ─────────────────────────────────
with tab_d:
    col1, col2 = st.columns(2)

    with col1:
        df = load_csv("readmission_windows")
        if df is not None:
            fig = px.bar(df, x="readmission_window", y="count", title="Readmission Timing Distribution", color="readmission_window")
            st.plotly_chart(fig, use_container_width=True)
        else:
            missing_data_notice("readmission_windows")

    with col2:
        df = load_csv("medicines_expiring_soon")
        if df is not None:
            fig = px.scatter(
                df, x="months_to_expiry", y="unit_cost", color="type",
                hover_name="medicine_name", title="Medicines Expiring Within 12 Months",
                labels={"months_to_expiry": "Months to Expiry", "unit_cost": "Unit Cost ($)"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            missing_data_notice("medicines_expiring_soon")

st.divider()
st.caption("Built from a 36-exercise SQL analytics project · Data is entirely synthetic (Kaggle training dataset).")
