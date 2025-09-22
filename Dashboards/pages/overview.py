import os
import pandas as pd
import streamlit as st
import altair as alt

# ------------------------
# Page Config
# ------------------------
st.set_page_config(
    page_title="NYC Bus Violations - Overview",
    layout="wide"
)

# ------------------------
# Load Custom CSS
# ------------------------
def load_custom_css(css_file: str):
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css("assets/style.css")

# ------------------------
# Data Loading
# ------------------------
@st.cache_data
def load_csv(dataset_name: str) -> pd.DataFrame:
    path = os.path.join("insights", f"{dataset_name}.csv")
    if not os.path.exists(path):
        st.error(f"❌ Dataset '{dataset_name}.csv' not found!")
        return pd.DataFrame()
    return pd.read_csv(path)

# ------------------------
# Visualization Functions
# ------------------------
def plot_weekday_violations(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return None

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["weekday"] = pd.Categorical(df["weekday"], categories=weekday_order, ordered=True)

    bars = alt.Chart(df).mark_bar().encode(
        x=alt.X("weekday:N", title="Day of Week", sort=weekday_order),
        y=alt.Y("violations:Q", title="Number of Violations"),
        color=alt.Color("violations:Q", scale=alt.Scale(scheme="reds")),
        tooltip=["weekday", "violations"]
    )

    text = bars.mark_text(dy=-5, color="black").encode(
        text=alt.Text("violations:Q", format=",.0f")
    )

    return (bars + text).properties(height=400, title="Violations by Day of the Week")


def plot_hourly_violations(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return None

    line = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("hour:O", title="Hour of Day"),
        y=alt.Y("violations:Q", title="Number of Violations"),
        tooltip=["hour", "violations"]
    ).properties(height=400, title="Hourly Violations")

    return line

# ------------------------
# Heatmap Function
# ------------------------
def plot_weekday_hour_heatmap(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return None

    # Ensure weekday is ordered
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["weekday"] = pd.Categorical(df["weekday"], categories=weekday_order, ordered=True)

    heatmap = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("hour:O", title="Hour of Day"),
            y=alt.Y("weekday:N", title="Day of Week", sort=weekday_order),
            color=alt.Color("violations:Q", scale=alt.Scale(scheme="reds"), title="Violations"),
            tooltip=["weekday", "hour", "violations"]
        )
        .properties(height=400, title="Heatmap of Violations (Hour × Weekday)")
    )

    return heatmap

# ------------------------
# Main Page
# ------------------------
def main():
    # Load datasets
    weekday_counts = load_csv("../data/weekday_counts")
    hourly_counts = load_csv("../data/hourly_counts")
    monthly_counts = load_csv("../data/monthly_counts")
    stop_counts = load_csv("../data/stop_counts")
    st.title("📊 NYC Bus Violations Overview")

    # ------------------------
    # Filters
    # ------------------------
    filter_col1, filter_col2, filter_col3 , filter_col4= st.columns(4)

    with filter_col1:
        month_options = ["All"] + sorted(weekday_counts["month"].dropna().unique().tolist(),
                                  key=lambda x: pd.to_datetime(x, format="%Y-%m"),
                                  reverse=True
                                  )

        selected_month = st.selectbox("📅 Filter by Month", month_options, index=0)

    with filter_col2:
        weekday_options = ["All"] + ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selected_weekday = st.selectbox("📆 Filter by Weekday", weekday_options, index=0)

    with filter_col3:
        route_options = ["All"] + sorted(weekday_counts["bus_route_id"].dropna().unique().tolist())
        selected_route = st.selectbox("🚌 Filter by Bus Route", route_options, index=0)

    with filter_col4:
        violation_options = ["All"] + sorted(weekday_counts["violation_type"].dropna().unique().tolist())
        selected_violation = st.selectbox("⚠️ Filter by Violation Type", violation_options, index=0)
    # ------------------------
    # Apply Filters
    # ------------------------
    filtered_weekday = weekday_counts.copy()
    filtered_hourly = hourly_counts.copy()
    filtered_monthly = monthly_counts.copy()

    if selected_month != "All":
        filtered_weekday = filtered_weekday[filtered_weekday["month"] == selected_month]
        filtered_hourly = filtered_hourly[filtered_hourly["month"] == selected_month]
        filtered_monthly = filtered_monthly[filtered_monthly["month"] == selected_month]
        stop_counts = stop_counts[stop_counts["month"] == selected_month]

    if selected_weekday != "All":
        filtered_weekday = filtered_weekday[filtered_weekday["weekday"] == selected_weekday]
        filtered_hourly = filtered_hourly[filtered_hourly["weekday"] == selected_weekday]
        top_counts = stop_counts[stop_counts["weekday"] == selected_weekday]

    if selected_route != "All":
        filtered_weekday = filtered_weekday[filtered_weekday["bus_route_id"] == selected_route]
        filtered_hourly = filtered_hourly[filtered_hourly["bus_route_id"] == selected_route]
        filtered_monthly = filtered_monthly[filtered_monthly["bus_route_id"] == selected_route]
        stop_counts = stop_counts[stop_counts["bus_route_id"] == selected_route]
    
    if selected_violation != "All":
        filtered_weekday = filtered_weekday[filtered_weekday["violation_type"] == selected_violation]
        filtered_hourly = filtered_hourly[filtered_hourly["violation_type"] == selected_violation]
        filtered_monthly = filtered_monthly[filtered_monthly["violation_type"] == selected_violation]
        stop_counts = stop_counts[stop_counts["violation_type"] == selected_violation]

    
    
    # ------------------------
    # KPIs
    # ------------------------
    total_violations = int(filtered_weekday["violations"].sum())
    if not filtered_hourly.empty:
        peak_hour_row = filtered_hourly.loc[filtered_hourly["violations"].idxmax()]
        peak_hour = int(peak_hour_row["hour"])
        peak_hour_count = int(peak_hour_row["violations"])
    else:
        peak_hour, peak_hour_count = "-", "-"

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Total Violations", f"{total_violations:,}")
    kpi_col2.metric("Peak Hour", f"{peak_hour}")
    kpi_col3.metric("Violations at Peak Hour", f"{peak_hour_count}")

    # ------------------------
    # Charts
    # ------------------------
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        chart1 = plot_weekday_violations(
            filtered_weekday.groupby("weekday", as_index=False)["violations"].sum()
        )
        if chart1:
            st.altair_chart(chart1, use_container_width=True)

    with chart_col2:
        chart2 = plot_hourly_violations(
            filtered_hourly.groupby("hour", as_index=False)["violations"].sum()
        )
        if chart2:
            st.altair_chart(chart2, use_container_width=True)

    

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown("### 🏙️ Top 10 Stops with Most Violations")
        top_stops = (
            stop_counts.groupby("stop_name", as_index=False)["violations"].sum()
            .sort_values("violations", ascending=False)
            .head(10)
        )

        if not top_stops.empty:
            stops_chart = (
                alt.Chart(top_stops)
                .mark_bar()
                .encode(
                    x=alt.X("violations:Q", title="Violations"),
                    y=alt.Y("stop_name:N", title="Bus Stop", sort="-x"),
                    color=alt.Color("violations:Q", scale=alt.Scale(scheme="reds")),
                    tooltip=["stop_name", "violations"]
                )
                .properties(height=400)
            )
            st.altair_chart(stops_chart, use_container_width=True)

    with chart_col4:
        st.markdown("### 🔥 When Do Violations Spike?")
        heatmap_data = (
            filtered_hourly.groupby(["weekday", "hour"], as_index=False)["violations"].sum()
        )
        heatmap_chart = plot_weekday_hour_heatmap(heatmap_data)
        if heatmap_chart:
            st.altair_chart(heatmap_chart, use_container_width=True)


if __name__ == "__main__":
    main()
