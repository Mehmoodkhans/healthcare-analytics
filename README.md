# 🏥 Healthcare Data Analysis Project

A comprehensive **SQL + Python** analytics project built on a synthetic healthcare dataset of **17 tables and 7,078,107 rows**. The project progresses from foundational SQL through advanced techniques including window functions, recursive CTEs, and multi-dimensional risk scoring — all applied to realistic healthcare scenarios.

---

## 📊 Portfolio Reports — Live on GitHub Pages

All analytical reports are published as standalone HTML pages with all charts embedded. View directly in any browser — no dependencies required.

| Report Section | Live URL |
|----------------|----------|
| Introduction | [Introduction.html](https://mehmood-khans.github.io/healthcare-analytics/Introduction.html) |
| Section A — Patient & Care Quality | [Section_A.html](https://mehmood-khans.github.io/healthcare-analytics/Section_A.html) |
| Section B — Operations & Capacity | [Section_B.html](https://mehmood-khans.github.io/healthcare-analytics/Section_B.html) |
| Section C — Financial & Revenue Cycle | [Section_C.html](https://mehmood-khans.github.io/healthcare-analytics/Section_C.html) |
| Section D — Risk, Safety & Compliance | [Section_D.html](https://mehmood-khans.github.io/healthcare-analytics/Section_D.html) |
| Section E — System Performance & Scalability | [Section_E.html](https://mehmood-khans.github.io/healthcare-analytics/Section_E.html) |
| Section F — Strategic Recommendations | [Section_F.html](https://mehmood-khans.github.io/healthcare-analytics/Section_F.html) |

**104 charts embedded across 6 analytical sections · $13.3B total opportunity identified**

---

## 📁 Project Structure

```
healthcare-analytics/
│
├── README.md                        # This file
├── Healthcare_Data_Analysis.ipynb   # Main notebook (36 exercises + capstone)
├── Introduction.html                # Portfolio intro & database architecture
├── Section_A.html                   # Patient & Care Quality (17 charts)
├── Section_B.html                   # Operations & Capacity (19 charts)
├── Section_C.html                   # Financial & Revenue Cycle (15 charts)
├── Section_D.html                   # Risk, Safety & Compliance (18 charts)
├── Section_E.html                   # System Performance & Scalability (35 charts)
├── Section_F.html                   # Strategic Recommendations
└── .gitignore                       # Excludes database and raw data files
```

---

## 📊 Dataset

| Property      | Detail                                                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------------------------ |
| Type          | Synthetic training data (no real patient records)                                                                  |
| Tables        | 17                                                                                                                 |
| Rows          | 7,078,107                                                                                                          |
| Database size | ~1.2 GB (SQLite)                                                                                                   |
| Source format | CSV files inside `Health_care.zip`                                                                                 |
| Kaggle link   | [moid1234/health-care-data-set-20-tables](https://www.kaggle.com/datasets/moid1234/health-care-data-set-20-tables) |

### Tables at a glance

| Table           | Description          | Approx. rows |
| --------------- | -------------------- | ------------ |
| `STG_EHP__PATN` | Patient demographics | 351,765      |
| `STG_EHP__VIST` | Visit records        | 917,331      |
| `STG_EHP__BILL` | Billing & payments   | 917,331      |
| `STG_EHP__APPT` | Appointments         | 974,032      |
| `STG_EHP__TRTM` | Treatments           | 917,191      |
| `STG_EHP__STFF` | Staff records        | 5,496        |
| `STG_EHP__DPMT` | Departments          | 30           |
| `STG_EHP__INSR` | Insurance policies   | 457,072      |
| `STG_EHP__MDCN` | Medications          | 346,302      |
| `STG_EHP__PTAL` | Patient allergies    | 644,303      |
| `STG_EHP__ALGY` | Allergy reference    | 44           |
| `STG_EHP__MEDT` | Medical teams        | 312,870      |
| `STG_EHP__ROMS` | Rooms                | 24,302       |
| `STG_EHP__EQPM` | Equipment            | 10,190       |
| `STG_EHP__MDBL` | Medical bills detail | 465,152      |
| `STG_EHP__SPLY` | Supply chain         | 721,134      |
| `STG_EHP__VNDR` | Vendors              | 13,562       |

---

## 🚀 Getting Started

### 1 · Clone the repo

```bash
git clone https://github.com/Mehmoodkhans/healthcare-analytics.git
cd healthcare-analytics
```

### 2 · Install dependencies

```bash
pip install pandas matplotlib seaborn numpy
```

### 3 · Download the dataset

The database (~1.2 GB) is not included in this repo. Download the dataset from Kaggle:

**[🔗 Healthcare Management System Dataset — Kaggle](https://www.kaggle.com/datasets/moid1234/health-care-data-set-20-tables)**

Extract the ZIP file to a folder on your machine, e.g. `~/healthcare_data/`.
The folder should contain 17 CSV files named `STG_EHP__*.csv`.

### 4 · Configure the path

Open the notebook and update **one line** in the **Configuration** cell:

```python
DATA_DIR = "/path/to/your/healthcare_data"
```

### 5 · Build the database (once)

Run the **Setup** cell. It will extract the CSVs and load them into `healthcare.db`.  
This takes **3–6 minutes** and only needs to be done once.

### 6 · Run any exercise

After setup, every exercise cell is independent — run them in any order.

---

## 📚 Exercise Index

### Phase 1 · SQL Fundamentals (Exercises 1–16)

| Exercise | Topic                        | SQL Concepts                        |
| -------- | ---------------------------- | ----------------------------------- |
| 1        | Blood type distribution      | GROUP BY, COUNT                     |
| 2        | Gender analysis              | Conditional aggregation             |
| 3        | Age & temporal coverage      | Date functions, BETWEEN             |
| 4        | Department location analysis | Basic JOIN, GROUP BY                |
| 5        | Equipment analysis           | Aggregation, HAVING                 |
| 6        | Supply chain overview        | Multi-table JOIN                    |
| 7–16     | Healthcare fundamentals      | SELECT, WHERE, ORDER BY, subqueries |

### Phase 2 · JOIN Techniques (Exercises 17–24)

| Exercise | Topic                  | SQL Concepts                 |
| -------- | ---------------------- | ---------------------------- |
| 17       | Department capacity    | CROSS JOIN                   |
| 18       | Salary equity          | SELF JOIN                    |
| 19       | Appointment–visit gaps | Outer JOIN + NULL detection  |
| 20       | Patient profiling      | Mixed JOIN types             |
| 21       | Query optimisation     | EXPLAIN QUERY PLAN, indexes  |
| 22       | Patient care pathway   | 5-table JOIN, GROUP_CONCAT   |
| 23       | 30-day readmissions    | SELF JOIN, CTE, julianday()  |
| 24       | Treatment outcomes     | Conditional aggregation, CTE |

### Phase 3 · Advanced SQL (Exercises 25–35)

| Exercise | Topic                     | SQL Concepts                           |
| -------- | ------------------------- | -------------------------------------- |
| 25       | Staff workload            | SELF JOIN, CTE, CASE WHEN              |
| 26       | Supply chain flow         | Window functions, correlated subqueries|
| 27       | Temporal JOINs            | Date-range JOIN, BETWEEN               |
| 28       | Cohort analysis           | ROW_NUMBER, LAG, PARTITION BY          |
| 29       | Revenue cycle             | NULLIF, bill status analysis           |
| 30       | Insurance claims          | EXISTS, temporal JOIN                  |
| 31       | Allergy cross-check       | Safety-critical JOIN, NOT EXISTS       |
| 32       | Advanced window functions | RANK, NTILE, LEAD/LAG, moving averages |
| 33       | Recursive CTEs            | Hierarchies, date series generation    |
| 34       | Complex subqueries        | Correlated, scalar, EXISTS             |
| 35       | Patient risk profiles     | Multi-dimensional scoring, risk tiers  |

### Phase 4 · Capstone (Exercise 36)

| Report                   | Description                                      |
| ------------------------ | ------------------------------------------------ |
| Executive Dashboard      | 30-day snapshot — volume, revenue, quality, risk |
| Patient Journey Analysis | Lifecycle stages, engagement, risk scoring       |
| Financial Deep-Dive      | Revenue trends, moving averages, value segments  |
| Strategic Recommendations| Care gaps, retention model, cost reduction plan  |

---

## 🛠️ Tech Stack

| Tool       | Version  | Purpose                         |
| ---------- | -------- | ------------------------------- |
| Python     | 3.10+    | Data processing & orchestration |
| SQLite     | built-in | Analytical database             |
| pandas     | 2.x      | DataFrames & result handling    |
| matplotlib | 3.x      | Visualisations                  |
| seaborn    | 0.x      | Statistical charts              |
| numpy      | 1.x      | Numerical operations            |

---

## 💡 Key Skills Demonstrated

- **SQL:** JOINs (INNER, LEFT, CROSS, SELF), CTEs, recursive CTEs, window functions, subqueries, performance optimisation
- **Healthcare analytics:** Revenue cycle, readmission analysis, risk stratification, allergy safety checks, cohort analysis
- **Python:** SQLite integration, pandas, matplotlib/seaborn visualisation, modular helper functions
- **Data engineering:** Bulk CSV loading with chunking, index creation, data integrity verification

---

## ⚠️ Important Notes

- The dataset is **entirely synthetic** — generated for training purposes only
- The `.db` file (~1.2 GB) and raw CSV/ZIP data are excluded from the repo via `.gitignore`
- Dataset source: [Healthcare Management System — Kaggle](https://www.kaggle.com/datasets/moid1234/health-care-data-set-20-tables)
- Each exercise cell re-declares `DB_PATH` and helper functions so it can run standalone

---

## 📄 License

This project is released for educational and portfolio use.  
The synthetic dataset is for training purposes only.
