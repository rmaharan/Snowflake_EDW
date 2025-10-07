import streamlit as st
from snowflake.snowpark.context import get_active_session

# Get the current Snowpark session (if running within Snowflake)
session = get_active_session()

# Or establish a new connection if running locally
# from snowflake.snowpark import Session
# connection_parameters = {
#     "account": "your_account_identifier",
#     "user": "your_user",
#     "password": "your_password",
#     "warehouse": "your_warehouse",
#     "database": "SNOWFLAKE",
#     "schema": "ACCOUNT_USAGE",
#     "role": "ACCOUNTADMIN" # Or a role with access to Account Usage views
# }
# session = Session.builder.configs(connection_parameters).create()

@st.cache_data(ttl=3600) # Cache data for 1 hour to reduce query load
def get_query_performance_data():
    query = """
    SELECT
        QUERY_ID,
        QUERY_TEXT,
        EXECUTION_TIME,
        START_TIME,
        END_TIME,
        WAREHOUSE_NAME,
        USER_NAME
    FROM
        SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE
        START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    ORDER BY
        EXECUTION_TIME DESC
    LIMIT 100;
    """
    return session.sql(query).to_pandas()

query_data = get_query_performance_data()
