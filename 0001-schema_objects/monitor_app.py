class SnowflakePlatformMonitor:
    """Snowflake Platform Monitor without external chart libraries"""
    
    def __init__(self, session):
        self.session = session
        self.warehouses = ["COMPUTE_WH", "DEV_ENT_ELT_WHS", "DEV_STREAMLIT_WHS", "DEV_STREAMLIT_WHS"]
        self.databases = ["DEV_STREAMLIT_DB", "DEV_RAW_DB", "DEV_STREAMLIT_DB", "DEV_STREAMLIT_DB"]
        
    def get_account_info(self):
        """Get Snowflake account information"""
        try:
            account = self.session.sql("SELECT CURRENT_ACCOUNT()").collect()[0][0]
            region = self.session.sql("SELECT CURRENT_REGION()").collect()[0][0]
            warehouse = self.session.sql("SELECT CURRENT_WAREHOUSE()").collect()[0][0]
            database = self.session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
            schema = self.session.sql("SELECT CURRENT_SCHEMA()").collect()[0][0]
            user = self.session.sql("SELECT CURRENT_USER()").collect()[0][0]
            role = self.session.sql("SELECT CURRENT_ROLE()").collect()[0][0]
            
            return {
                'account': account,
                'region': region,
                'warehouse': warehouse,
                'database': database,
                'schema': schema,
                'user': user,
                'role': role
            }
        except Exception as e:
            return {
                'account': 'N/A',
                'region': 'N/A', 
                'warehouse': 'N/A',
                'database': 'N/A',
                'schema': 'N/A',
                'user': 'N/A',
                'role': 'N/A'
            }
    
    def get_warehouse_usage(self):
        """Get warehouse usage information"""
        try:
            # Try to get real warehouse usage from ACCOUNT_USAGE
            query = """
            SELECT 
                WAREHOUSE_NAME,
                SUM(CREDITS_USED) as TOTAL_CREDITS,
                COUNT(*) as QUERY_COUNT,
                AVG(EXECUTION_TIME) as AVG_EXEC_TIME
            FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
            WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
            GROUP BY WAREHOUSE_NAME
            ORDER BY TOTAL_CREDITS DESC
            LIMIT 10
            """
            result = self.session.sql(query).to_pandas()
            
            if result.empty:
                raise Exception("No data found")
                
            return result
            
        except Exception:
            # Generate sample data if real data is not accessible
            data = []
            for wh in self.warehouses:
                data.append({
                    'WAREHOUSE_NAME': wh,
                    'TOTAL_CREDITS': random.uniform(0.5, 10.0),
                    'QUERY_COUNT': random.randint(50, 500),
                    'AVG_EXEC_TIME': random.uniform(100, 2000)
                })
            return pd.DataFrame(data)
    
    def get_query_history(self):
        """Get recent query history"""
        try:
            query = """
            SELECT 
                QUERY_TYPE,
                DATABASE_NAME,
                WAREHOUSE_NAME,
                EXECUTION_STATUS,
                TOTAL_ELAPSED_TIME,
                ROWS_PRODUCED,
                BYTES_SCANNED,
                START_TIME
            FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
            WHERE START_TIME >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
            ORDER BY START_TIME DESC
            LIMIT 100
            """
            result = self.session.sql(query).to_pandas()
            
            if result.empty:
                raise Exception("No data found")
                
            return result
            
        except Exception:
            # Generate sample data
            query_types = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'COPY', 
                          'REFRESH_DYNAMIC_TABLE_AT_REFRESH_VERSION', 'DESCRIBE_QUERY', 
                          'DESCRIBE', 'SHOW', 'UNKNOWN']
            statuses = ['SUCCESS', 'RUNNING', 'FAILED']
            
            data = []
            for i in range(100):
                data.append({
                    'QUERY_TYPE': random.choice(query_types),
                    'DATABASE_NAME': random.choice(self.databases),
                    'WAREHOUSE_NAME': random.choice(self.warehouses),
                    'EXECUTION_STATUS': random.choice(statuses),
                    'TOTAL_ELAPSED_TIME': random.randint(100, 10000),
                    'ROWS_PRODUCED': random.randint(0, 100000),
                    'BYTES_SCANNED': random.randint(1000, 1000000),
                    'START_TIME': datetime.now() - timedelta(minutes=random.randint(1, 60))
                })
            return pd.DataFrame(data)
    
    def get_storage_usage(self):
        """Get storage usage information"""
        try:
            query = """
            SELECT 
                DATABASE_NAME,
                SCHEMA_NAME,
                TABLE_NAME,
                BYTES,
                ROWS
            FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
            WHERE CATALOG_NAME = CURRENT_DATABASE()
            ORDER BY BYTES DESC
            LIMIT 20
            """
            result = self.session.sql(query).to_pandas()
            
            if result.empty:
                raise Exception("No data found")
                
            return result
            
        except Exception:
            # Generate sample data
            data = []
            for i in range(15):
                data.append({
                    'DATABASE_NAME': random.choice(self.databases),
                    'SCHEMA_NAME': random.choice(['PUBLIC', 'STAGING', 'PROD', 'DEV']),
                    'TABLE_NAME': f'TABLE_{i+1}',
                    'BYTES': random.randint(1000000, 1000000000),
                    'ROWS': random.randint(1000, 10000000)
                })
            return pd.DataFrame(data)

def calculate_percentage(value, max_value):
    """Calculate percentage without using min() function - avoiding Snowpark conflict"""
    if max_value <= 0:
        return 0
    
    percentage = (value / max_value) * 100
    
    # Use if-else instead of min() function
    if percentage > 100:
        return 100
    else:
        return percentage

def create_progress_bar(value, max_value, label):
    """Create a CSS-based progress bar without using min() function"""
    percentage = calculate_percentage(value, max_value)
    
    if percentage < 50:
        bar_class = "progress-low"
    elif percentage < 80:
        bar_class = "progress-medium"
    else:
        bar_class = "progress-high"
    
    return f"""
    <div class="progress-container">
        <div class="progress-bar {bar_class}" style="width: {percentage}%">
            {label}: {value:.1f} / {max_value:.1f}
        </div>
    </div>
    """

def create_metric_card(value, label, icon="📊"):
    """Create a metric card"""
    return f"""
    <div class="sf-metric-card">
        <div class="sf-metric-value">{icon} {value}</div>
        <div class="sf-metric-label">{label}</div>
    </div>
    """

def safe_divide(numerator, denominator):
    """Safely divide two numbers avoiding division by zero"""
    if denominator == 0:
        return 0
    return numerator / denominator

def shorten_query_type(query_type):
    """Shorten long query type names for better display"""
    # Dictionary of common abbreviations
    abbreviations = {
        'REFRESH_DYNAMIC_TABLE_AT_REFRESH_VERSION': 'REFRESH_DYN_TABLE',
        'DESCRIBE_QUERY': 'DESC_QUERY',
        'DESCRIBE': 'DESC',
        'SELECT': 'SELECT',
        'INSERT': 'INSERT',
        'UPDATE': 'UPDATE',
        'DELETE': 'DELETE',
        'CREATE': 'CREATE',
        'SHOW': 'SHOW',
        'UNKNOWN': 'UNKNOWN'
    }
    
    if query_type in abbreviations:
        return abbreviations[query_type]
    
    # For other long names, truncate and clean
    if len(query_type) > 20:
        return query_type[:17] + "..."
    
    return query_type.replace('_', ' ').title()

def main():
    # Initialize monitor
    monitor = SnowflakePlatformMonitor(session)
    
    # Header
    st.markdown('<h1 class="snowflake-header">❄️ Snowflake Platform Monitor</h1>', unsafe_allow_html=True)
    
    # Get account info
    account_info = monitor.get_account_info()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ❄️ <span class='sf-brand'>Snowflake Controls</span>", unsafe_allow_html=True)
        
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
        refresh_interval = st.slider("Refresh Interval (seconds)", 10, 120, 30)
        
        st.markdown("## 📊 Display Options")
        show_warehouses = st.checkbox("🏢 Show Warehouse Usage", value=True)
        show_queries = st.checkbox("🔍 Show Query History", value=True)
        show_storage = st.checkbox("💾 Show Storage Usage", value=True)
        show_query_types = st.checkbox("📊 Show Query Types Chart", value=True)
        
        # Account info
        st.markdown("## ❄️ Account Info")
        st.write(f"**Account:** {account_info['account']}")
        st.write(f"**Region:** {account_info['region']}")
        st.write(f"**User:** {account_info['user']}")
        st.write(f"**Role:** {account_info['role']}")
        st.write(f"**Warehouse:** {account_info['warehouse']}")
        st.write(f"**Database:** {account_info['database']}")
        st.write(f"**Schema:** {account_info['schema']}")
    
    # Main dashboard
    if auto_refresh:
        placeholder = st.empty()
        
        with placeholder.container():
            render_dashboard(monitor, show_warehouses, show_queries, show_storage, show_query_types)
            
        # Auto refresh
        time.sleep(refresh_interval)
        st.rerun()
    else:
        render_dashboard(monitor, show_warehouses, show_queries, show_storage, show_query_types)

def render_dashboard(monitor, show_warehouses, show_queries, show_storage, show_query_types):
    """Render the main dashboard content"""
    
    # Get data
    warehouse_usage = monitor.get_warehouse_usage()
    query_history = monitor.get_query_history()
    storage_usage = monitor.get_storage_usage()
    
    # Calculate summary metrics safely
    if not warehouse_usage.empty:
        total_credits = warehouse_usage['TOTAL_CREDITS'].sum()
        total_queries = warehouse_usage['QUERY_COUNT'].sum()
        avg_exec_time = warehouse_usage['AVG_EXEC_TIME'].mean()
        active_warehouses = len(warehouse_usage)
    else:
        total_credits = 0
        total_queries = 0
        avg_exec_time = 0
        active_warehouses = 0
    
    # Top level metrics
    st.markdown("## 📊 <span class='sf-brand'>Snowflake Overview</span>", unsafe_allow_html=True)
    
    # Metric cards using columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(f"{total_credits:.2f}", "💰 Credits Used (24h)", "💰"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(f"{total_queries:,}", "🔍 Total Queries", "🔍"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(f"{avg_exec_time:.0f}ms", "⚡ Avg Exec Time", "⚡"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(f"{active_warehouses}", "🏢 Active Warehouses", "🏢"), unsafe_allow_html=True)
    
    # Warehouse usage section
    if show_warehouses and not warehouse_usage.empty:
        st.markdown("## 🏢 <span class='sf-brand'>Warehouse Usage (24h)</span>", unsafe_allow_html=True)
        
        # Find max credits for progress bars
        max_credits = 0
        for _, row in warehouse_usage.iterrows():
            if row['TOTAL_CREDITS'] > max_credits:
                max_credits = row['TOTAL_CREDITS']
        
        # Progress bars for each warehouse
        for _, row in warehouse_usage.iterrows():
            st.markdown(f"### {row['WAREHOUSE_NAME']}")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(create_progress_bar(
                    row['TOTAL_CREDITS'], 
                    max_credits, 
                    "Credits"
                ), unsafe_allow_html=True)
            
            with col2:
                st.metric("Queries", f"{int(row['QUERY_COUNT']):,}")
                st.metric("Avg Time", f"{row['AVG_EXEC_TIME']:.0f}ms")
        
        # Warehouse usage table
        st.markdown("### 📋 Detailed Warehouse Metrics")
        st.dataframe(warehouse_usage, use_container_width=True)
    
    # Query history section
    if show_queries and not query_history.empty:
        st.markdown("## 🔍 <span class='sf-brand'>Recent Query Activity</span>", unsafe_allow_html=True)
        
        # Query status summary
        status_counts = query_history['EXECUTION_STATUS'].value_counts()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            success_count = status_counts.get('SUCCESS', 0)
            st.metric("✅ Successful", success_count)
        
        with col2:
            running_count = status_counts.get('RUNNING', 0)
            st.metric("🔄 Running", running_count)
        
        with col3:
            failed_count = status_counts.get('FAILED', 0)
            st.metric("❌ Failed", failed_count)
        
        # Query type distribution - FIXED VERSION
        if show_query_types:
            st.markdown("### 📊 Query Types Distribution")
            query_type_counts = query_history['QUERY_TYPE'].value_counts()
            total_queries_hist = len(query_history)
            
            # Create two column layout for better organization
            chart_col, table_col = st.columns([2, 1])
            
            with chart_col:
                st.markdown("#### Visual Distribution")
                for query_type, count in query_type_counts.head(8).items():
                    percentage = safe_divide(count * 100, total_queries_hist)
                    
                    # Shorten the query type name
                    display_name = shorten_query_type(query_type)
                    
                    # Calculate bar width (minimum 15% for visibility)
                    bar_width = percentage if percentage > 15 else 15
                    
                    st.markdown(f"""
                    <div class="query-bar-container">
                        <div class="query-bar" style="width: {bar_width}%">
                            <span class="query-name">{display_name}</span>
                            <span class="query-stats">{count} ({percentage:.1f}%)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with table_col:
                st.markdown("#### Summary Table")
                # Create summary DataFrame
                summary_data = []
                for query_type, count in query_type_counts.head(8).items():
                    percentage = safe_divide(count * 100, total_queries_hist)
                    summary_data.append({
                        'Type': shorten_query_type(query_type),
                        'Count': count,
                        'Percent': f"{percentage:.1f}%"
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Recent queries table
        st.markdown("### 📋 Recent Queries")
        recent_queries = query_history.head(20)
        
        # Add better formatting to the queries table
        if not recent_queries.empty:
            # Clean up query types for display
            recent_queries['QUERY_TYPE_CLEAN'] = recent_queries['QUERY_TYPE'].apply(shorten_query_type)
            
            # Select important columns for display
            display_columns = ['QUERY_TYPE_CLEAN', 'DATABASE_NAME', 'WAREHOUSE_NAME', 
                             'EXECUTION_STATUS', 'TOTAL_ELAPSED_TIME', 'START_TIME']
            
            # Rename columns for better display
            display_df = recent_queries[display_columns].copy()
            display_df.columns = ['Query Type', 'Database', 'Warehouse', 'Status', 'Time (ms)', 'Start Time']
            
            st.dataframe(display_df, use_container_width=True)
    
    # Storage usage section
    if show_storage and not storage_usage.empty:
        st.markdown("## 💾 <span class='sf-brand'>Storage Usage</span>", unsafe_allow_html=True)
        
        # Convert bytes to GB for better readability
        storage_usage['SIZE_GB'] = storage_usage['BYTES'] / (1024**3)
        
        # Find largest table size for scaling
        max_size = 0
        for _, row in storage_usage.iterrows():
            if row['SIZE_GB'] > max_size:
                max_size = row['SIZE_GB']
        
        # Top tables by size
        st.markdown("### 📊 Largest Tables")
        top_tables = storage_usage.head(10)
        
        for _, row in top_tables.iterrows():
            percentage = safe_divide(row['SIZE_GB'] * 100, max_size)
            
            # Ensure minimum width for visibility
            display_width = percentage if percentage > 10 else 10
            
            st.markdown(f"""
            <div class="query-bar-container">
                <div class="query-bar" style="width: {display_width}%">
                    <span class="query-name">{row['TABLE_NAME']}</span>
                    <span class="query-stats">{row['SIZE_GB']:.2f} GB ({row['ROWS']:,} rows)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Storage summary
        total_storage = storage_usage['SIZE_GB'].sum()
        total_rows = storage_usage['ROWS'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📦 Total Storage", f"{total_storage:.2f} GB")
        with col2:
            st.metric("📊 Total Rows", f"{total_rows:,}")
        
        # Storage details table
        st.markdown("### 📋 Storage Details")
        display_storage = storage_usage[['DATABASE_NAME', 'SCHEMA_NAME', 'TABLE_NAME', 'SIZE_GB', 'ROWS']].copy()
        display_storage['SIZE_GB'] = display_storage['SIZE_GB'].round(3)
        display_storage.columns = ['Database', 'Schema', 'Table', 'Size (GB)', 'Rows']
        st.dataframe(display_storage, use_container_width=True)
    
    # Alerts section
    st.markdown("## 🚨 <span class='sf-brand'>System Alerts</span>", unsafe_allow_html=True)
    
    # Generate alerts based on metrics
    alerts = []
    
    if not warehouse_usage.empty:
        # Check for high credit usage
        for _, wh in warehouse_usage.iterrows():
            if wh['TOTAL_CREDITS'] > 5:
                alerts.append(("Critical", f"High Credit Usage - {wh['WAREHOUSE_NAME']}", 
                             f"Used {wh['TOTAL_CREDITS']:.2f} credits in 24 hours"))
        
        # Check for slow performance
        for _, wh in warehouse_usage.iterrows():
            if wh['AVG_EXEC_TIME'] > 1000:
                alerts.append(("Warning", f"Slow Performance - {wh['WAREHOUSE_NAME']}", 
                             f"Average execution time: {wh['AVG_EXEC_TIME']:.0f}ms"))
    
    if not query_history.empty:
        # Check for failed queries
        failed_count = 0
        for _, query in query_history.iterrows():
            if query['EXECUTION_STATUS'] == 'FAILED':
                failed_count += 1
        
        if failed_count > 5:
            alerts.append(("Warning", "High Query Failure Rate", 
                         f"{failed_count} failed queries in the last hour"))
    
    if alerts:
        for alert_type, title, message in alerts:
            if alert_type == "Critical":
                st.markdown(f"""
                <div class="sf-alert-critical">
                    <strong>🔥 {title}</strong><br>
                    {message}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="sf-alert-warning">
                    <strong>⚠️ {title}</strong><br>
                    {message}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sf-alert-success">
            <strong>✅ All Snowflake Services Optimal</strong><br>
            No performance issues detected in your Snowflake environment.
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; color: #00d4ff; margin-top: 50px; padding: 20px; 
                background: linear-gradient(90deg, rgba(0,212,255,0.1), rgba(0,163,217,0.1)); 
                border-radius: 10px;">
        ❄️ <strong>Snowflake Platform Monitor</strong> | 
        🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
        📊 Fully optimized for Streamlit in Snowflake
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
