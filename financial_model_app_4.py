import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 1) Use a recognized built-in Matplotlib style
plt.style.use("seaborn-v0_8-whitegrid")

st.title("Clinician Simple RPM Model with GPCI Adjustment")

# -------------------------------------
# 1) SIDEBAR: BASIC CONFIGURATION
# -------------------------------------
st.sidebar.header("Staffing & Patients")

clinicians_per_hour = st.sidebar.slider(
    "Number of Clinicians", min_value=1, max_value=50, value=10, step=1
)

patients_per_clinician_per_hour = st.sidebar.slider(
    "Patients per Clinician per Hour", min_value=1, max_value=20, value=2, step=1
)

clinician_hourly_wage = st.sidebar.number_input(
    "Clinician Hourly Wage ($)", min_value=10.0, max_value=120.0, value=24.04, step=1.0
)

use_nurse = st.sidebar.checkbox("Use Nurse(s)?", value=True)
nurse_hourly_wage = 0.0
NURSE_PER_X_PATIENTS = 100

if use_nurse:
    nurse_hourly_wage = st.sidebar.number_input(
        "Nurse Hourly Wage ($)", min_value=10.0, max_value=120.0, value=36.06, step=1.0
    )

use_doctor = st.sidebar.checkbox("Use Doctor(s)?", value=True)
doctor_hourly_wage = 0.0
DOCTOR_PER_X_NURSES = 100

if use_doctor:
    doctor_hourly_wage = st.sidebar.number_input(
        "Doctor Hourly Wage ($)", min_value=10.0, max_value=120.0, value=60.0, step=1.0
    )

# -------------------------------------
# 2) GPCI ADJUSTMENT
# -------------------------------------
st.sidebar.header("GPCI Adjustment")

gpci_adjustments = {
    "Virginia": 1.0,
    "Florida": 1.05,
    "Texas": 1.03,
    "New York": 1.08,
    "California": 1.1,
}

selected_state = st.sidebar.selectbox("Select State for GPCI Adjustment", gpci_adjustments.keys())
gpci = gpci_adjustments[selected_state]

# -------------------------------------
# 3) BILLING CODES (RECURRING ONLY)
# -------------------------------------
st.sidebar.header("Recurring Billing Codes")

recurring_codes = {
    "99454 - RPM Device Supply": 45.12 * gpci,
    "99457 - RPM Mgmt (20 mins)": 46.85 * gpci,
    "99458 - RPM Mgmt (add’l 20)": 37.62 * gpci,
    "99490 - CCM by Clin Staff": 59.90 * gpci,
    "99491 - CCM by Physician (1/20)": (80.98 / 20) * gpci,
    "99091 - Data Interpretation": 51.29 * gpci,
}

enabled_codes = {}
for code_name, code_value in recurring_codes.items():
    checked = st.sidebar.checkbox(code_name, value=True)
    if checked:
        enabled_codes[code_name] = code_value

sum_of_selected_codes = sum(enabled_codes.values())

# -------------------------------------
# 4) REVENUE AND COST CALCULATIONS
# -------------------------------------
revenue_per_clinician_hour = sum_of_selected_codes * patients_per_clinician_per_hour
total_revenue_per_hour = revenue_per_clinician_hour * clinicians_per_hour
clinician_cost_per_hour = clinicians_per_hour * clinician_hourly_wage

# Calculate nurse costs as a fraction based on patient load
num_patients_per_hour = clinicians_per_hour * patients_per_clinician_per_hour
num_nurses = num_patients_per_hour / NURSE_PER_X_PATIENTS if use_nurse else 0
nurse_cost_per_hour = num_nurses * nurse_hourly_wage

# Calculate doctor costs as a fraction based on nurse load
num_doctors = num_nurses / DOCTOR_PER_X_NURSES if use_doctor else 0
doctor_cost_per_hour = num_doctors * doctor_hourly_wage

total_cost_per_hour = clinician_cost_per_hour + nurse_cost_per_hour + doctor_cost_per_hour
ebitda_per_hour = total_revenue_per_hour - total_cost_per_hour

# -------------------------------------
# 5) MAIN DASHBOARD DISPLAY
# -------------------------------------
st.subheader(f"Hourly Economics for {selected_state} (GPCI: {gpci})")

col1, col2, col3 = st.columns(3)
col1.metric("Revenue/Hour", f"${total_revenue_per_hour:,.2f}")
col2.metric("Cost/Hour", f"${total_cost_per_hour:,.2f}")
col3.metric("EBITDA/Hour", f"${ebitda_per_hour:,.2f}")

# -------------------------------------
# 6) BAR CHART
# -------------------------------------
labels = ["Revenue", "Clinician Cost", "Nurse Cost", "Doctor Cost", "EBITDA"]
values = [
    total_revenue_per_hour,
    clinician_cost_per_hour,
    nurse_cost_per_hour,
    doctor_cost_per_hour,
    ebitda_per_hour,
]
colors = ["#5DADE2", "#F1948A", "#F7DC6F", "#58D68D", "#76D7C4"]

fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

# Create individual bars for each value
bars = ax.bar(labels, values, color=colors, edgecolor="black", zorder=2)

# Formatting
ax.set_title(f"Hourly Economics for {selected_state} (GPCI: {gpci})", fontsize=14, weight="bold")
ax.set_ylabel("USD ($)")
ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)

for bar in bars:
    height = bar.get_height()
    if height > 0:
        ax.annotate(
            f"${height:,.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha='center',
            va='bottom',
            fontsize=10,
            fontweight='bold'
        )

st.pyplot(fig)

# -------------------------------------
# 7) INTERPRETATION TEXT
# -------------------------------------
st.write("""
This tool models **clinician staffing and revenue generation** for Remote Patient Monitoring (RPM). 
It leverages recurring billing codes, GPCI adjustments, and customizable staffing parameters 
to provide a detailed overview of revenue, costs, and EBITDA on an hourly basis. 

Use the inputs in the sidebar to experiment with different scenarios and visualize their financial outcomes.
""")

# Interpretation Text
interpretation_text = f"""
### Financial Insights

#### State-Specific Metrics
In **{selected_state}**, the **Geographic Practice Cost Index (GPCI)** adjustment is **{gpci:.2f}**.  
You have selected a workload of **{patients_per_clinician_per_hour} patients per clinician per hour**.

---

#### Hourly Revenue Per Clinician
To calculate the hourly revenue per clinician, we multiply the sum of selected recurring billing codes by the patients served per hour:

Hourly Revenue = Sum of Billing Codes × Patients Per Hour

Using your inputs:
- Sum of Billing Codes = {sum_of_selected_codes:,.2f}
- Patients Per Hour = {patients_per_clinician_per_hour}

Hourly Revenue Per Clinician = {revenue_per_clinician_hour:,.2f}

---

#### Cost Breakdown
- **Clinician Hourly Wage**: ${clinician_hourly_wage:,.2f}/hour
- **Nurse Hourly Wage**: ${nurse_hourly_wage:,.2f}/hour
- **Doctor Hourly Wage**: ${doctor_hourly_wage:,.2f}/hour

Based on your input:
- **Clinician Cost**: ${clinician_cost_per_hour:,.2f}
- **Nurse Cost**: ${nurse_cost_per_hour:,.2f}
- **Doctor Cost**: ${doctor_cost_per_hour:,.2f}

---

By adjusting the inputs in the sidebar, you can explore how changes in staffing or patient load affect revenue and costs, helping you make informed decisions for your RPM program.
"""
st.markdown(interpretation_text)
