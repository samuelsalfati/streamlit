import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 1) Use a recognized built-in Matplotlib style
#    (e.g., "ggplot", "seaborn-whitegrid", "fivethirtyeight", etc.)
plt.style.use("seaborn-v0_8-whitegrid")

st.title("Clinician Simple RPM Model (Modern Chart)")

# ---------------------
# 1) User Inputs
# ---------------------
st.sidebar.header("Clinician & Billing Inputs")

# Hourly wage (~$24 if annual salary is ~$50k, 40 hrs/week)
clinician_hourly_wage = st.sidebar.number_input(
    "Clinician Hourly Wage ($)",
    min_value=10.0,
    max_value=50.0,
    value=24.04,
    step=1.0
)

# How many patients can the clinician handle in 1 hour?
patients_per_hour = st.sidebar.slider(
    "Patients per Hour",
    min_value=1,
    max_value=10,
    value=3
)

# Recurring codes
recurring_codes = {
    "99454": 45.12,
    "99457": 46.85,
    "99458": 37.62,
    "99490": 59.90,
    "99491 (1 of 20)": 80.98 / 20,  # approximate 1 in 20
    "99091": 51.29
}

# Non-recurring codes
non_recurring_codes = {
    "99453": 18.95,
    "99495": 230.00
}

# Toggle: Include Non-Recurring codes in every hour?
# (In reality, these might be once per new patient, but for demonstration we keep it simple.)
include_non_recurring = st.sidebar.checkbox(
    "Include Non-Recurring Codes for Each Patient/Hour?",
    value=False
)

# ---------------------
# 2) Simple Calculation
# ---------------------
recurring_revenue_per_patient = sum(recurring_codes.values())
non_recurring_revenue_per_patient = sum(non_recurring_codes.values()) if include_non_recurring else 0.0

revenue_per_patient = recurring_revenue_per_patient + non_recurring_revenue_per_patient
revenue_per_hour = patients_per_hour * revenue_per_patient
cost_per_hour = clinician_hourly_wage
ebitda_per_hour = revenue_per_hour - cost_per_hour

# ---------------------
# 3) Display Results
# ---------------------
st.subheader("Hourly Economics")

col1, col2, col3 = st.columns(3)
col1.metric("Revenue/Hour", f"${revenue_per_hour:,.2f}")
col2.metric("Cost/Hour (Clinician)", f"${cost_per_hour:,.2f}")
col3.metric("EBITDA/Hour", f"${ebitda_per_hour:,.2f}")

st.write("---")

st.write("### Breakdown of Codes Used")
st.write("**Recurring Codes:**")
for code_name, val in recurring_codes.items():
    st.write(f"- {code_name}: ${val:.2f}")

if include_non_recurring:
    st.write("**Non-Recurring Codes:**")
    for code_name, val in non_recurring_codes.items():
        st.write(f"- {code_name}: ${val:.2f}")
else:
    st.write("*Non-recurring codes are not included in this calculation.*")

# ---------------------
# 4) Visualization
# ---------------------
labels = ["Revenue/Hour", "Cost/Hour", "EBITDA/Hour"]
values = [revenue_per_hour, cost_per_hour, ebitda_per_hour]

fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

# Custom colors
colors = ["#5DADE2", "#F1948A", "#58D68D"]  # Blue, Red-Pink, Green

bars = ax.bar(labels, values, color=colors, edgecolor="black", zorder=2)

ax.set_ylabel("USD ($)", fontsize=12)
ax.set_title("Clinician Hourly Economics (RPM)", fontsize=14, weight="bold")

# Annotate bar values
for bar in bars:
    height = bar.get_height()
    ax.annotate(
        f"${height:,.2f}",
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

# Remove top/right spines for a cleaner look
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Add dashed horizontal grid
ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)

st.pyplot(fig)
