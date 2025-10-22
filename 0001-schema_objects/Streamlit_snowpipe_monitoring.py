import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import plotly.express as px

session = get_active_session()
# Main header

st.title("❄️Snowflake Snowpipe Monitor")

# Example: Fetching Snowpipe usage history
snowpipe_data = session.sql("""
    SELECT
        PIPE_NAME,
        START_TIME,
        END_TIME,
        FILES_INSERTED,
        BYTES_INSERTED
    FROM
        SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
    ORDER BY
        START_TIME DESC
""").to_pandas()

currentdate_snowpipe_data = session.sql("""
      SELECT PIPE_NAME,
        PIPE_RECEIVED_TIME,
        TABLE_SCHEMA_NAME,
        TABLE_NAME,
        STATUS,
        LAST_LOAD_TIME,
        FILE_NAME,
        ROW_COUNT,
        ROW_PARSED
        FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
        WHERE PIPE_RECEIVED_TIME=CURRENT_DATE()
""").to_pandas()

# Add interactive filters (e.g., date range)
start_date = st.date_input("Start Date", value=snowpipe_data['START_TIME'].min())
end_date = st.date_input("End Date", value=snowpipe_data['START_TIME'].max())

filtered_data = snowpipe_data[
    (snowpipe_data['START_TIME'].dt.date >= start_date) &
    (snowpipe_data['START_TIME'].dt.date <= end_date)
]

    # Visualizations in tabs
tab1, tab2, tab3= st.tabs([
        "Detailed Snowpipe History", 
        "Current Snowpipe status", 
        "Failed Snowpipes"
    ])
# Display key metrics
with tab1:
 st.subheader("Overall Snowpipe Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Files Inserted", filtered_data['FILES_INSERTED'].sum())
col3.metric("Total Bytes Inserted (GB)", round(filtered_data['BYTES_INSERTED'].sum() / (1024**3), 2))

# Visualize data
st.subheader("Snowpipe Activity Over Time")
fig = px.line(filtered_data, x='START_TIME', y='FILES_INSERTED', color='PIPE_NAME', title='Files Inserted by Snowpipe')
st.plotly_chart(fig)

st.subheader("Detailed Snowpipe History")
st.dataframe(filtered_data)

with tab2:
 st.subheader("Current Snowpipe status")
 filtered_data1 = currentdate_snowpipe_data
st.dataframe(filtered_data1)


with tab3:
 st.subheader("Overall Snowpipe Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Files Inserted", filtered_data['FILES_INSERTED'].sum())
col3.metric("Total Bytes Inserted (GB)", round(filtered_data['BYTES_INSERTED'].sum() / (1024**3), 2))

# Visualize data
st.subheader("Snowpipe Activity Over Time")
fig = px.line(filtered_data, x='START_TIME', y='FILES_INSERTED', color='PIPE_NAME', title='Files Inserted by Snowpipe')
st.plotly_chart(fig)

st.subheader("Detailed Snowpipe History")
st.dataframe(filtered_data)
