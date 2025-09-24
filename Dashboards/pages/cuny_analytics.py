import os
import pandas as pd
import streamlit as st
import altair as alt

# ------------------------
# Page Config
# ------------------------
st.set_page_config(
    page_title="CUNY Campus Violations & Ridership",
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
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    path = os.path.join(data_dir, f"{dataset_name}.csv")

    if not os.path.exists(path):
        st.error(f"❌ Dataset '{path}' not found!")
        return pd.DataFrame()

    return pd.read_csv(path)


# ------------------------
# Visualization Functions
# ------------------------
def plot_monthly_violations(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return None

    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("month:N", sort=month_order),
            y="violations:Q",
            color="campus_name:N",
            tooltip=["campus_name", "month", "violations"]
        )
        .properties(height=400, title="Monthly Violations per Campus")
    )


def plot_violation_types(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return None

    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("violation_type:N", sort="-y"),
            y="violations:Q",
            color="campus_name:N",
            tooltip=["campus_name", "violation_type", "violations"]
        )
        .properties(height=400, title="Violations by Type per Campus")
    )


def plot_ridership_by_campus(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return None

    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x="campus_name:N",
            y="total_ridership:Q",
            color="campus_name:N",
            tooltip=["campus_name", "total_ridership"]
        )
        .properties(height=400, title="Total Ridership per Campus")
    )


def plot_ridership_by_route(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return None

    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("campus_name:N", sort="-y", title="Campus"),
            y=alt.Y("total_ridership:Q", title="Total Ridership"),
            color="campus_name:N",
            tooltip=["campus_name", "route_id", "total_ridership"]
        )
        .properties(height=400, title="Ridership by Campus for Selected Route")
    )




# ------------------------
# Main Page
# ------------------------
def main():
    # Load datasets
    monthly_df = load_csv("monthly_violations_per_campus_2025")
    type_df = load_csv("violations_by_type_per_campus_2025")
    ridership_df = load_csv("ridership_route_campus")

    st.title("🏫 CUNY Campus Dashboard")

    # ------------------------
    # Violations Section
    # ------------------------
    st.header("🚨 Violations Analysis")

    selected_month = st.selectbox(
        "📅 Filter Violations by Month",
        ["All"] + sorted(monthly_df["month"].dropna().unique().tolist(),
                         key=lambda x: pd.to_datetime(x, errors="coerce"))
    )

    selected_violation = st.selectbox(
        "⚠️ Filter by Violation Type",
        ["All"] + sorted(type_df["violation_type"].dropna().unique().tolist())
    )

    selected_campus_violations = st.selectbox(
        "🏛️ Filter Violations by Campus",
        ["All"] + sorted(monthly_df["campus_name"].dropna().unique().tolist())
    )

    filtered_monthly = monthly_df.copy()
    filtered_types = type_df.copy()

    if selected_month != "All":
        filtered_monthly = filtered_monthly[filtered_monthly["month"] == selected_month]

    if selected_violation != "All":
        filtered_types = filtered_types[filtered_types["violation_type"] == selected_violation]

    if selected_campus_violations != "All":
        filtered_monthly = filtered_monthly[filtered_monthly["campus_name"] == selected_campus_violations]
        filtered_types = filtered_types[filtered_types["campus_name"] == selected_campus_violations]

    # ------------------------
    # Violations KPIs
    # ------------------------
    st.subheader("📊 Violations KPIs")
    col1, col2 = st.columns(2)

    with col1:
        total_violations = filtered_monthly["violations"].sum()
        st.metric("Total Violations", f"{total_violations:,}")

    with col2:
        avg_violations = filtered_monthly["violations"].mean()
        st.metric("Average Violations per Campus", f"{avg_violations:.2f}")

    st.subheader("Monthly Violations")
    chart1 = plot_monthly_violations(filtered_monthly)
    if chart1:
        st.altair_chart(chart1, use_container_width=True)

    st.subheader("Violations by Type")
    chart2 = plot_violation_types(filtered_types)
    if chart2:
        st.altair_chart(chart2, use_container_width=True)

    # ------------------------
    # Ridership Section
    # ------------------------
    st.header("🚌 Ridership Analysis")

    selected_route = st.selectbox(
        "🚌 Select Route",
        ["All"] + sorted(ridership_df["route_id"].dropna().unique().tolist())
    )

    # Only filter by route — do NOT filter campuses
    route_filtered_ridership = ridership_df.copy()
    if selected_route != "All":
        route_filtered_ridership = route_filtered_ridership[
            route_filtered_ridership["route_id"] == selected_route
        ]

    # ------------------------
    # Ridership KPIs
    # ------------------------
    st.subheader("📊 Ridership KPIs")
    col3, col4 = st.columns(2)

    with col3:
        total_ridership = route_filtered_ridership["total_ridership"].sum()
        st.metric("Total Ridership", f"{total_ridership:,}")

    with col4:
        avg_ridership = route_filtered_ridership["total_ridership"].mean()
        st.metric("Average Ridership per Campus", f"{avg_ridership:.2f}")

    st.subheader("Ridership by Campus for Selected Route")
    chart4 = plot_ridership_by_route(route_filtered_ridership)
    if chart4:
        st.altair_chart(chart4, use_container_width=True)


if __name__ == "__main__":
    main()
