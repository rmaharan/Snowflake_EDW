from snowflake.snowpark.context import get_active_session
import pandas as pd
import streamlit as st
import altair as alt
import numpy as np

st.title('Top n longest-running queries')

# Input widgets
col = st.columns(3)

with col[0]:
    timeframe_option = st.selectbox('Select a timeframe', ('day', 'week', 'month'))

with col[1]:
    limit_option = st.slider('Display n rows', 10, 200, 100)

with col[2]:
    bin_option = st.slider('Bin size', 1, 30, 10)

    # Data retrieval
session = get_active_session()
df = session.sql(
    f"""
    SELECT query_id,
      ROW_NUMBER() OVER(ORDER BY partitions_scanned DESC) AS query_id_int,
      query_text,
      total_elapsed_time/1000 AS query_execution_time_seconds,
      partitions_scanned,
      partitions_total,
    FROM snowflake.account_usage.query_history Q
    WHERE warehouse_name = 'DEV_ENT_ELT_WHS' AND TO_DATE(Q.start_time) > DATEADD({timeframe_option},-1,TO_DATE(CURRENT_TIMESTAMP()))
      AND total_elapsed_time > 0 --only get queries that actually used compute
      AND error_code IS NULL
      AND partitions_scanned IS NOT NULL
    ORDER BY total_elapsed_time desc
    LIMIT {limit_option};
    """
    ).to_pandas()



st.title('Histogram of Query Execution Times')

# Create a DataFrame for the histogram data
hist, bin_edges = np.histogram(df['QUERY_EXECUTION_TIME_SECONDS'], bins=bin_option)

histogram_df = pd.DataFrame({
    'bin_start': bin_edges[:-1],
    'bin_end': bin_edges[1:],
    'count': hist
})
histogram_df['bin_label'] = histogram_df.apply(lambda row: f"{row['bin_start']:.2f} - {row['bin_end']:.2f}", axis=1)

# Create plots
histogram_plot = alt.Chart(histogram_df).mark_bar().encode(
    x=alt.X('bin_label:N', sort=histogram_df['bin_label'].tolist(),
            axis=alt.Axis(title='QUERY_EXECUTION_TIME_SECONDS', labelAngle=90)),
    y=alt.Y('count:Q', axis=alt.Axis(title='Count')),
    tooltip=['bin_label', 'count']
)

box_plot = alt.Chart(df).mark_boxplot(
    extent="min-max",
    color='yellow'
).encode(
    alt.X("QUERY_EXECUTION_TIME_SECONDS:Q", scale=alt.Scale(zero=False))
).properties(
    height=200
)

st.altair_chart(histogram_plot, use_container_width=True)
st.altair_chart(box_plot, use_container_width=True)


# Data display
with st.expander('Show data'):
    st.dataframe(df)
with st.expander('Show summary statistics'):
    st.write(df['QUERY_EXECUTION_TIME_SECONDS'].describe())
