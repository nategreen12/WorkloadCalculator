import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Special Education Case Manager Workload Calculator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Special Education Case Manager Workload Calculator")
st.caption("Estimate annual workload, contract overage, and remote-capable vs. in-person duties.")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Contract & Caseload")
contract_days = st.sidebar.number_input("Contract Days", min_value=0.0, value=185.0, step=1.0)
hours_per_day = st.sidebar.number_input("Hours Per Day", min_value=0.0, value=7.25, step=0.25)
caseload = st.sidebar.number_input("Student Caseload", min_value=0, value=100, step=1)

st.sidebar.header("IEP Work")
annual_ieps = st.sidebar.number_input("Annual IEPs", min_value=0, value=100, step=1)
annual_iep_hours = st.sidebar.number_input("Hours per Annual IEP", min_value=0.0, value=2.5, step=0.25)
amendments = st.sidebar.number_input("Amendments", min_value=0, value=60, step=1)
amendment_hours = st.sidebar.number_input("Hours per Amendment", min_value=0.0, value=1.25, step=0.25)
iep_meetings = st.sidebar.number_input("IEP Meetings", min_value=0, value=100, step=1)
iep_meeting_hours = st.sidebar.number_input("Hours per Meeting Cycle", min_value=0.0, value=1.5, step=0.25)
manifestations = st.sidebar.number_input("Manifestations", min_value=0, value=0, step=1)
manifestation_hours = st.sidebar.number_input("Hours per Manifestation", min_value=0.0, value=2.0, step=0.25)

st.sidebar.header("Evaluation Work")
evaluations = st.sidebar.number_input("Evaluations", min_value=0, value=50, step=1)
evaluation_hours = st.sidebar.number_input("Hours per Evaluation", min_value=0.0, value=8.0, step=0.25)

st.sidebar.header("Communication")
family_minutes = st.sidebar.number_input("Family Minutes per Student per Week", min_value=0.0, value=5.0, step=0.5)
staff_minutes = st.sidebar.number_input("Staff Minutes per Student per Week", min_value=0.0, value=3.0, step=0.5)
communication_weeks = st.sidebar.number_input("Communication Weeks", min_value=0, value=36, step=1)
other_communication_hours = st.sidebar.number_input("Other Communication Hours", min_value=0.0, value=0.0, step=1.0)

st.sidebar.header("In-Person Work")
academic_testing_evals = st.sidebar.number_input("Academic Testing Evaluations", min_value=0, value=15, step=1)
academic_testing_hours = st.sidebar.number_input("Hours per Academic Testing Eval", min_value=0.0, value=1.5, step=0.25)
observations_per_student = st.sidebar.number_input("Observations/Check-ins per Student", min_value=0.0, value=3.0, step=0.5)
observation_minutes = st.sidebar.number_input("Minutes per Observation/Check-in", min_value=0.0, value=20.0, step=1.0)

st.sidebar.header("Progress Reports")
progress_reports_per_student = st.sidebar.number_input("Progress Reports per Student", min_value=0.0, value=3.0, step=0.5)
progress_report_minutes = st.sidebar.selectbox(
    "Minutes per Progress Report",
    options=[0, 15, 30, 45, 60, 75, 90],
    index=2)

st.sidebar.header("Other Duties")
other_duties_hours = st.sidebar.number_input(
    "Other Duties Hours",
    min_value=0.0,
    value=0.0,
    step=1.0)

# -----------------------------
# Calculations
# -----------------------------
contracted_hours = contract_days * hours_per_day

iep_work = (
    annual_ieps * annual_iep_hours
    + amendments * amendment_hours
    + iep_meetings * iep_meeting_hours
    + manifestations * manifestation_hours
)

evaluation_work = evaluations * evaluation_hours

family_communication = (caseload * family_minutes * communication_weeks) / 60
staff_communication = (caseload * staff_minutes * communication_weeks) / 60
communication_total = family_communication + staff_communication + other_communication_hours

academic_testing = academic_testing_evals * academic_testing_hours
observations = (caseload * observations_per_student * observation_minutes) / 60
in_person_total = academic_testing + observations

progress_report_total = (caseload * progress_reports_per_student * progress_report_minutes) / 60

total_without_progress = iep_work + evaluation_work + communication_total + in_person_total + other_duties_hours
total_with_progress = total_without_progress + progress_report_total

remote_without_progress = iep_work + evaluation_work + communication_total + other_duties_hours
remote_with_progress = remote_without_progress + progress_report_total

over_without_progress = total_without_progress - contracted_hours
over_with_progress = total_with_progress - contracted_hours

days_over_without_progress = over_without_progress / hours_per_day if hours_per_day else 0
days_over_with_progress = over_with_progress / hours_per_day if hours_per_day else 0

remote_percent = (remote_with_progress / total_with_progress * 100) if total_with_progress else 0
in_person_percent = (in_person_total / total_with_progress * 100) if total_with_progress else 0

# -----------------------------
# Summary Metrics
# -----------------------------
st.subheader("Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Contracted Hours", f"{contracted_hours:,.1f}")
col2.metric("Total Workload", f"{total_with_progress:,.1f}")
col3.metric("Over Contract", f"{over_with_progress:,.1f} hrs", f"{days_over_with_progress:,.1f} days")
col4.metric("Remote-Capable Work", f"{remote_percent:,.1f}%", f"{remote_with_progress:,.1f} hrs")

if over_with_progress > 0:
    st.warning(f"Estimated workload is over contracted time by approximately {over_with_progress:,.1f} hours, or {days_over_with_progress:,.1f} work days.")
else:
    st.success("Estimated workload is within contracted time.")

# -----------------------------
# Tables
# -----------------------------
workload_df = pd.DataFrame({
    "Category": [
        "IEP Work",
        "Evaluation Work",
        "Communication",
        "Progress Reports",
        "In-Person Work"
    ],
    "Hours": [
        iep_work,
        evaluation_work,
        communication_total,
        progress_report_total,
        in_person_total
    ],
    "Location": [
        "Remote-capable",
        "Remote-capable",
        "Remote-capable",
        "Remote-capable",
        "In-person"
    ]
})

workload_df["Percent of Total"] = workload_df["Hours"] / total_with_progress * 100 if total_with_progress else 0

st.subheader("Annual Workload Breakdown")
st.dataframe(
    workload_df.style.format({"Hours": "{:.1f}", "Percent of Total": "{:.1f}%"}),
    use_container_width=True
)

# -----------------------------
# Charts
# -----------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Workload by Category")
    fig = px.pie(
        workload_df,
        names="Category",
        values="Hours",
        hole=0.35,
        title="Estimated Hours by Workload Category"
    )
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.subheader("Remote vs. In-Person")
    location_df = pd.DataFrame({
        "Location": ["Remote-capable", "In-person"],
        "Hours": [remote_with_progress, in_person_total]
    })
    fig2 = px.pie(
        location_df,
        names="Location",
        values="Hours",
        hole=0.35,
        title="Remote-Capable vs. In-Person Work"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Contract Comparison")
comparison_df = pd.DataFrame({
    "Scenario": [
        "Contracted Hours",
        "Workload Without Progress Reports",
        "Workload With Progress Reports"
    ],
    "Hours": [contracted_hours, total_without_progress, total_with_progress]
})
fig3 = px.bar(
    comparison_df,
    x="Scenario",
    y="Hours",
    text="Hours",
    title="Contracted Hours Compared to Estimated Workload"
)
fig3.update_traces(texttemplate="%{text:.1f}", textposition="outside")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Detailed Summary Text
# -----------------------------
st.subheader("Copy/Paste Summary")
summary_text = f"""
Annual Workload Breakdown (Estimated)

Total Contracted Hours: {contracted_hours:,.1f} hours ({contract_days:,.0f} days × {hours_per_day:,.2f} hours)
Total Estimated Workload Without Progress Reports: {total_without_progress:,.1f} hours
Over/Under Contract Without Progress Reports: {over_without_progress:,.1f} hours ({days_over_without_progress:,.1f} days)

Total Estimated Workload With Progress Reports: {total_with_progress:,.1f} hours
Over/Under Contract With Progress Reports: {over_with_progress:,.1f} hours ({days_over_with_progress:,.1f} days)

IEP Work: {iep_work:,.1f} hours
Evaluation Work: {evaluation_work:,.1f} hours
Communication: {communication_total:,.1f} hours
Progress Reports: {progress_report_total:,.1f} hours
In-Person Work: {in_person_total:,.1f} hours

Remote-Capable Work: {remote_with_progress:,.1f} hours ({remote_percent:,.1f}%)
In-Person Work: {in_person_total:,.1f} hours ({in_person_percent:,.1f}%)
"""

st.text_area("Summary", summary_text, height=320)

# -----------------------------
# Notes
# -----------------------------
st.caption("Note: This calculator provides an estimate based on user-entered assumptions. Actual workload may vary depending on student needs, timelines, compliance requirements, meeting complexity, and district procedures.")
st.markdown("---")
st.caption("Special Education Case Manager Workload Calculator © 2026 Nate Green")
