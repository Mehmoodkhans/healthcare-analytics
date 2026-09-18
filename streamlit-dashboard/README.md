# Healthcare Analytics — Interactive Dashboard

A live, interactive companion to the full [Healthcare Analytics HTML reports](https://mehmoodkhans.github.io/healthcare-analytics/) — built with Streamlit, Plotly, and Matplotlib.

**Live app:** https://mehmoodkhans-healthcare.streamlit.app

This dashboard mirrors the structure of the main report (Introduction + Sections A–F), letting visitors explore the underlying data interactively instead of only reading static findings.

## What's in this folder

| File | Purpose |
|---|---|
| `streamlit_app.py` | The dashboard itself — reads the CSVs in `data/` and renders all charts across the 7 sections |
| `export_for_streamlit.py` | Run this once locally against the full `healthcare.db` (not included in this repo — see below) to generate the CSVs the dashboard needs |
| `requirements.txt` | Python dependencies for both the export script and the dashboard |
| `data/` | Small, pre-aggregated CSV files (a few KB–MB each) — the only data actually committed to GitHub. The full 840MB database never leaves a local machine |

## Why the data is pre-exported, not queried live

The full dataset (`healthcare.db`) is 7M+ rows / ~840MB — far too large for GitHub or Streamlit Community Cloud to host directly. Instead:

1. `export_for_streamlit.py` runs the real SQL queries once, locally, against the full database
2. It saves each result (already aggregated — counts, percentages, groupings) as a small CSV in `data/`
3. Only those small CSVs are committed to GitHub and read by the live dashboard

This keeps the deployed app fast and lightweight while still reflecting real, verified numbers from the full dataset.

## Running this yourself

```bash
pip install -r requirements.txt

# Edit DB_PATH at the top of export_for_streamlit.py to point at your own healthcare.db, then:
python export_for_streamlit.py

# Launch the dashboard locally:
streamlit run streamlit_app.py
```

## Relationship to the main project

This dashboard is a companion to, not a replacement for, the full written analysis. For the complete narrative — root-cause findings, ROI calculations, and strategic recommendations — see:

- [Full HTML reports](https://mehmoodkhans.github.io/healthcare-analytics/) (Introduction, Sections A–F)
- [Main project README](../README.md)
- [Source Jupyter notebook](../Healthcare_Data_Analysis.ipynb)
