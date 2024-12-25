import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Billing codes and costs
define_data = {
    "billing_codes": {
        "99453": 18.95,
        "99454": 45.12,
        "99457": 46.85,
        "99458": 37.62,
        "99490": 59.90,
        "99491": 80.98 / 20,
        "99091": 51.29,
        "99495": 230.00,
    },
    "gpci_adjustments": {
        "Virginia": 1.0,
        "Florida": 1.05,
        "Texas": 1.03,
        "New York": 1.08,
        "California": 1.1,
    },
    "recurring_costs": {"Platform Fee": 5.00, "Staffing": 25.00},
    "one_time_costs": {"Device": 185.00},
}

# Sidebar configuration
st.sidebar.header("Configure Staffing and Billing")

patients_per_clinician = st.sidebar.slider(
    "Patients per Clinician", min_value=5, max_value=50, value=20, step=5
)
clinicians_per_nurse = st.sidebar.slider(
    "Clinicians per Nurse", min_value=1, max_value=10, value=5, step=1
)
nurses_per_doctor = st.sidebar.slider(
    "Nurses per Doctor", min_value=1, max_value=10, value=3, step=1
)

billable_hours_per_week = st.sidebar.slider(
    "Billable Hours per Week", min_value=20, max_value=40, value=30, step=5
)

clinician_salary = st.sidebar.number_input(
    "Clinician Annual Salary ($)", min_value=30000, max_value=100000, value=50000, step=5000
)
nurse_salary = st.sidebar.number_input(
    "Nurse Annual Salary ($)", min_value=40000, max_value=120000, value=70000, step=5000
)
doctor_salary = st.sidebar.number_input(
    "Doctor Annual Salary ($)", min_value=100000, max_value=300000, value=200000, step=10000
)

theoretical_billing = st.sidebar.checkbox(
    "Activate Theoretical Billing Codes (Requires MD)", value=False
)

# Helper functions
def calculate_unit_economics(state, billing, recurring, one_time, patients, theoretical):
    gpci = define_data["gpci_adjustments"][state]
    codes = define_data["billing_codes"] if not theoretical else {**define_data["billing_codes"], "Alzheimer's Prevention": 180.00, "Mental Health Support": 120.00, "Preventive Care": 200.00}

    recurring_revenue = (
        codes["99454"]
        + codes["99457"]
        + codes["99458"]
        + codes["99490"]
        + (codes["99491"] / 20)
        + codes["99091"]
    )

    if theoretical:
        recurring_revenue += codes.get("Alzheimer's Prevention", 0) + codes.get("Mental Health Support", 0)

    recurring_revenue *= gpci
    non_recurring_revenue = (codes["99453"] + codes["99495"]) * gpci

    recurring_cost = patients * (recurring["Staffing"] + recurring["Platform Fee"])
    non_recurring_cost = one_time["Device"] * patients

    ebitda = recurring_revenue - recurring_cost + non_recurring_revenue - non_recurring_cost

    return {
        "State": state,
        "Recurring Revenue": recurring_revenue,
        "Non-Recurring Revenue": non_recurring_revenue,
        "Recurring Costs": recurring_cost,
        "Non-Recurring Costs": non_recurring_cost,
        "EBITDA": ebitda,
    }

unit_df = pd.DataFrame.from_dict(
    {
        state: calculate_unit_economics(
            state=state,
            billing=define_data["billing_codes"],
            recurring=define_data["recurring_costs"],
            one_time=define_data["one_time_costs"],
            patients=patients_per_clinician,
            theoretical=theoretical_billing,
        )
        for state in define_data["gpci_adjustments"]
    },
    orient='index'
)

# Calculate revenue per billable hour
revenue_per_hour = unit_df["Recurring Revenue"].sum() / (billable_hours_per_week * 52)
cost_per_hour = (clinician_salary + nurse_salary + doctor_salary) / (billable_hours_per_week * 52)
ebita_per_hour = revenue_per_hour - cost_per_hour

# Display results
st.title("Unit Economics Dashboard")
st.subheader("Key Metrics per State")
st.dataframe(unit_df)

st.markdown(f"### Revenue per Billable Hour: ${revenue_per_hour:.2f}")
st.markdown(f"### Cost per Billable Hour: ${cost_per_hour:.2f}")
st.markdown(f"### EBITDA per Billable Hour: ${ebita_per_hour:.2f}")

# Visualization
custom_palette = [
    mcolors.CSS4_COLORS["mediumseagreen"],
    mcolors.CSS4_COLORS["indianred"],
    mcolors.CSS4_COLORS["cornflowerblue"],
    mcolors.CSS4_COLORS["darkorange"],
]

fig, ax = plt.subplots(3, 1, figsize=(10, 18))

# Revenue vs Costs by State
x = np.arange(len(unit_df))
width = 0.4

ax[0].bar(x - width / 2, unit_df["Recurring Revenue"], width, label="Recurring Revenue", color=custom_palette[0])
ax[0].bar(x - width / 2, unit_df["Non-Recurring Revenue"], width, bottom=unit_df["Recurring Revenue"], label="Non-Recurring Revenue", color=custom_palette[1])
ax[0].bar(x + width / 2, -unit_df["Recurring Costs"], width, label="Recurring Costs", color=custom_palette[2])
ax[0].bar(x + width / 2, -unit_df["Non-Recurring Costs"], width, bottom=-unit_df["Recurring Costs"], label="Non-Recurring Costs", color=custom_palette[3])
ax[0].set_xticks(x)
ax[0].set_xticklabels(unit_df.index, rotation=45, ha='right')
ax[0].set_xlabel("State")
ax[0].set_ylabel("USD ($)")
ax[0].set_title("Revenue vs Costs by State")
ax[0].legend()
ax[0].grid(axis='y', linestyle='--', alpha=0.7)

# EBITDA by State
ax[1].bar(x, unit_df["EBITDA"], color=custom_palette[0])
ax[1].set_xticks(x)
ax[1].set_xticklabels(unit_df.index, rotation=45, ha='right')
ax[1].set_xlabel("State")
ax[1].set_ylabel("EBITDA ($)")
ax[1].set_title("EBITDA by State")
ax[1].grid(axis='y', linestyle='--', alpha=0.7)

# Revenue vs Cost per Billable Hour
metrics = [revenue_per_hour, cost_per_hour, ebita_per_hour]
labels = ["Revenue per Hour", "Cost per Hour", "EBITDA per Hour"]
ax[2].bar(labels, metrics, color=custom_palette[:3])
ax[2].set_title("Key Metrics per Billable Hour")
ax[2].set_ylabel("USD ($)")
ax[2].grid(axis='y', linestyle='--', alpha=0.7)

st.pyplot(fig)
