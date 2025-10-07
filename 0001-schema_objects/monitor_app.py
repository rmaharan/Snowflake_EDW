import streamlit as st
import pandas as pd
import numpy as np
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import *
from snowflake.snowpark.types import *
import time
import random
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="🚀 Snowflake Platform Monitor",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get Snowflake session
session = get_active_session()

# Custom CSS for colorful UI
st.markdown("""
<style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Snowflake-themed header */
    .snowflake-header {
        background: linear-gradient(90deg, #00d4ff, #0099cc, #006699, #004466);
        background-size: 300% 300%;
        animation: snowflake-gradient 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    @keyframes snowflake-gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Snowflake metric cards */
    .sf-metric-card {
        background: linear-gradient(145deg, #0080bf 0%, #00a3d9 50%, #00c7f2 100%);
        padding: 25px;
        border-radius: 20px;
        border: 2px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(15px);
        color: white;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 12px 40px 0 rgba(0, 128, 191, 0.4);
        transition: transform 0.3s ease;
    }
    
    .sf-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px 0 rgba(0, 128, 191, 0.6);
    }
    
    .sf-metric-value {
        font-size: 3rem;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.7);
        margin: 10px 0;
    }
    
    .sf-metric-label {
        font-size: 1.2rem;
        color: #e6f7ff;
        margin-top: 8px;
        font-weight: 500;
    }
    
    /* Progress bars */
    .progress-container {
        width: 100%;
        background-color: rgba(255,255,255,0.2);
        border-radius: 15px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 25px;
        border-radius: 15px;
        text-align: center;
        line-height: 25px;
        color: white;
        font-weight: bold;
        transition: width 0.5s ease;
    }
    
    .progress-low { background: linear-gradient(90deg, #52c41a, #73d13d); }
    .progress-medium { background: linear-gradient(90deg, #faad14, #ffc53d); }
    .progress-high { background: linear-gradient(90deg, #ff4d4f, #ff7875); }
    
    /* Query type bars - Fixed styling */
    .query-bar-container {
        margin: 8px 0;
        padding: 5px;
        background: rgba(0,212,255,0.1);
        border-radius: 10px;
        border: 1px solid rgba(0,212,255,0.2);
    }
    
    .query-bar {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        height: 35px;
        margin: 2px 0;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        color: white;
        font-weight: bold;
        font-size: 14px;
        min-width: 200px;
        max-width: 100%;
        overflow: hidden;
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    }
    
    .query-name {
        max-width: 65%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 13px;
    }
    
    .query-stats {
        font-size: 12px;
        opacity: 0.95;
        background: rgba(255,255,255,0.2);
        padding: 2px 8px;
        border-radius: 10px;
    }
    
    /* Status indicators */
    .status-healthy {
        color: #52c41a;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(82, 196, 26, 0.6);
    }
    
    .status-warning {
        color: #faad14;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(250, 173, 20, 0.6);
    }
    
    .status-critical {
        color: #ff4d4f;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 77, 79, 0.6);
    }
    
    /* Snowflake alerts */
    .sf-alert-success {
        background: linear-gradient(90deg, #52c41a, #73d13d);
        color: white;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #389e0d;
    }
    
    .sf-alert-warning {
        background: linear-gradient(90deg, #faad14, #ffc53d);
        color: white;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #d48806;
    }
    
    .sf-alert-critical {
        background: linear-gradient(90deg, #ff4d4f, #ff7875);
        color: white;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #cf1322;
        animation: critical-pulse 2s infinite;
    }
    
    @keyframes critical-pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
    }
    
    /* Snowflake branding */
    .sf-brand {
        color: #00d4ff;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)
