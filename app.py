import streamlit as st
import pandas as pd
import plotly.express as px
from extract_data import get_all_calendar_events

# Load event data (expects a tuple: (calendar_events_dict, calendar_id_mapping))
@st.cache_data
def load_data():
    return get_all_calendar_events()
calendar_events_dict, calendar_id_mapping = load_data()

st.title("Time-blocking Tracking")

# Dropdown for calendar selection
calendar_name = st.selectbox("Select a calendar", options=[info["name"] for info in calendar_id_mapping.values()])
selected_calendar_id = next(cal_id for cal_id, info in calendar_id_mapping.items() if info["name"] == calendar_name)
selected_color = calendar_id_mapping[selected_calendar_id]["color"] # Maps chart colour to colour chosen in GCalendar

# Get event data for the chosen calendar
events = calendar_events_dict[selected_calendar_id]["events"]

# Convert event data to DataFrame
df = pd.DataFrame(events)

if df.empty:
    st.warning("No past events found for this calendar.")
else:
    # Convert datetime strings to datetime objects (UTC) and coerce errors
    df["start"] = pd.to_datetime(df["start"], errors="coerce", utc=True)
    df["end"] = pd.to_datetime(df["end"], errors="coerce", utc=True)

    # Drop rows with invalid dates
    df = df.dropna(subset=["start", "end"])

    # Dropdown for granularity selection
    granularity = st.selectbox("Select granularity", options=["Week", "Month"])

    # Calculate duration in hours
    df["duration_hours"] = (df["end"] - df["start"]).dt.total_seconds() / 3600

    # Set the start column as the index for resampling
    df = df.set_index("start")

    if granularity == "Week":
        summary = df.resample("W-MON")["duration_hours"].sum().reset_index()
        # Use only the ISO week number as the label (as a string)
        summary["period"] = summary["start"].dt.strftime("%G-W%V")
    else:  # Month
        summary = df.resample("ME")["duration_hours"].sum().reset_index()
        # Use the full month name as the label (e.g. "January")
        summary["period"] = summary["start"].dt.strftime("%B")

    summary = summary.sort_values("start")
    summary["duration_minutes"] = (summary["duration_hours"] * 60).round(0)

    # Plot bar chart
    fig = px.bar(
        summary,
        x="period",
        y="duration_hours",
        text=summary["duration_hours"].round(1),
        labels={"period": granularity, "duration_hours": "Total Hours"},
        title=f"Total Time Spent Per {granularity} - {calendar_name}",
    )
    max_val = summary["duration_hours"].max()
    fig.update_yaxes(range=[0, max_val * 1.1])
    fig.update_traces(
        marker_color=selected_color,
        textposition="outside",
        hovertemplate="%{y:.2f} hours<br>%{customdata[0]} minutes",
        customdata=summary[["duration_minutes"]]
    )
    st.plotly_chart(fig)