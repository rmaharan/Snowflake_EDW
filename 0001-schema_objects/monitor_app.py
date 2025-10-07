# app.py
import os
import pandas as pd
import streamlit as st
import altair as alt
import datetime as dt
import snowflake.connector
 
# ----------------------------
# App config
# ----------------------------
st.set_page_config(page_title="Snowflake Usage Monitor", layout="wide")
st.title("❄️ Snowflake Usage Monitor")
st.caption("Interactive dashboard over SNOWFLAKE.ACCOUNT_USAGE (credits, queries, storage)")
 
# ----------------------------
# Connection helpers
# ----------------------------
@st.cache_resource(show_spinner=False)

 
@st.cache_data(ttl=900, show_spinner=False)
def run_query(sql: str, params: dict | None = None):
    with get_connection() as conn:
        cur = conn.cursor(snowflake.connector.DictCursor)
        try:
            cur.execute(sql, params=params or {})
            rows = cur.fetchall()
            return pd.DataFrame(rows)
        finally:
            cur.close()
 
# ----------------------------
# Sidebar filters
# ----------------------------
with st.sidebar:
    st.header("Filters")
    end_date = st.date_input("End date", value=dt.date.today())
    start_date = st.date_input("Start date", value=end_date - dt.timedelta(days=30))
    if start_date > end_date:
        st.error("Start date must be <= end date")
 
    wh_df = run_query("""
        SELECT DISTINCT WAREHOUSE_NAME
        FROM WAREHOUSE_METERING_HISTORY
        WHERE START_TIME >= :start AND START_TIME < :end
        ORDER BY 1
    """, {"start": start_date, "end": end_date + dt.timedelta(days=1)})
    warehouse_options = ["(All)"] + wh_df["WAREHOUSE_NAME"].dropna().tolist()
    warehouse_pick = st.selectbox("Warehouse", warehouse_options, index=0)
 
# ----------------------------
# Helper for params
# ----------------------------
base_params = {"start": start_date, "end": end_date + dt.timedelta(days=1)}
if warehouse_pick != "(All)":
    base_params["warehouse_name"] = warehouse_pick
 
# ----------------------------
# Tabs
# ----------------------------
tab1, tab2, tab3 = st.tabs(["💳 Credits", "⚙️ Query Performance", "💾 Storage"])
 
# ===== Tab 1: Credits =====
with tab1:
    sql = """
    SELECT
      DATE_TRUNC('day', START_TIME) AS USAGE_DATE,
      WAREHOUSE_NAME,
      SUM(CREDITS_USED) AS DAILY_CREDITS,
      SUM(CREDITS_USED_COMPUTE) AS COMPUTE_CREDITS,
      SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_CREDITS
    FROM WAREHOUSE_METERING_HISTORY
    WHERE START_TIME >= :start AND START_TIME < :end
    """
    if warehouse_pick != "(All)":
        sql += " AND WAREHOUSE_NAME = :warehouse_name "
    sql += " GROUP BY 1,2 ORDER BY 1,2"
 
    df = run_query(sql, base_params)
    if df.empty:
        st.info("No credit usage for selected filters.")
    else:
        st.download_button(
            "⬇️ Download CSV (Credits)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"credit_usage_{start_date}_to_{end_date}.csv",
            mime="text/csv",
        )
        chart = (
            alt.Chart(df)
            .mark_area(opacity=0.7)
            .encode(
                x="USAGE_DATE:T",
                y="sum(DAILY_CREDITS):Q",
                color="WAREHOUSE_NAME:N",
                tooltip=["USAGE_DATE", "WAREHOUSE_NAME", "DAILY_CREDITS", "COMPUTE_CREDITS", "CLOUD_CREDITS"],
            )
        )
        st.altair_chart(chart, use_container_width=True)
 
# ===== Tab 2: Query Performance =====
with tab2:
    sql = """
    SELECT
      DATE_TRUNC('day', START_TIME) AS QUERY_DATE,
      USER_NAME,
      WAREHOUSE_NAME,
      COUNT(*) AS QUERY_COUNT,
      AVG(TOTAL_ELAPSED_TIME/1000) AS AVG_EXEC_SEC,
      AVG(BYTES_SCANNED/1024/1024/1024) AS AVG_SCAN_GB
    FROM QUERY_HISTORY
    WHERE START_TIME >= :start AND START_TIME < :end
    """
    if warehouse_pick != "(All)":
        sql += " AND WAREHOUSE_NAME = :warehouse_name "
    sql += " GROUP BY 1,2,3 ORDER BY 1,2,3"
 
    df = run_query(sql, base_params)
    if df.empty:
        st.info("No query history for selected filters.")
    else:
        st.download_button(
            "⬇️ Download CSV (Query Performance)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"query_performance_{start_date}_to_{end_date}.csv",
            mime="text/csv",
        )
        chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x="QUERY_DATE:T",
                y="AVG_EXEC_SEC:Q",
                color="WAREHOUSE_NAME:N",
                tooltip=["QUERY_DATE", "USER_NAME", "WAREHOUSE_NAME", "AVG_EXEC_SEC", "AVG_SCAN_GB"],
            )
        )
        st.altair_chart(chart, use_container_width=True)
 
# ===== Tab 3: Storage =====
with tab3:
    sql = """
    SELECT
      DATE_TRUNC('day', USAGE_DATE) AS STORAGE_DATE,
      TABLE_CATALOG,
      TABLE_SCHEMA,
      SUM(ACTIVE_BYTES)/1024/1024/1024 AS ACTIVE_GB,
      SUM(TIME_TRAVEL_BYTES)/1024/1024/1024 AS TT_GB,
      SUM(FAILSAFE_BYTES)/1024/1024/1024 AS FS_GB
    FROM TABLE_STORAGE_METRICS
    WHERE USAGE_DATE >= :start AND USAGE_DATE < :end
    GROUP BY 1,2,3 ORDER BY 1,2,3
    """
    df = run_query(sql, base_params)
    if df.empty:
        st.info("No storage metrics for selected filters.")
    else:
        df["TOTAL_GB"] = df[["ACTIVE_GB", "TT_GB", "FS_GB"]].sum(axis=1)
        st.download_button(
            "⬇️ Download CSV (Storage Growth)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"storage_growth_{start_date}_to_{end_date}.csv",
            mime="text/csv",
        )
        chart = (
            alt.Chart(df)
            .mark_area(opacity=0.7)
            .encode(
                x="STORAGE_DATE:T",
                y="sum(TOTAL_GB):Q",
                color="TABLE_SCHEMA:N",
                tooltip=["STORAGE_DATE", "TABLE_CATALOG", "TABLE_SCHEMA", "TOTAL_GB"],
            )
        )
        st.altair_chart(chart, use_container_width=True)
