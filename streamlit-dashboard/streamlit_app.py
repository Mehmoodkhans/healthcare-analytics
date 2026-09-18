"""
Healthcare Analytics — Interactive Streamlit Dashboard
Reads pre-aggregated CSVs from ./data (produced by export_for_streamlit.py)
so the app stays lightweight enough to run on Streamlit Community Cloud.

Color palette matches the source notebook (All_Final_new_visualization_cleaned.ipynb)
so charts here look consistent with the HTML report brand.
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from collections import defaultdict
import streamlit as st
from streamlit_option_menu import option_menu
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ── Exact palette from the source notebook's COLORS / HC dicts ─────────────
HC = {
    "blue": "#1565C0",
    "teal": "#33a7c8",
    "green": "#388E3C",
    "purple": "#a538c6",
    "orange": "#F57C00",
    "red": "#D32F2F",
    "light_purple": "#d29ce3",
    "grey": "#9E9E9E",
}
HC_SEQUENCE = [HC["blue"], HC["teal"], HC["green"], HC["purple"],
               HC["orange"], HC["red"], HC["light_purple"], HC["grey"]]

# Category-specific maps mirroring the notebook's PALETTE_STATUS / status_colours
STATUS_COLOR_MAP = {
    # Visit statuses (actual labels from this dataset)
    "Admitted": HC["blue"], "Discharged": HC["green"], "Scheduled": HC["teal"],
    "In Progress": HC["orange"], "No Show": HC["grey"],
    # Generic / other status vocab used elsewhere in the portfolio
    "Active": HC["green"], "Completed": HC["green"],
    "Hold": HC["orange"], "On Hold": HC["orange"], "Pending": HC["orange"],
    "Restrict": HC["blue"],
    "Discont": HC["red"], "Cancelled": HC["red"], "Denied": HC["red"], "Failed": HC["red"],
    "Inactive": HC["grey"], "Not Tolerated": HC["grey"], "Declined": HC["grey"],
}

st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
)

# ── Global sizing override ──────────────────────────────────────────────────
# Streamlit's default font/spacing scale looks tiny on large or high-resolution
# monitors because it doesn't auto-scale with screen size. This bumps the base
# font size, widens the usable content area, and enlarges tab labels/metrics
# app-wide. Tune the values below (all in rem/px) to taste.
st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-size: 17px;
        }
        /* Widen the content area (was capped at 1400px, causing a boxy/square
           look with large empty margins on wide monitors). Percentage-based
           side padding means every tab gets the same edge-to-edge width,
           regardless of how much content that tab has. */
        .block-container {
            max-width: 100%;
            padding-left: 4%;
            padding-right: 4%;
            padding-top: 2rem;
            padding-bottom: 1rem;
        }
        h1 { font-size: 2.4rem !important; }
        h2 { font-size: 1.9rem !important; }
        h3 { font-size: 1.75rem !important; }
        h4 { font-size: 1.4rem !important; }
        p, li, .stMarkdown { font-size: 1.15rem !important; line-height: 1.7 !important; }
        [data-testid="stMetricValue"] { font-size: 2.1rem !important; }
        [data-testid="stMetricLabel"] { font-size: 1.1rem !important; }
        [data-testid="stAlert"] p { font-size: 1.1rem !important; line-height: 1.6 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Apply the HC palette as the default Plotly template for every chart in this app
px.defaults.color_discrete_sequence = HC_SEQUENCE
px.defaults.template = "plotly_white"


@st.cache_data
def load_csv(name):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


MPL_AGE_COLORS = [HC["teal"], HC["blue"], HC["green"], HC["orange"], HC["red"]]

import re
import numpy as np


def fig_age_group_barh(
    df_dob,
    title="Patients by Age Group",
    title_fontsize=15,
    title_fontweight="bold",
    show_all_spines=False,
    xlabel="Number of\nPatients",        # fixed: was "Number of/n Patients" (literal slash-n, not a newline)
    xlabel_fontsize=13,
    xlabel_fontweight="bold",
    xlabel_pos=(-0.06, -0.01),          # (x, y) in axes-fraction coords via set_label_coords
    xtick_fontsize=12,
    ytick_fontsize=13,
    tick_fontweight="bold",
    xtick_start=20000,
    xtick_stop=80000,
    xtick_step=20000,
):
    """Exercise 3 — horizontal bar of patients by age group, notebook order/colors."""
    df = df_dob.copy()
    df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
    df["age"] = ((pd.Timestamp.now() - df["dob"]).dt.days / 365.25)
    df = df[(df["age"] >= 0) & (df["age"] <= 120)]

    def bucket(a):
        if a < 18: return "0-17 (Child)"
        if a < 35: return "18-34 (Young Adult)"
        if a < 50: return "35-49 (Adult)"
        if a < 65: return "50-64 (Middle Age)"
        return "65+ (Senior)"

    df["age_group"] = df["age"].apply(bucket)
    order = ["0-17 (Child)", "18-34 (Young Adult)", "35-49 (Adult)",
             "50-64 (Middle Age)", "65+ (Senior)"]
    counts = df["age_group"].value_counts().reindex(order, fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.patch.set_facecolor("white")
    ax.barh(counts.index, counts.values, color=MPL_AGE_COLORS,
            edgecolor="black", linewidth=1.2, alpha=0.9)
    for i, v in enumerate(counts.values):
        ax.text(v + max(counts.values) * 0.01, i, f"{v:,.0f}", va="center",fontsize= 13, fontweight="bold")

    # 1) Title
    ax.set_title(title, fontsize=title_fontsize, fontweight=title_fontweight)

    # 3) X label with manual position + font size
    ax.set_xlabel(xlabel, fontsize=xlabel_fontsize,fontstyle= 'italic', fontweight=xlabel_fontweight)
    ax.xaxis.set_label_coords(*xlabel_pos)

    ax.grid(axis="x", alpha=0.3)

    # spines
    if show_all_spines:
        for spine in ax.spines.values():
            spine.set_visible(True)
    else:
        ax.spines[["top", "right"]].set_visible(False)

    # 2) Y tick labels: split "0-17 (Child)" -> "0-17\nChild"
    new_labels = []
    for label in counts.index:
        m = re.match(r"(.+?)\s*\((.+)\)", label)
        if m:
            new_labels.append(f"{m.group(1)}\n{m.group(2)}")
        else:
            new_labels.append(label)
    ax.set_yticklabels(new_labels)

    # 4) Explicit x-ticks
    ax.set_xticks(np.arange(xtick_start, xtick_stop + 1, xtick_step))

    # tick font sizes / weight (applied after set_xticks so it sticks)
    ax.tick_params(axis="x", labelsize=xtick_fontsize)
    ax.tick_params(axis="y", labelsize=ytick_fontsize)
    for lbl in ax.get_xticklabels():
        lbl.set_fontweight(tick_fontweight)
    for lbl in ax.get_yticklabels():
        lbl.set_fontweight(tick_fontweight)

    fig.tight_layout()
    return fig, counts
# 

def fig_readmission_benchmark(
    df,
    title="30-day Readmission Rate vs National Benchmark",
    title_fontsize=15,
    title_fontweight="bold",
    show_all_spines=False,          # 2) True -> show all 4 spines, False -> keep top/right hidden
    ylabel="Readmission\nRate (%)",
    ylabel_rotation=0,
    ylabel_labelpad=40,             # x-offset-ish spacing for horizontal label
    ylabel_pos=(-0.02, 0.99),            # (x, y) position of the ylabel via set_label_coords
    xtick_fontsize=12,
    ytick_fontsize=12,
    tick_fontweight="bold",       # set "bold" if needed
):
    """Exercise 23 — 30-day readmission rate vs national benchmark, bar comparison."""
    rate = float(df["readmission_rate_pct"].iloc[0])
    labels = ["This Hospital", "National Low (15%)", "National High (20%)"]
    values = [rate, 15.0, 20.0]
    colors = [HC["green"] if rate < 15 else (HC["orange"] if rate < 20 else HC["red"]),
              HC["blue"], HC["red"]]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.patch.set_facecolor("white")
    bars = ax.bar(labels, values, color=colors, edgecolor="black", linewidth=1.2, width=0.6)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.4, f"{v:.2f}%",
                ha="center", fontweight="bold", fontsize=12)

    ax.axhline(rate, color=HC["teal"], linestyle="--", linewidth=2.5, alpha=0.7)

    # 1) Title
    ax.set_title(title, fontsize=title_fontsize, fontweight=title_fontweight)

    # 3) Y label with rotation + manual position
    ax.set_ylabel(ylabel, fontweight="bold",fontstyle = "italic", fontsize = 13, rotation=ylabel_rotation, labelpad=ylabel_labelpad)
    ax.yaxis.set_label_coords(*ylabel_pos)

    ax.set_ylim(0, max(values) * 1.25)

# remove the tick that sits exactly at the top of the y-axis
    ymax = ax.get_ylim()[1]
    yticks = ax.get_yticks()
    yticks = yticks[yticks < ymax]          # drop any tick at/above the ceiling
    ax.set_yticks(yticks)

    # 2) Spines
    if show_all_spines:
        for spine in ax.spines.values():
            spine.set_visible(True)
    else:
        ax.spines[["top", "right"]].set_visible(False)

    ax.grid(axis="y", alpha=0.3)

    # 4) Tick label font size / weight
    ax.tick_params(axis="x", labelsize=xtick_fontsize)
    ax.tick_params(axis="y", labelsize=ytick_fontsize)
    for label in ax.get_xticklabels():
        label.set_fontweight(tick_fontweight)
    for label in ax.get_yticklabels():
        label.set_fontweight(tick_fontweight)

    fig.tight_layout()
    return fig

def fig_department_locations(df):
    """Exercise 4 — Department distribution by Building/Floor, matches notebook's stacked-bar-with-boxes."""
    def parse_location(loc):
        parts = [p.strip() for p in str(loc).split(',')]
        parts += [''] * (3 - len(parts))  # pad so parts[1]/[2] always exist, even if malformed
        building = parts[0].replace('Building ', '') if parts[0] else 'Unknown'
        floor = '0' if 'Ground' in parts[1] else (parts[1].replace('Floor ', '').strip() or '0')
        wing = parts[2].replace('Wing ', '') if parts[2] else ''
        return building, floor, wing

    df = df.copy()
    parsed = df["location"].apply(lambda x: pd.Series(parse_location(x), index=["Building", "Floor", "Wing"]))
    df = pd.concat([df, parsed], axis=1)

    dept_by_location = defaultdict(list)
    for _, row in df.iterrows():
        dept_by_location[(row["Floor"], row["Building"])].append(row["department"])

    FLOOR_COLORS = {"0": HC["teal"], "1": HC["blue"], "2": HC["green"],
                     "3": HC["orange"], "4": HC["red"], "5": HC["purple"]}
    FLOOR_LABELS = {"0": "Ground", "1": "Floor 1", "2": "Floor 2",
                     "3": "Floor 3", "4": "Floor 4", "5": "Floor 5"}

    building_floor = df.groupby(["Building", "Floor"]).size().reset_index(name="Count")
    pivot_df = building_floor.pivot(index="Building", columns="Floor", values="Count").fillna(0)
    floor_order = ["0", "1", "2", "3", "4", "5"]
    pivot_df = pivot_df[[c for c in floor_order if c in pivot_df.columns]]
    bar_colors = [FLOOR_COLORS[f] for f in floor_order if f in pivot_df.columns]

    fig, ax = plt.subplots(figsize=(9.5, 7.23))
    fig.patch.set_facecolor("white")
    pivot_df.plot(kind="bar", stacked=True, ax=ax, width=0.8, color=bar_colors,
                  edgecolor="black", linewidth=1.5, legend=False)

    ax.set_xlabel("Building", fontsize=15, fontweight="bold", fontstyle="italic")
    ax.xaxis.set_label_coords(0.06, -0.01)   # (x, y) in axes-fraction coords — tune as needed
    present_floors = [f for f in floor_order if f in pivot_df.columns]
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=FLOOR_COLORS[f], edgecolor="black") for f in present_floors]
    ax.legend(handles, [FLOOR_LABELS[f] for f in present_floors], title="",
          bbox_to_anchor=(0.5, -0.04), loc="upper center", fontsize=13, title_fontsize=14,
          ncol=len(present_floors), frameon=True, edgecolor="#cccccc",
          handlelength=1, handleheight=1, handletextpad=0.5)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=13,fontweight="bold", )
    ax.set_ylabel("")
    ax.spines["left"].set_visible(False)
    ax.yaxis.set_ticklabels([])
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", alpha=0.3, linestyle="--", color="#888888")
    ax.set_axisbelow(True)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    for b_idx, building in enumerate(pivot_df.index):
        y_offset = 0
        for floor in floor_order:
            if floor in pivot_df.columns:
                count = int(pivot_df.loc[building, floor])
                if count > 0:
                    depts = dept_by_location.get((floor, building), [])
                    y_pos = y_offset + count / 2
                    dept_text = "\n".join(depts)
                    font_size = 8.0 if any(len(d) > 14 for d in depts) else 14
                    box_color = FLOOR_COLORS.get(floor, HC["grey"])
                    ax.text(b_idx, y_pos, dept_text, ha="center", va="center",
                            fontsize=font_size, fontweight="bold", color="white",
                            bbox=dict(boxstyle="round,pad=0.3", facecolor=box_color,
                                      alpha=0.75, edgecolor="white", linewidth=1.0))
                    y_offset += count

    ax.set_title("Department Distribution by Building and Floor", fontsize=20, fontweight="bold")
    fig.tight_layout()
    return fig


def fig_salary_equity_donut(df):
    """Exercise 18 — Salary equity donut with hollow-center 'Total Pairs' label, matches notebook's fig4."""
    order = ["Equitable", "Moderate", "Concern"]
    label_map = {"Equitable": "Equitable\n(<\\$5K diff)", "Moderate": "Moderate Gap\n(\\$5K\u2013\\$10K)",
                 "Concern": "Concern\n(>\\$10K)"}
    counts = {cat: 0 for cat in order}
    for _, row in df.iterrows():
        if row["gap_category"] in counts:
            counts[row["gap_category"]] = row["pair_count"]

    values = [counts[c] for c in order]
    labels = [label_map[c] for c in order]
    colors_pie = [HC["green"], HC["orange"], HC["red"]]

    fig, ax = plt.subplots(figsize=(5, 1.85))
    fig.patch.set_facecolor("white")
    ax.set_aspect("equal")
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.05, 1.30)

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors_pie,
        pctdistance=0.78, explode=[0.04, 0.04, 0.04],
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontweight("bold")
        at.set_fontsize(5.5)
    for text in texts:
        text.set_fontsize(6.5)
        text.set_fontweight("normal")

    total_pairs = sum(values)
    ax.text(0, 0.1, f"{total_pairs:,}", ha="center", va="center",
            fontsize=7, fontweight="bold", color="#333")
    ax.text(0, -0.18, "Total Pairs", ha="center", va="center", fontsize=7, color="#666")

    ax.set_title("Salary Equity Analysis", fontsize=7, fontweight="bold")
    ax.title.set_position((0.5, 1.01))
    #fig.tight_layout()
    fig.subplots_adjust(
    left=0.02,
    right=0.98,
    top=0.88,
    bottom=0.02
)
    return fig


BILL_STATUS_COLORS = {
    "Write-Off": HC["red"], "Insurance Denied": HC["purple"],
    "Pending Insurance Review": HC["teal"], "Insurance Covered 50%": HC["orange"],
    "Insurance Covered 80%": HC["blue"], "Insurance Covered 100%": HC["green"],
}

def fig_monthly_billing_stacked(
    df,
    quarterly_tick_labels=True,      # keep all monthly bars, only label every 3rd tick as a quarter
    ylabel="Total Billed ($)",
    ylabel_fontsize=14,
    ylabel_fontweight="bold",
    ylabel_rotation=0,
    ylabel_labelpad=55,
    ylabel_pos=(-0.02, 1.02),        # (x, y) in axes-fraction coords via set_label_coords
    ytick_fontsize=10,
    ytick_fontweight="bold",
    xtick_fontsize=12,
    xtick_fontweight="bold",
    xtick_rotation=0,
    legend_fontsize=12,
    legend_edgecolor="#cccccc",
):
    """Figure C-04 — Monthly Billing Volume by Status, stacked bar.
    Bars/stacking stay monthly; only the x-axis labels can be thinned to one per quarter."""
    pivot = df.pivot_table(index="year_month", columns="bill_status",
                            values="total_billed", aggfunc="sum", fill_value=0)
    pivot = pivot.sort_index()
    status_order = [s for s in BILL_STATUS_COLORS if s in pivot.columns]
    pivot = pivot[status_order + [c for c in pivot.columns if c not in status_order]]
    colors = [BILL_STATUS_COLORS.get(s, HC["light_purple"]) for s in pivot.columns]

    fig, ax = plt.subplots(figsize=(9.0, 6.2))
    fig.patch.set_facecolor("white")
    pivot.plot(kind="bar", stacked=True, ax=ax, color=colors,
               edgecolor="white", linewidth=0.5, width=0.75, legend=False)

    ax.set_xlabel("")

    # Y label: horizontal rotation + manual position
    ax.set_ylabel(ylabel, fontsize=ylabel_fontsize, fontweight=ylabel_fontweight,
                  rotation=ylabel_rotation, labelpad=ylabel_labelpad)
    ax.yaxis.set_label_coords(*ylabel_pos)

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M" if x >= 1e6 else f"${x:,.0f}"))

    # X tick labels: all monthly bars stay, but only every 3rd tick gets a
    # "Qtr N, YYYY" label — the rest are blanked out (bar itself is untouched).
    if quarterly_tick_labels:
        months = pd.to_datetime(pivot.index, format="%Y-%m")
        labels = []
        for m in months:
            if m.month in (1, 4, 7, 10):          # first month of each quarter
                q = (m.month - 1) // 3 + 1
                labels.append(f"Qtr {q},\n{m.year}")
            else:
                labels.append("")
    else:
        labels = list(pivot.index)

    ax.set_xticklabels(labels, rotation=xtick_rotation, ha="left",
                        fontsize=xtick_fontsize, fontweight=xtick_fontweight)

    # Y tick labels: size + bold
    ax.tick_params(axis="y", labelsize=ytick_fontsize)
    for lbl in ax.get_yticklabels():
        lbl.set_fontweight(ytick_fontweight)

    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    legend = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=legend_fontsize,
                        frameon=True, edgecolor=legend_edgecolor)
    legend.get_frame().set_linewidth(2.5)   # adjust thickness here
    
    ax.set_title("Monthly Billing Volume by Status", fontsize=18, fontweight="bold")
    fig.tight_layout()
    return fig
    
def fig_insurance_coverage_stacked(df):
    """Figure C-06 — Insurance Coverage by Visit Type, 100%-stacked bar with overall-coverage callout."""
    pivot = df.pivot_table(index="visit_type", columns="coverage_status",
                            values="visit_count", aggfunc="sum", fill_value=0)
    for col in ["Covered", "Uninsured"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot[["Covered", "Uninsured"]]

    totals = pivot.sum(axis=1)
    pct = pivot.div(totals, axis=0) * 100

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    fig.patch.set_facecolor("white")

    x_pos = range(len(pct.index))
    ax.bar(x_pos, pct["Covered"], color=HC["green"], width=0.5, label="Covered",
           edgecolor="white", linewidth=1)
    ax.bar(x_pos, pct["Uninsured"], bottom=pct["Covered"], color=HC["red"], width=0.5,
           label="Uninsured", edgecolor="white", linewidth=1)

    for i, vt in enumerate(pct.index):
        covered_pct = pct.loc[vt, "Covered"]
        uninsured_pct = pct.loc[vt, "Uninsured"]
        ax.text(i, covered_pct / 2, f"{covered_pct:.0f}%", ha="center", va="center",
                color="white", fontweight="bold", fontsize=12)
        ax.text(i, covered_pct + uninsured_pct / 2, f"{uninsured_pct:.0f}%", ha="center",
                va="center", color="white", fontweight="bold", fontsize=12)

    overall_covered = totals @ (pct["Covered"] / 100) / totals.sum() * 100
    ax.text(0.63, 0.70, f"Overall Coverage\n{overall_covered:.1f}%", transform=ax.transAxes,
            ha="right", va="top", fontsize=10, fontweight="bold", color="#1565C0",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#EEF4FF",
                      edgecolor=HC["blue"], linewidth=1.5))

    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(pct.index, fontsize=12, fontweight="bold")
    #ax.set_ylabel("Visit Share (%)", fontsize=12, fontweight="bold")

    # Y label with rotation + manual position
    ax.set_ylabel(
    "Visit Share (%)",
    fontsize=11,
    fontstyle= 'italic',    
    fontweight="bold",
    rotation=0,
    labelpad=40,          # spacing so a horizontal label doesn't overlap the axis
)
    ax.yaxis.set_label_coords(-0.05, 1.05)   # (x, y) in axes-fraction coords — tune as needed
    
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.spines[["top", "right"]].set_visible(False)

# Y tick label size + bold
    ax.tick_params(axis="y", labelsize=12)
    for lbl in ax.get_yticklabels():
        lbl.set_fontweight("bold")

# Legend frame: visible, black, manual thickness
    legend = ax.legend(loc="upper left", bbox_to_anchor=(0.36, 0.36), ncol=1, fontsize=11,
                        frameon=True, edgecolor="black")
    legend.get_frame().set_linewidth(1.5)   # adjust thickness here
    ax.set_title("Insurance Coverage by Visit Type", fontsize=14, fontweight="bold", pad=45)
    fig.tight_layout()
    return fig


VENDOR_STATUS_COLORS = {
    "ACTIVE": "#2E7D32", "PENDING": HC["light_purple"], "TERMINATED": HC["red"],
    "PROBATION": HC["orange"], "SUSPENDED": HC["purple"], "BLACKLISTED": "#8B0000",
    "INACTIVE": HC["grey"],
}


def fig_vendor_compliance_pie(df):
    """Figure D-05 — Vendor Compliance Status, top-50-vendor cohort (matches Ex 26's LIMIT 50)."""
    df = df.sort_values("vendor_count", ascending=False).reset_index(drop=True)
    colors = [VENDOR_STATUS_COLORS.get(str(s).upper(), HC["blue"]) for s in df["vendor_status"]]

    fig, ax = plt.subplots(figsize=(7.5, 1.27))
    fig.patch.set_facecolor("white")
    ax.set_aspect("auto")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)

    wedges, texts, autotexts = ax.pie(
    df["vendor_count"], labels=df["vendor_status"], autopct="%1.1f%%",
    colors=colors, startangle=90,
    pctdistance=0.80,   # default is 0.6 — higher pushes labels further out toward the edge
    wedgeprops=dict(edgecolor="white", linewidth=1.0),
    )
    for at in autotexts:
        at.set_fontweight("bold")
        at.set_fontsize(2.5)
        at.set_color("white")
    for text in texts:
        text.set_fontsize(3.0)
        text.set_fontweight("normal")

    total_vendors = int(df["vendor_count"].sum())
    ax.text(0.5, -0.12, f"Total Vendors: {total_vendors}", transform=ax.transAxes,
            ha="center", fontsize=3, fontweight="bold", color="#333",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#EEF4FF",
                      edgecolor=HC["blue"], linewidth=0.5))

    # ax.set_title("Vendor Compliance Status Distribution", fontsize=4.5, fontweight="bold")
    ax.set_title("Vendor Compliance Status Distribution", fontsize=4.5, fontweight="bold")
    ax.title.set_position((0.5, 1.10))
    fig.tight_layout()
    return fig


MEDICATION_STATUS_COLORS = {
    "RX": HC["teal"], "OTC": HC["green"], "HOLD": "#F2C230",
    "DISCONT": HC["orange"], "BLOCKED": HC["red"],
}
import numpy as np


def fig_medication_status_bar(
    df,
    xlabel="Number of\nMedications",
    xlabel_fontsize=14,
    xlabel_fontweight="bold",
    xlabel_pos=(-0.04, -0.01),          # (x, y) in axes-fraction coords via set_label_coords
    xtick_fontsize=13,
    xtick_fontweight="bold",
    xtick_start=1000,                   # explicit tick range: 1000, 2000, 3000, 4000
    xtick_stop=4000,
    xtick_step=1000,
    ytick_fontsize=12.5,
    ytick_fontweight="bold",
):
    """Medication Inventory Status — full-population GROUP BY on MSTAT_DES (medication status,
    distinct from TYPE_DES which is therapeutic drug class)."""
    df = df.sort_values("medication_count", ascending=True).reset_index(drop=True)
    colors = [MEDICATION_STATUS_COLORS.get(str(s).upper(), HC["blue"]) for s in df["status"]]

    fig, ax = plt.subplots(figsize=(8.75, 6.35))
    fig.patch.set_facecolor("white")
    bars = ax.barh(df["status"], df["medication_count"], color=colors,
                    edgecolor="black", linewidth=1.2)
    for bar, count, pct in zip(bars, df["medication_count"], df["pct"]):
        ax.text(bar.get_width() + max(df["medication_count"]) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{count:,} \n({pct}%)", va="center", fontweight="bold", fontsize=13)

    # X label with manual position
    ax.set_xlabel(xlabel, fontsize=xlabel_fontsize, fontweight=xlabel_fontweight)
    ax.xaxis.set_label_coords(*xlabel_pos)

    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=0.3)

    # X tick labels: explicit range (1000, 2000, 3000, 4000), size + bold
    ax.set_xticks(np.arange(xtick_start, xtick_stop + 1, xtick_step))
    ax.tick_params(axis="x", labelsize=xtick_fontsize)
    for lbl in ax.get_xticklabels():
        lbl.set_fontweight(xtick_fontweight)

    # Y tick labels: size + bold
    ax.tick_params(axis="y", labelsize=ytick_fontsize)
    for lbl in ax.get_yticklabels():
        lbl.set_fontweight(ytick_fontweight)

    ax.set_title("Medication Status\n(Items Expiring Within 12 Months)", fontsize=18, fontweight="bold")
    fig.tight_layout()
    return fig


TREATMENT_STATUS_COLORS = {
    "Completed": HC["green"], "Partially Completed": HC["orange"], "Planned": HC["blue"],
    "On Hold": HC["light_purple"], "Not Tolerated": HC["purple"], "Failed": HC["red"],
    "Declined": HC["teal"],
}
def fig_treatment_status_leadlag(
    df,
    ylabel="Number of\nTreatment Records",
    ylabel_fontsize=12,
    ylabel_fontweight="bold",
    ylabel_rotation=0,
    ylabel_labelpad=60,               # extra spacing since a horizontal label needs more room
    ylabel_pos=(-0.02, 1.01),         # (x, y) in axes-fraction coords via set_label_coords
    xtick_fontsize=11,
    xtick_fontweight="bold",
    xtick_rotation=0,
    wrap_two_word_labels=True,       # split two-word labels onto 2 lines when rotation=0
    ytick_fontsize=10,
    ytick_fontweight="bold",
    title="Treatment Status Distribution \n       (LEAD/LAG Analysis)",
    title_fontsize=15,
    title_fontweight="bold",
    title_pos=(0.75, 1.08),            # (x, y) in axes-fraction coords
):
    """Figure E-08 — Treatment Status Distribution via LEAD/LAG (Exercise 32, LIMIT 100)."""
    counts = df["treatment_status"].value_counts()
    order = [s for s in TREATMENT_STATUS_COLORS if s in counts.index]
    order += [s for s in counts.index if s not in order]
    counts = counts.reindex(order)
    colors = [TREATMENT_STATUS_COLORS.get(s, HC["grey"]) for s in counts.index]
    total = counts.sum()

    fig, ax = plt.subplots(figsize=(8, 5.92))
    fig.patch.set_facecolor("white")
    bars = ax.bar(counts.index, counts.values, color=colors, edgecolor="black", linewidth=1.2)
    for bar, v in zip(bars, counts.values):
        pct = v / total * 100
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(counts.values) * 0.001,
                f"{v}\n({pct:.0f}%)", ha="center", va="bottom", fontsize=11, fontweight="bold")

    if "next_treatment_date" in df.columns:
        gaps = (pd.to_datetime(df["next_treatment_date"]) - pd.to_datetime(df["treatment_date"])).dt.days.dropna()
        if len(gaps) > 0:
            avg_gap = gaps.mean()
            ax.text(0.98, 0.95, f"Avg days between\ntreatments: {avg_gap:.1f}", transform=ax.transAxes,
                    ha="right", va="top", fontsize=11, fontweight="bold", color="#1565C0",
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#EEF4FF",
                              edgecolor=HC["blue"], linewidth=1.2))

    # Y label: font size/weight + rotation + manual position
    ax.set_ylabel(ylabel, fontsize=ylabel_fontsize, fontweight=ylabel_fontweight,
                  rotation=ylabel_rotation, labelpad=ylabel_labelpad)
    ax.yaxis.set_label_coords(*ylabel_pos)

    # X tick labels: if rotation is 0 and a label has 2+ words, wrap onto multiple
    # lines instead of letting a long horizontal label run into its neighbors.
    labels = list(counts.index)
    if wrap_two_word_labels and xtick_rotation == 0:
        labels = [lbl.replace(" ", "\n") if " " in lbl else lbl for lbl in labels]
    ax.set_xticklabels(
        labels,
        rotation=xtick_rotation,
        ha="right" if xtick_rotation != 0 else "center",
        fontsize=xtick_fontsize,
        fontweight=xtick_fontweight,
    )

    # Y tick labels: size + weight
    ax.tick_params(axis="y", labelsize=ytick_fontsize)
    for lbl in ax.get_yticklabels():
        lbl.set_fontweight(ytick_fontweight)

    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    # Title: font size/weight + manual position
    ax.set_title(title, fontsize=title_fontsize, fontweight=title_fontweight)
    ax.title.set_position(title_pos)

    fig.tight_layout()
    return fig


FUNNEL_STATUS_COLORS = {
    "Discharged": HC["green"], "Need Follow-Up": HC["orange"], "Admitted": HC["blue"],
    "Cancelled": HC["red"], "Scheduled": HC["teal"], "Completed": HC["green"],
}

def fig_visit_chain_funnel(
    df,
    ylabel="Visit Count",
    ylabel_fontsize=12,
    ylabel_fontweight="bold",
    ylabel_rotation=0,
    ylabel_labelpad=45,
    ylabel_pos=(-0.05, 1.02),        # (x, y) in axes-fraction coords via set_label_coords
):
    """Figure E-11 — Recursive Visit Chain Funnel, Steps 1-5 (Exercise 33.2)."""
    pivot = df.pivot_table(index="visit_sequence", columns="visit_status",
                            values="visit_count", aggfunc="sum", fill_value=0)
    pivot = pivot.sort_index()
    steps = pivot.index.tolist()
    step_totals = pivot.sum(axis=1)

    fig, ax = plt.subplots(figsize=(8, 5.8))
    fig.patch.set_facecolor("white")
    x_pos = np.arange(len(steps))
    bottoms = np.zeros(len(steps))
    for status in pivot.columns:
        vals = pivot[status].values
        colour = FUNNEL_STATUS_COLORS.get(status, HC["light_purple"])
        ax.bar(x_pos, vals, bottom=bottoms, color=colour, label=status,
               width=0.6, edgecolor="white", linewidth=0.5)
        bottoms += vals

    for i, total in enumerate(step_totals.values):
        ax.text(i, total + max(step_totals.values) * 0.01, f"{int(total)}",
                ha="center", va="bottom", fontsize=10, fontweight="bold", color="#333")

    if len(steps) >= 2:
        s1, s2 = step_totals.iloc[0], step_totals.iloc[1]
        drop = (1 - s2 / s1) * 100 if s1 > 0 else 0
        ax.annotate(
            f"Drop-off step 1→2: {drop:.0f}%",
            xy=(0.98, 0.60), xycoords="axes fraction", fontsize=10, color="#333", ha="right",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=HC["red"], linewidth=1.5, alpha=0.9),
        )

    reached = step_totals.values
    ended_at = [reached[i] - (reached[i + 1] if i + 1 < len(reached) else 0) for i in range(len(reached))]
    chain_txt = " | ".join(f"{steps[i]}-visit: {int(c)} pts" for i, c in enumerate(ended_at) if c > 0)
    if chain_txt:
        ax.text(0.60, 0.96, chain_txt, transform=ax.transAxes, fontsize=8.5, color="#333",
                ha="center", va="bottom", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#EEF4FF",
                          edgecolor=HC["blue"], linewidth=1.2, alpha=0.92))

    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"Step {s}" for s in steps], fontsize=11, fontweight="bold")

    # Y label: rotation + manual position
    ax.set_ylabel(ylabel, fontsize=ylabel_fontsize, fontweight=ylabel_fontweight,
                  rotation=ylabel_rotation, labelpad=ylabel_labelpad)
    ax.yaxis.set_label_coords(*ylabel_pos)

    ax.spines[["top", "right"]].set_visible(False)
    legend = ax.legend(
    fontsize=10, title="Visit Status", title_fontsize=11, loc="upper right",
    bbox_to_anchor=(0.98, 0.9),      # (x, y) in axes-fraction coords — manual position
    framealpha=0.9, edgecolor="#cccccc", fancybox=True, frameon=True,
)
    legend.get_frame().set_linewidth(1.2)   # manual frame thickness
    ax.set_title("Recursive Visit Chain Funnel: Steps 1-5", fontsize=15, fontweight="bold", pad=25)
    fig.tight_layout()
    return fig

def fig_kpi_badge_row(
    items,
    figsize=(11, 8.4),
    circle_radius=0.46,              # bigger radius = bigger circle (was 0.4)
    circle_center=(0.5, 0.58),
    value_fontsize=21,               # was 15
    value_fontweight="bold",
    value_color="white",
    sub_fontsize=15,                 # was 8.5
    sub_fontweight="bold",
    sub_color="white",
    label_fontsize=18,               # was 10
    label_fontweight="bold",
    label_color="#1E293B",
    title="Data Foundation at a Glance",
    title_fontsize=20,               # was 14
    title_fontweight="bold",
    wspace=0.15,
    hspace=0.4,
    xlim=(0, 1),
    ylim=(0, 1.05),
    frame_edgecolor="#cccccc",
    frame_linewidth=3.5,
):
    """Section F recap — solid-color circular KPI badges, matching the HTML's badge-circle style.
    Arranged as a 2x2 grid, sized up for full-screen display."""
    fig, axes = plt.subplots(
        2, 2, figsize=figsize, gridspec_kw={"wspace": wspace, "hspace": hspace}
    )
    fig.patch.set_facecolor("white")
    axes = axes.flatten()

    for ax, item in zip(axes, items):
        circle = plt.Circle(circle_center, circle_radius, color=item["color"], ec="none", zorder=1)
        ax.add_patch(circle)
        ax.text(0.5, 0.62, item["value"], ha="center", va="center",
                fontsize=value_fontsize, fontweight=value_fontweight,
                color=value_color, zorder=2)
        ax.text(0.5, 0.44, item["sub"], ha="center", va="center",
                fontsize=sub_fontsize, fontweight=sub_fontweight,
                color=sub_color, zorder=2, linespacing=1.3)
        ax.text(0.5, 0.05, item["label"], ha="center", va="top",
                fontsize=label_fontsize, fontweight=label_fontweight,
                color=label_color, linespacing=1.3)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")

    for ax in axes[len(items):]:
        ax.axis("off")

    fig.suptitle(title, fontsize=title_fontsize, fontweight=title_fontweight, y=0.96)
    fig.tight_layout(rect=[0.03, 0.03, 0.97, 0.92])

    frame = plt.Rectangle(
        (0.015, 0.015), 0.97, 0.965, fill=False,
        edgecolor=frame_edgecolor, linewidth=frame_linewidth,
        transform=fig.transFigure, zorder=10,
    )
    fig.add_artist(frame)
    return fig


def fig_kpi_gauge_row(
    items,
    figsize=(11, 8.4),                 # bumped up from (7, 5.25) for full-screen display
    donut_radius=1.15,               # bigger radius = bigger circle
    donut_width=0.38,                # thickness of the donut ring
    pct_fontsize=20,                 # was 14
    pct_fontweight="bold",
    label_fontsize=18,               # was 9.5
    label_fontweight="bold",
    label_color="#1E293B",
    title="Key Findings Across Sections A–E",
    title_fontsize=20,               # was 14
    title_fontweight="bold",
    wspace=0.15,
    hspace=0.35,
    xlim=(-1.15, 1.15),              # tightened from (-1.3, 1.3) to shrink whitespace
    ylim=(-1.35, 1.15),              # tightened from (-1.6, 1.3)
    frame_edgecolor="#cccccc",
    frame_linewidth=3.5,
):
    """Section F recap — donut-gauge KPI badges for percentages, matching the HTML's mini-donut
    style. Arranged as a 2x2 grid, sized up for full-screen display."""
    fig, axes = plt.subplots(
        2, 2, figsize=figsize, gridspec_kw={"wspace": wspace, "hspace": hspace}
    )
    fig.patch.set_facecolor("white")
    axes = axes.flatten()

    for ax, item in zip(axes, items):
        pct = item["value"]
        ax.pie(
            [pct, max(0, 100 - pct)],
            colors=[item["color"], "#C2C2C4"],
            startangle=90,
            counterclock=False,
            radius=donut_radius,
            wedgeprops=dict(width=donut_width, edgecolor="white", linewidth=2),
        )
        ax.text(0, 0.08, f"{pct:.1f}%", ha="center", va="center",
                fontsize=pct_fontsize, fontweight=pct_fontweight)
        ax.text(0, -1.25, item["label"], ha="center", va="top",
                fontsize=label_fontsize, fontweight=label_fontweight,
                color=label_color, linespacing=1.3)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")

    for ax in axes[len(items):]:
        ax.axis("off")

    fig.suptitle(title, fontsize=title_fontsize, fontweight=title_fontweight, y=0.95)
    fig.tight_layout(rect=[0.03, 0.03, 0.97, 0.92])

    frame = plt.Rectangle(
        (0.015, 0.015), 0.97, 0.965, fill=False,
        edgecolor=frame_edgecolor, linewidth=frame_linewidth,
        transform=fig.transFigure, zorder=10,
    )
    fig.add_artist(frame)
    return fig


def metric_badge(label, value, color):
    """Banner/button-style metric badge for the top header row (Patients, Visits, etc.),
    visually consistent with the KPI highlight boxes used elsewhere in the dashboard."""
    st.markdown(
        f"""
        <div style='
            background:{color}15;
            border:1px solid {color}55;
            border-bottom:4px solid {color};
            border-radius:10px;
            padding:14px 10px;
            text-align:center;
        '>
            <div style='
                font-size:1rem;
                font-weight:700;
                color:#475569;
                text-transform:uppercase;
                letter-spacing:0.04em;
                margin-bottom:6px;
            '>{label}</div>
            <div style='font-size:1.55rem;font-weight:800;color:{color};'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def missing_data_notice(name):
    st.info(
        f"`{name}.csv` not found in the data folder yet. "
        f"Run `export_for_streamlit.py` locally and commit the `data/` folder to see this chart."
    )


def kpi_highlight_box(
    value,
    label,
    color,
    value_fontsize=34,
    label_fontsize=17,
    padding="30px 22px",
    min_height=155,
    border_width=5,
    border_radius=8,
    bg_alpha_hex="22",   # appended to the hex color for a translucent background
    gap=8,               # spacing between the big number and the label
):
    """Render a colored highlight box (used on the Introduction tab) with readable,
    tunable font sizes and a fixed minimum height so it doesn't flatten into a thin
    strip on wide screens."""
    st.markdown(
        f"""
        <div style='
            background:{color}{bg_alpha_hex};
            border-left:{border_width}px solid {color};
            border-radius:{border_radius}px;
            padding:{padding};
            min-height:{min_height}px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            gap:{gap}px;
        '>
            <div style='font-size:{value_fontsize}pt;font-weight:800;line-height:1.1;color:{color};'>
                {value}
            </div>
            <div style='font-size:{label_fontsize}pt;color:#1E293B;line-height:1.3;'>
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# ── Header ─────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;font-size:2.9rem;margin-bottom:0.3rem;'>"
    "🏥 Healthcare Data Analysis Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style='text-align:center;font-size:1.05rem;color:#475569;margin-bottom:1.2rem;'>
        Synthetic dataset · 17 tables · 7M+ rows · Built with SQLite + Python + Streamlit —
        <a href='https://github.com/Mehmoodkhans/healthcare-analytics'
           style='color:#1D4ED8;font-weight:600;text-decoration:underline;'>
           View the full SQL notebook &amp; report on GitHub</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Executive KPIs ────────────────────────────────────────────────────────
kpis = load_csv("executive_kpis")
if kpis is not None and len(kpis) > 0:
    row = kpis.iloc[0]
    c1, c2, c3, c4, c5, c6 = st.columns(6, gap="small")
    with c1:
        metric_badge("Patients", f"{row['total_patients']:,.0f}", HC["blue"])
    with c2:
        metric_badge("Visits", f"{row['total_visits']:,.0f}", HC["teal"])
    with c3:
        metric_badge("Appointments", f"{row['total_appointments']:,.0f}", HC["green"])
    with c4:
        metric_badge("Active Staff", f"{row['active_staff']:,.0f}", HC["orange"])
    with c5:
        metric_badge("Departments", f"{row['total_departments']:,.0f}", HC["purple"])
    with c6:
        metric_badge("Total Revenue", f"${row['total_revenue'] / 1_000_000_000:.3f}B", HC["red"])
else:
    missing_data_notice("executive_kpis")

st.divider()

selected = option_menu(
    menu_title=None,
    options=["Introduction", "Section A", "Section B", "Section C",
             "Section D", "Section E", "Section F"],
    icons=["file-earmark-text", "people", "building", "cash-coin",
           "exclamation-triangle", "gear", "bullseye"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0", "background-color": "#ffffff", "width": "100%"},
        "nav": {"width": "100%", "display": "flex", "gap": "20px"},
        "nav-item": {"flex": "1", "display": "flex"},
        "icon": {"font-size": "1.1rem"},
        "nav-link": {
            "display": "flex",              # keeps icon + label on one row, never stacked
            "align-items": "center",
            "justify-content": "center",
            "gap": "8px",
            "white-space": "nowrap",         # prevents "Introduction" from wrapping
            "width": "100%",
            "flex-grow": "1",
            "font-size": "1.15rem",
            "font-weight": "800",
            "text-align": "center",
            "padding": "16px 8px",
            "margin": "0",
            "border-radius": "10px",
            "background-color": "#b3c9df",
            "border": "2.5px solid #5384b5",     # thicker, darker outline for a stronger button feel
            "box-shadow": "0 1px 3px rgba(0,0,0,0.06)",
            "color": "#334155",
            "transition": "all 0.15s ease-in-out",
        },
        "nav-link-selected": {
            "background-color": "#1D4ED8",
            "color": "#ffffff",
            "border": "2.5px solid #1D4ED8",
            "box-shadow": "0 2px 6px rgba(29,78,216,0.35)",
        },
    },
)

# ── Introduction ─────────────────────────────────────────────────────────
if selected == "Introduction":
    st.markdown("### A Comprehensive SQL + Python Analytics Project")
    st.markdown(
        "Built on a synthetic healthcare dataset of **17 tables and 7,078,107 rows**, this project "
        "progresses from foundational SQL through advanced techniques — window functions, recursive "
        "CTEs, and multi-dimensional risk scoring — all applied to realistic healthcare scenarios."
    )

    st.markdown("#### Portfolio at a Glance")
    b1, b2, b3 = st.columns(3, gap="large")
    with b1:
        kpi_highlight_box("$13.3B", "Strategic opportunity identified", HC["blue"])
    with b2:
        kpi_highlight_box("36", "SQL exercises completed", HC["teal"])
    with b3:
        kpi_highlight_box("6", "Analytical report sections", HC["purple"])

    st.markdown("")
    st.markdown("#### The Story Arc")
    st.markdown(
        "- **Section A — Patient & Care Quality**: who the patients are and how care quality varies\n"
        "- **Section B — Operations & Capacity**: how efficiently the hospital runs day to day\n"
        "- **Section C — Financial & Revenue Cycle**: where revenue is at risk and why\n"
        "- **Section D — Risk, Safety & Compliance**: what threatens patients and the organization\n"
        "- **Section E — System Performance & Scalability**: whether the data foundation itself holds up\n"
        "- **Section F — Strategic Recommendations**: what to do about all of the above"
    )

    st.markdown(
        """
        <div style='
            background:#EFF6FF;
            border-left:5px solid #3B82F6;
            border-radius:8px;
            padding:16px 20px;
            font-size:1.1rem;
            line-height:1.6;
            color:#0F172A;
        '>
            Each tab above mirrors the matching section of the full HTML report — this dashboard
            lets you explore the same findings interactively.
            <a href='https://mehmoodkhans.github.io/healthcare-analytics/'
               style='color:#1D4ED8;font-weight:600;text-decoration:underline;'>
               Read the full written reports on GitHub</a>.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Section A: Patient & Care Quality ────────────────────────────────────
if selected == "Section A":
    st.markdown(
        "<div style='font-size:1.15rem;font-weight:700;color:#1E293B;margin-bottom:0.15rem;'>"
        "👥 Patient &amp; Care Quality</div>",
        unsafe_allow_html=True,
    )
    st.caption("Mirrors HTML Section A")
    col1, col2 = st.columns(2)

    with col1:
        df = load_csv("patient_dob_raw")
        if df is not None:
            fig, counts = fig_age_group_barh(df)
            st.pyplot(fig, use_container_width=True)
            st.caption("Balanced across all 5 groups — corrects the earlier 85.5%-elderly miscalculation.")
        else:
            missing_data_notice("patient_dob_raw")

    with col2:
        df = load_csv("readmission_rate_benchmark")
        if df is not None:
            fig = fig_readmission_benchmark(df)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Top 10–15% of hospitals nationally. Strongest clinical quality proof point "
                "in the portfolio."
            )
        else:
            missing_data_notice("readmission_rate_benchmark")

# ── Section B: Operations & Capacity ─────────────────────────────────────
if selected == "Section B":
    st.markdown(
        "<div style='font-size:1.15rem;font-weight:700;color:#1E293B;margin-bottom:0.15rem;'>"
        "🏢 Operations &amp; Capacity</div>",
        unsafe_allow_html=True,
    )
    st.caption("Mirrors HTML Section B")
    col1, col2 = st.columns(2)

    with col1:
        df = load_csv("department_locations")
        if df is not None:
            fig = fig_department_locations(df)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Stacked bar showing the number of departments per building broken down by floor "
                "level. Reveals concentration of clinical services and identifies adjacency "
                "optimization opportunities. Base: 30 departments, 4 buildings, 21 locations."
            )
        else:
            missing_data_notice("department_locations")

    with col2:
        df = load_csv("salary_equity_summary")
        if df is not None:
            fig = fig_salary_equity_donut(df)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Chart examining salary equity across demographic or role groupings — identifies "
                "pay gaps and equity concerns requiring HR attention. Base: All active staff."
            )
        else:
            missing_data_notice("salary_equity_summary")

# ── Section C: Financial & Revenue Cycle ─────────────────────────────────
if selected == "Section C":
    st.markdown(
        "<div style='font-size:1.15rem;font-weight:700;color:#1E293B;margin-bottom:0.15rem;'>"
        "💰 Financial &amp; Revenue Cycle</div>",
        unsafe_allow_html=True,
    )
    st.caption("Mirrors HTML Section C")
    col1, col2 = st.columns(2)

    with col1:
        df = load_csv("insurance_coverage_by_visit_type")
        if df is not None:
            fig = fig_insurance_coverage_stacked(df)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Stacked bar chart showing the proportion of insured vs. uninsured visits "
                "broken down by visit type. Identifies which visit pathways have the worst "
                "verification rates and therefore the highest revenue exposure per episode."
            )
        else:
            missing_data_notice("insurance_coverage_by_visit_type")

    with col2:
        df = load_csv("monthly_billing_by_status")
        if df is not None:
            fig = fig_monthly_billing_stacked(df)
            st.pyplot(fig, use_container_width=True)
            st.caption("Stacked bar showing monthly billing volume by status.")
        else:
            missing_data_notice("monthly_billing_by_status")

# ── Section D: Risk, Safety & Compliance ─────────────────────────────────
if selected == "Section D":
    st.markdown(
        "<div style='font-size:1.15rem;font-weight:700;color:#1E293B;margin-bottom:0.15rem;'>"
        "⚠️ Risk, Safety &amp; Compliance</div>",
        unsafe_allow_html=True,
    )
    st.caption("Mirrors HTML Section D")
    col1, col2 = st.columns(2)

    with col1:
        df = load_csv("vendor_compliance_top50")
        if df is not None:
            fig = fig_vendor_compliance_pie(df)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Pie chart showing the top 50 vendors (by supply volume, ≥10 supplies each) "
                "by compliance status. Highlights concentration of problematic statuses among "
                "the most active vendors."
            )
        else:
            missing_data_notice("vendor_compliance_top50")

    with col2:
        df = load_csv("medication_status_full")
        if df is not None and len(df) > 0:
            fig = fig_medication_status_bar(df)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Horizontal bar chart showing medication status for items expiring within the "
                "next 12 months — the near-term action window, not the full inventory."
            )
        elif df is not None:
            st.info(
                "`medication_status_full.csv` loaded but contains 0 rows — no medications "
                "currently fall within this expiry window in your database."
            )
        else:
            missing_data_notice("medication_status_full")

# ── Section E: System Performance & Scalability ──────────────────────────
if selected == "Section E":
    st.markdown(
        "<div style='font-size:1.15rem;font-weight:700;color:#1E293B;margin-bottom:0.15rem;'>"
        "⚙️ System Performance &amp; Scalability</div>",
        unsafe_allow_html=True,
    )
    st.caption("Mirrors HTML Section E")
    col1, col2 = st.columns(2)

    with col1:
        df = load_csv("treatment_status_leadlag")
        if df is not None and len(df) > 0:
            fig = fig_treatment_status_leadlag(df)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Bar chart showing 100 treatment records by status. The LEAD/LAG technique "
                "identifies each patient's treatment sequence, enabling care coordinators to "
                "flag patients whose next treatment is overdue."
            )
        elif df is not None:
            st.info("`treatment_status_leadlag.csv` loaded but contains 0 rows.")
        else:
            missing_data_notice("treatment_status_leadlag")

    with col2:
        df = load_csv("visit_chain_funnel")
        if df is not None and len(df) > 0 and df["visit_sequence"].nunique() > 1:
            fig = fig_visit_chain_funnel(df)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Stacked bar funnel showing patient count at each visit chain step. Each bar is "
                "segmented by visit status."
            )
        elif df is not None:
            st.info(
                "`visit_chain_funnel.csv` only shows a single step in your data — re-run "
                "export_for_streamlit.py and confirm the row count before trusting this chart."
            )
        else:
            missing_data_notice("visit_chain_funnel")

# ── Section F: Strategic Recommendations ─────────────────────────────────
if selected == "Section F":
    st.markdown(
        "<div style='font-size:1.15rem;font-weight:700;color:#1E293B;margin-bottom:0.15rem;'>"
        "🎯 Strategic Recommendations</div>",
        unsafe_allow_html=True,
    )
    st.caption("Recap of verified findings from Sections A–E")

    col1, col2 = st.columns(2, gap="large")
    findings = []

    with col1:
        kpis = load_csv("executive_kpis")
        bills = load_csv("revenue_by_bill_status")
        if kpis is not None and len(kpis) > 0 and bills is not None:
            row = kpis.iloc[0]
            badge_items = [
                {"value": f"{row['total_patients']:,.0f}", "sub": "PATIENTS", "color": HC["blue"],
                 "label": "Core patient\npopulation"},
                {"value": f"{row['total_visits']:,.0f}", "sub": "VISITS", "color": HC["teal"],
                 "label": "Total recorded\nvisits"},
                {"value": f"{row['total_appointments']:,.0f}", "sub": "APPTS", "color": HC["green"],
                 "label": "Scheduled\nappointments"},
                {"value": f"{bills['bill_count'].sum():,.0f}", "sub": "BILLS", "color": HC["purple"],
                 "label": "Billing records\ngenerated"},
            ]
            fig = fig_kpi_badge_row(badge_items)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "This portfolio spans 17 tables and 7M+ rows across the full patient journey. "
                "Every number above is the same record count shown in the KPI bar at the top "
                "of this dashboard, reused here rather than recomputed."
            )
        else:
            missing_data_notice("executive_kpis")

    with col2:
        readm = load_csv("readmission_rate_benchmark")
        if readm is not None and len(readm) > 0:
            findings.append({
                "label": "30-Day Readmission\nRate (Sec. A)",
                "value": float(readm["readmission_rate_pct"].iloc[0]),
                "color": HC["green"],
            })

        salary = load_csv("salary_equity_summary")
        if salary is not None and len(salary) > 0:
            concern = salary.loc[salary["gap_category"] == "Concern", "pair_count"].sum()
            total = salary["pair_count"].sum()
            if total > 0:
                findings.append({
                    "label": "Salary Gaps >$10K\n(Sec. B)",
                    "value": concern / total * 100,
                    "color": HC["red"],
                })

        coverage = load_csv("insurance_coverage_by_visit_type")
        if coverage is not None and len(coverage) > 0:
            piv = coverage.pivot_table(index="visit_type", columns="coverage_status",
                                        values="visit_count", aggfunc="sum", fill_value=0)
            if "Covered" in piv.columns:
                covered_total = piv["Covered"].sum()
                grand_total = piv.values.sum()
                if grand_total > 0:
                    findings.append({
                        "label": "Insurance Coverage\n(Sec. C)",
                        "value": covered_total / grand_total * 100,
                        "color": HC["blue"],
                    })

        vendors = load_csv("vendor_compliance_top50")
        if vendors is not None and len(vendors) > 0:
            at_risk_statuses = {"SUSPENDED", "BLACKLISTED", "TERMINATED"}
            at_risk = vendors[vendors["vendor_status"].str.upper().isin(at_risk_statuses)]["vendor_count"].sum()
            total_v = vendors["vendor_count"].sum()
            if total_v > 0:
                findings.append({
                    "label": "At-Risk Vendors\n(Sec. D)",
                    "value": at_risk / total_v * 100,
                    "color": HC["orange"],
                })

        if findings:
            fig = fig_kpi_gauge_row(findings)
            st.pyplot(fig, use_container_width=True)
            st.caption(
                "Clinical quality (Sec. A) is the strongest result; compensation equity (Sec. B) "
                "is the clearest risk. Insurance verification (Sec. C) and vendor governance "
                "(Sec. D) sit in between. Each gauge is recomputed with the exact same data and "
                "logic as its original chart."
            )
        else:
            st.info("Underlying section CSVs not yet available — run export_for_streamlit.py first.")

st.markdown(
    """
    <hr style='margin-top:1rem;margin-bottom:0.6rem;border:none;border-top:1px solid #E5E7EB;'>
    <div style='font-size:1.05rem;color:#475569;'>
        Built as a comprehensive SQL + Python analytics project · All data is synthetic, used solely for demonstration purposes.
    </div>
    """,
    unsafe_allow_html=True,
)
