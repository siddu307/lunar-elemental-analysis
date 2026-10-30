
import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MAIN_DB = BASE_DIR / "lunar_analysis.db"
ML_DB = BASE_DIR / "lunar_ml_integration.db"


st.set_page_config(
    page_title="Lunar Elemental Analysis",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌙 Lunar Elemental Analysis Dashboard")
st.caption("Chandrayaan-2 pixel measurements and machine-learning results")

st.markdown("""
<style>
.stApp {
    background-color: #F4F7FB;
}
h1, h2, h3 {
    color: #102A43;
}
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #D9E2EC;
    padding: 18px;
    border-radius: 12px;
}
div[data-testid="stMetricValue"] {
    color: #087EBA;
}
.stDataFrame {
    border: 1px solid #D9E2EC;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_summary():
    with sqlite3.connect(MAIN_DB) as conn:
        total_pixels = conn.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0]

    with sqlite3.connect(ML_DB) as conn:
        total_ml = conn.execute(
            "SELECT COUNT(*) FROM ml_results"
        ).fetchone()[0]

        anomaly_count = conn.execute(
            "SELECT COUNT(*) FROM ml_results WHERE isolation_forest_flag = 1"
        ).fetchone()[0]

        cluster_counts = pd.read_sql_query(
            """
            SELECT cluster_label, COUNT(*) AS pixel_count
            FROM ml_results
            GROUP BY cluster_label
            ORDER BY cluster_label
            """,
            conn
        )

    return total_pixels, total_ml, anomaly_count, cluster_counts

total_pixels, total_ml, anomaly_count, cluster_counts = load_summary()

col1, col2, col3 = st.columns(3)
col1.metric("Total Pixel Records", f"{total_pixels:,}")
col2.metric("ML Sample Records", f"{total_ml:,}")
col3.metric("Flagged Anomalies", f"{anomaly_count:,}")

st.sidebar.title("Dashboard Filters")
st.sidebar.write("Filter the machine-learning sample.")

cluster_filter = st.sidebar.selectbox(
    "Select cluster",
    ["All clusters", 0, 1, 2]
)

anomaly_filter = st.sidebar.selectbox(
    "Anomaly status",
    ["All records", "Flagged anomalies", "Normal records"]
)

st.subheader("ML Cluster Distribution")

@st.cache_data
def load_filtered_cluster_counts(anomaly_filter):
    query = """
        SELECT cluster_label, COUNT(*) AS pixel_count
        FROM ml_results
    """
    params = []

    if anomaly_filter == "Flagged anomalies":
        query += " WHERE isolation_forest_flag = 1"
    elif anomaly_filter == "Normal records":
        query += " WHERE isolation_forest_flag = 0"

    query += " GROUP BY cluster_label ORDER BY cluster_label"

    with sqlite3.connect(ML_DB) as conn:
        return pd.read_sql_query(query, conn, params=params)

filtered_cluster_counts = load_filtered_cluster_counts(anomaly_filter)
if cluster_filter != "All clusters":
    filtered_cluster_counts = filtered_cluster_counts[
        filtered_cluster_counts["cluster_label"] == cluster_filter
    ]
st.bar_chart(
    filtered_cluster_counts.set_index("cluster_label")["pixel_count"]
)

st.subheader("Explore Combined Pixel and ML Results")
search_col1, search_col2 = st.columns(2)

with search_col1:
    row_search = st.text_input("Search by Pixel Row")

with search_col2:
    column_search = st.text_input("Search by Pixel Column")

limit = st.selectbox("Records to display", [10, 20, 50, 100], index=1)
offset = st.number_input("Starting offset", min_value=0, value=0, step=10)


@st.cache_data
def load_combined_results(limit, offset, cluster_filter, anomaly_filter, row_search, column_search):
    query = """
        SELECT
            o.pixel_y AS pixel_row,
            o.pixel_x AS pixel_column,
            o.band_1,
            o.band_2,
            m.cluster_label,
            m.isolation_forest_score,
            m.isolation_forest_flag
        FROM observations o
        INNER JOIN ml_db.ml_results m
            ON o.pixel_y = m.pixel_row
            AND o.pixel_x = m.pixel_column
        WHERE 1=1
    """

    params = []

    if row_search.strip():
        query += " AND o.pixel_y = ?"
        params.append(int(row_search))

    if column_search.strip():
        query += " AND o.pixel_x = ?"
        params.append(int(column_search))

    if cluster_filter != "All clusters":
        query += " AND m.cluster_label = ?"
        params.append(cluster_filter)

    if anomaly_filter == "Flagged anomalies":
        query += " AND m.isolation_forest_flag = 1"
    elif anomaly_filter == "Normal records":
        query += " AND m.isolation_forest_flag = 0"

    query += " ORDER BY o.pixel_y, o.pixel_x LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with sqlite3.connect(MAIN_DB) as conn:
        conn.execute(
            "ATTACH DATABASE ? AS ml_db",
            (str(ML_DB),)
        )

        return pd.read_sql_query(query, conn, params=params)

results = load_combined_results(
    limit,
    offset,
    cluster_filter,
    anomaly_filter,
    row_search,
    column_search
)
@st.cache_data
def count_filtered_results(cluster_filter, anomaly_filter, row_search, column_search):
    query = "SELECT COUNT(*) FROM ml_results WHERE 1=1"
    params = []

    if row_search.strip():
        query += " AND pixel_row = ?"
        params.append(int(row_search))

    if column_search.strip():
        query += " AND pixel_column = ?"
        params.append(int(column_search))

    if cluster_filter != "All clusters":
        query += " AND cluster_label = ?"
        params.append(cluster_filter)

    if anomaly_filter == "Flagged anomalies":
        query += " AND isolation_forest_flag = 1"
    elif anomaly_filter == "Normal records":
        query += " AND isolation_forest_flag = 0"

    with sqlite3.connect(ML_DB) as conn:
        return conn.execute(query, params).fetchone()[0]


filtered_count = count_filtered_results(
    cluster_filter,
    anomaly_filter,
    row_search,
    column_search
)
st.metric("Records Matching Filters", f"{filtered_count:,}")
st.write(f"Showing {len(results)} records matching your filters")
st.dataframe(results, use_container_width=True)
st.download_button(
    label="Download Filtered Results as CSV",
    data=results.to_csv(index=False).encode("utf-8"),
    file_name="lunar_filtered_results.csv",
    mime="text/csv"
)

st.caption(
    "Note: Cluster labels and anomaly flags are model outputs, "
    "not confirmed geological classifications."
)
