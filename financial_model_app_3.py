import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math

# 1) Use a recognized built-in Matplotlib style
#    (e.g., "ggplot", "seaborn-whitegrid", "fivethirtyeight", etc.)
plt.style.use("seaborn-v0_8-whitegrid")

st.title("Clinician Simple RPM Model (Modern Chart)")
# -----------------------
# 1) Sidebar - Staff Inputs
# -----------------------
st.sidebar.header("Staffing Configuration")

num_clinicians = st.sidebar.slider(
    "Number of Clinicians (per Hour)",
    min_value=1,
    max_value=20,
    value=3,
    step=1
)

clinician_hourly_wage = st.sidebar.number_input(
    "Clinician Hourly Wage ($)",
    min_value=10.0,
    max_value=60.0,
    value=24.04,
    step=1.0
)

# Nurse Logic
use_nurse = st.sidebar.checkbox("Use Nurse(s)?", value=False)
if use_nurse:
    nurse_hourly_wage = st.sidebar.number_input(
        "Nurse Hourly Wage ($)",
        min_value=15.0,
        max_value=60.0,
        value=36.06,
        step=1.0
    )
    clinicians_per_nurse = st.sidebar.slider(
        "1 Nurse per N Clinicians",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )
else:
    nurse_hourly_wage = 0.0
    clinicians_per_nurse = 1  # No effect if nurse isn't used

# -----------------------
# 2) Billing Codes Setup
# -----------------------
st.sidebar.header("Billing Codes Toggle")

# Base/Conservative recurring codes (shown as checkboxes)
base_codes = {
    "99454 - RPM Device Supply": 45.12,
    "99457 - RPM Mgmt (20 mins)": 46.85,
    "99458 - RPM Mgmt (add’l 20)": 37.62,
    "99490 - CCM by Clin Staff": 59.90,
    "99491 - CCM by Physician (1/20)": 80.98 / 20,
    "99091 - Data Interpretation": 51.29,
}

# Additional codes that might be enabled
additional_codes = {
    "99487 - Complex CCM (60 mins)": 128.44,
    "99489 - Add'l Complex CCM (30 mins)": 69.13,
}

enabled_base_codes = {}
enabled_addl_codes = {}

st.sidebar.write("**Base (Conservative) Codes**:")
for code_name, code_value in base_codes.items():
    checked = st.sidebar.checkbox(code_name, value=True)
    if checked:
        enabled_base_codes[code_name] = code_value

st.sidebar.write("**Additional Codes**:")
for code_name, code_value in additional_codes.items():
    checked = st.sidebar.checkbox(code_name, value=False)
    if checked:
        enabled_addl_codes[code_name] = code_value

# Non-recurring codes (if you want them)
use_non_recurring = st.sidebar.checkbox("Include Non-Recurring Codes?", value=False)
non_recurring_codes = {
    "99453 - RPM Setup (one-time)": 18.95,
    "99495 - TCM (one-time)": 230.00,
}

enabled_non_recurring = {}
if use_non_recurring:
    # For simplicity, we’ll assume we always use these if toggled on
    enabled_non_recurring = non_recurring_codes

# -----------------------
# 3) Summation of Codes
# -----------------------
all_enabled_recurring_codes = {**enabled_base_codes, **enabled_addl_codes}
recurring_revenue_per_clinician_hour = sum(all_enabled_recurring_codes.values())

# Non-recurring
non_recurring_revenue_per_clinician_hour = sum(enabled_non_recurring.values())

total_revenue_per_clinician_hour = recurring_revenue_per_clinician_hour + non_recurring_revenue_per_clinician_hour

# -----------------------
# 4) Hourly Revenue & Cost
# -----------------------
# Revenue: # of clinicians × the sum of enabled codes
revenue_per_hour = num_clinicians * total_revenue_per_clinician_hour

# Clinician Cost
clinician_cost_per_hour = num_clinicians * clinician_hourly_wage

# Nurse Cost
nurse_cost_per_hour = 0.0
if use_nurse:
    # e.g., partial usage if 4 clinicians but ratio is 1 nurse per 3 => 1.33 nurses
    # If you want discrete, do math.ceil(...)
    num_nurses = num_clinicians / clinicians_per_nurse
    nurse_cost_per_hour = num_nurses * nurse_hourly_wage

total_cost_per_hour = clinician_cost_per_hour + nurse_cost_per_hour
ebitda_per_hour = revenue_per_hour - total_cost_per_hour

# -----------------------
# 5) Display in Streamlit
# -----------------------
st.subheader("Hourly Economics")

col1, col2, col3 = st.columns(3)
col1.metric("Revenue/Hour", f"${revenue_per_hour:,.2f}")
col2.metric("Cost/Hour", f"${total_cost_per_hour:,.2f}")
col3.metric("EBITDA/Hour", f"${ebitda_per_hour:,.2f}")

# Codes Summaries
st.write("---")
st.write("## Billing Codes Selected")
if all_enabled_recurring_codes:
    st.write("**Recurring Codes:**")
    for name, val in all_enabled_recurring_codes.items():
        st.write(f"- {name}: ${val:.2f}")
else:
    st.write("*No recurring codes selected.*")

if enabled_non_recurring:
    st.write("**Non-Recurring Codes:**")
    for name, val in enabled_non_recurring.items():
        st.write(f"- {name}: ${val:.2f}")
else:
    st.write("*No non-recurring codes selected.*")

# Staffing Summary
st.write("---")
st.write(f"**Clinicians**: {num_clinicians} × ${clinician_hourly_wage:.2f}/hr each.")
if use_nurse:
    st.write(
        f"**Nurse**: 1 per {clinicians_per_nurse} clinicians "
        f"=> {num_clinicians / clinicians_per_nurse:.2f} nurse(s) × "
        f"${nurse_hourly_wage:.2f}/hr each."
    )
else:
    st.write("*No nurse(s) activated.*")

# -----------------------
# 6) Bar Chart
# -----------------------
labels = ["Revenue/Hour", "Cost/Hour", "EBITDA/Hour"]
values = [revenue_per_hour, total_cost_per_hour, ebitda_per_hour]

fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
colors = ["#5DADE2", "#F1948A", "#58D68D"]  # Blue, pinkish, green

bars = ax.bar(labels, values, color=colors, edgecolor="black", zorder=2)

ax.set_ylabel("USD ($)", fontsize=12)
ax.set_title("Clinician Hourly Economics (Toggle Codes)", fontsize=14, weight="bold")

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

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)

st.pyplot(fig)
