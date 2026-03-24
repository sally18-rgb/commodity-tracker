import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Executive Terminal", layout="wide")

# 2. Noir Style CSS
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { font-size: 38px !important; color: #00FF00 !important; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { 
        background-color: #ffffff !important; color: #000000 !important; 
        border-radius: 0px !important; width: 100% !important; font-weight: bold !important;
    }
    header, footer, #MainMenu {visibility: hidden;}
    hr { border-top: 1px solid #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Core Commodity Data
@st.cache_data(ttl=300)
def get_core_data():
    # Focused list of high-liquidity indices
    core_assets = {
        "WTI Crude": "CL=F",
        "Brent Crude": "BZ=F",
        "Natural Gas": "NG=F",
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Copper": "HG=F",
        "US Dollar Index": "DX=F",
        "Bitcoin": "BTC-USD"
    }
    
    results = []
    for name, sym in core_assets.items():
        try:
            data = yf.Ticker(sym).history(period="2d")
            if not data.empty:
                price = data['Close'].iloc[-1]
                change = ((price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                results.append({"Commodity": name, "Price": f"{price:,.2f}", "Change %": f"{change:+.2f}%"})
        except:
            continue
    return results

# 4. Main Interface
st.markdown("<h1 style='text-align: center; letter-spacing: 10px;'>EXECUTIVE TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("---")

# Top Featured Metrics
col1, col2, col3 = st.columns(3)
try:
    with col1:
        oil = yf.Ticker("BZ=F").history(period="2d")['Close']
        st.metric("BRENT", f"${oil.iloc[-1]:.2f}")
    with col2:
        gold = yf.Ticker("GC=F").history(period="2d")['Close']
        st.metric("GOLD", f"${gold.iloc[-1]:.0f}")
    with col3:
        gas = yf.Ticker("NG=F").history(period="2d")['Close']
        st.metric("NAT GAS", f"${gas.iloc[-1]:.2f}")
except:
    st.write("Refreshing data stream...")

st.markdown("---")

# Main Table
st.subheader("MARKET SNAPSHOT")
data_feed = get_core_data()
if data_feed:
    df = pd.DataFrame(data_feed)
    st.table(df)

# Footer
if st.button('REFRESH TERMINAL'):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')} PKT // Operational")
