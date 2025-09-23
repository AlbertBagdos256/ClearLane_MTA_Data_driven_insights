import os
import pandas as pd
import streamlit as st
import altair as alt

# ------------------------
# Page Config
# ------------------------
st.set_page_config(
    page_title="ACE System & Bus Performance",
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
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Dashboards/
    data_dir = os.path.join(base_dir, "data")             # Dashboards/data/
    path = os.path.join(data_dir, f"{dataset_name}.csv")

    if not os.path.exists(path):
        st.error(f"❌ Dataset '{path}' not found!")
        return pd.DataFrame()

    df = pd.read_csv(path)
    if "month_dt" in df.columns:
        df['month_dt'] = pd.to_datetime(df['month_dt'])
    return df

# ------------------------
# Visualization Functions
# ------------------------
def plot_before_after_ace(df: pd.DataFrame, metric: str) -> alt.Chart:
    if df.empty:
        return None

    df_sorted = df.sort_values("month_dt")

    # Zoom in: calculate min/max with small margin
    min_val = df_sorted[metric].min()
    max_val = df_sorted[metric].max()
    margin = (max_val - min_val) * 0.1
    y_min = min_val - margin
    y_max = max_val + margin

    chart = (
        alt.Chart(df_sorted)
        .mark_line(point=True)
        .encode(
            x=alt.X("month_dt:T", title="Month"),
            y=alt.Y(f"{metric}:Q", title=f"{metric}", scale=alt.Scale(domain=[y_min, y_max])),
            color=alt.Color("is_ACE:N", title="ACE Active",
                            scale=alt.Scale(domain=[False, True],
                                            range=["#1f77b4", "#ff7f0e"])),
            tooltip=["Route ID", "month_dt", "is_ACE", metric]
        )
        .properties(height=400, title=f"{metric} Before vs After ACE")
    )
    return chart

def plot_top_bottom_routes(df: pd.DataFrame) -> alt.Chart:
    if df.empty:
        return None

    # Sort ascending to capture bottom and top properly
    df_sorted = df.sort_values("Pct Change", ascending=True)

    # Bottom 5 (most negative), top 5 (most positive)
    bottom5 = df_sorted.head(5)
    top5 = df_sorted.tail(5)
    highlight = pd.concat([bottom5, top5])

    # Sort highlight so left-to-right = most negative → most positive
    highlight = highlight.sort_values("Pct Change")

    # Vertical bar chart
    chart = (
        alt.Chart(highlight)
        .mark_bar()
        .encode(
            x=alt.X("Route ID:N", sort=highlight["Route ID"].tolist(), title="Route ID"),
            y=alt.Y("Pct Change:Q", title="% Change in Average Speed"),
            color=alt.condition(
                alt.datum["Pct Change"] > 0,
                alt.value("green"),
                alt.value("red")
            ),
            tooltip=["Route ID", "False", "True", "Pct Change"]
        )
        .properties(
            height=400,
            width=700,
            title="Top/Bottom Routes by % Change in Average Speed After ACE"
        )
    )
    return chart



# ------------------------
# Main Page
# ------------------------
def main():
    df = load_csv("before_after_ace")
    top_routes_df = load_csv("top5")
    if df.empty:
        st.stop()

    st.title("🚍 ACE System & Bus Performance Dashboard")

    # ------------------------
    # Filters
    # ------------------------
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        route_options = sorted(df["Route ID"].dropna().unique().tolist())
        selected_route = st.selectbox("🚌 Select Bus Route", route_options)

    with filter_col2:
        metric_options = ["Average Road Speed", "Average Travel Time"]
        selected_metric = st.selectbox("📊 Metric to Plot", metric_options)

    # ------------------------
    # Apply Filters
    # ------------------------
    filtered = df.copy()
    if selected_route != "All":
        filtered = filtered[filtered["Route ID"] == selected_route]

    # ------------------------
    # KPIs
    # ------------------------
    avg_val = filtered[selected_metric].mean() if not filtered.empty else 0

    before_ace = filtered[filtered["is_ACE"] == False][selected_metric].mean()
    after_ace = filtered[filtered["is_ACE"] == True][selected_metric].mean()

    if pd.notnull(before_ace) and pd.notnull(after_ace) and before_ace != 0:
        percent_change = ((after_ace - before_ace) / before_ace) * 100
    else:
        percent_change = None

    metric_unit = "mph" if "Speed" in selected_metric else "min"

    kpi_col1, kpi_col2 = st.columns(2)
    kpi_col1.metric(f"Average {selected_metric}", f"{avg_val:.2f} {metric_unit}")
    if percent_change is not None:
        kpi_col2.metric(f"Change After ACE", f"{percent_change:.2f}%", delta=f"{percent_change:.2f}%")
    else:
        kpi_col2.metric(f"Change After ACE", "N/A")

    # ------------------------
    # Plot Before vs After ACE
    # ------------------------
    chart = plot_before_after_ace(filtered, selected_metric)
    if chart:
        st.altair_chart(chart, use_container_width=True)

    # ------------------------
    # Top/Bottom Routes Chart
    # ------------------------
    if not top_routes_df.empty:
        st.markdown("### 🚀 Top/Bottom Routes by Speed Change")
        top_bottom_chart = plot_top_bottom_routes(top_routes_df)
        if top_bottom_chart:
            st.altair_chart(top_bottom_chart, use_container_width=True)

if __name__ == "__main__":
    main()
