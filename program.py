import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Global Energy Terminal", layout="wide")

# 2. Executive Noir CSS (Updated for clean vertical layout)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #000000 !important; font-family: 'JetBrains Mono', monospace !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'JetBrains Mono', monospace !important; }
    
    /* Metric Styling */
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #00FF00 !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; font-size: 12px; }
    
    /* Table Styling */
    .stTable { background-color: #000 !important; border: 1px solid #333 !important; }
    
    /* Clean Up UI */
    header, footer, #MainMenu {visibility: hidden;}
    hr { border: 0; border-top: 1px solid #333; margin: 20px 0; }
    
    /* Subheader spacing */
    .stSubheader { margin-top: 2rem !important; border-left: 4px solid #00FF00; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Categorized Database
MARKET_DATABASE = {
    "Global Benchmarks": {
        "Brent Crude (ICE)": "BZ=F",
        "WTI Crude (NYMEX)": "CL=F",
        "Natural Gas (HH)": "NG=F",
        "Gold (Spot)": "GC=F",
    },
    "Refined Products": {
        "RBOB Gasoline": "RB=F",
        "Heating Oil": "HO=F",
        "Ethanol": "CU=F",
        "Coal (Rotterdam)": "MTF=F"
    },
    "Regional & Currency": {
        "KSE 100 (Pakistan)": "^KSE",
        "USD/PKR Exchange": "PKR=X",
        "Murban Crude": "MUR=F",
        "S&P 500": "^GSPC"
    }
}

@st.cache_data(ttl=300)
def fetch_group_data(category_dict):
    results = []
    for name, sym in category_dict.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                price = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = ((price - prev) / prev) * 100
                results.append({
                    "Market/Index": name,
                    "Price": f"{price:,.2f}",
                    "Change %": f"{change:+.2f}%"
                })
        except:
            continue
    return results

def get_single_price(symbol):
    try:
        data = yf.Ticker(symbol).history(period="2d")
        return data['Close'].iloc[-1] if not data.empty else None
    except:
        return None

# 4. Main Interface Header
st.markdown("<h1 style='text-align: center; letter-spacing: 10px; margin-bottom: 0;'>TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #444 !important; font-size: 12px;'>REAL-TIME ENERGY & CURRENCY MONITOR</p>", unsafe_allow_html=True)
st.markdown("---")

# 5. Featured Metrics Bar
m1, m2, m3 = st.columns(3)

# Brent Crude Metric
brent_val = get_single_price("BZ=F")
if brent_val:
    m1.metric("BRENT CRUDE", f"${brent_val:.2f}")
else:
    m1.metric("BRENT CRUDE", "OFFLINE")

# Gold 10G PKR Metric
gold_usd = get_single_price("GC=F")
pkr_rate = get_single_price("PKR=X")
if gold_usd and pkr_rate:
    gold_pkr_10g = (gold_usd / 31.103) * 10 * pkr_rate
    m2.metric("GOLD (10G PKR)", f"Rs {gold_pkr_10g:,.0f}")
else:
    m2.metric("GOLD (10G PKR)", "DATA ERROR")

# USD/PKR Metric
if pkr_rate:
    m3.metric("USD / PKR", f"{pkr_rate:.2f}")
else:
    m3.metric("USD / PKR", "OFFLINE")

st.markdown("---")

# 6. Data Tables (Vertical Stack - No Tabs)
def color_changes(val):
    if not isinstance(val, str): return ""
    color = '#00FF00' if '+' in val else '#FF3333'
    return f'color: {color}'

for category, data_dict in MARKET_DATABASE.items():
    st.subheader(category.upper())
    raw_data = fetch_group_data(data_dict)
    
    if raw_data:
        df = pd.DataFrame(raw_data)
        # Handle Pandas version differences for styling
        try:
            styled_df = df.style.map(color_changes, subset=['Change %'])
        except AttributeError:
            styled_df = df.style.applymap(color_changes, subset=['Change %'])
            
        st.table(styled_df)
    else:
        st.info(f"Awaiting data for {category}...")
    st.markdown("<br>", unsafe_allow_html=True)

# 7. Sidebar Control
with st.sidebar:
    st.markdown("### TERMINAL STATUS")
    if st.button('FORCE SYNC', use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("Feed: Yahoo Finance")
