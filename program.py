import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Global Energy Terminal", layout="wide")

# 2. Executive Noir CSS (Updated with Monospace fonts and better table styling)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #000000 !important; font-family: 'JetBrains Mono', monospace !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'JetBrains Mono', monospace !important; }
    
    /* Metric Styling */
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #00FF00 !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; font-size: 12px; }
    
    /* Clean Up UI */
    header, footer, #MainMenu {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { gap: 20px; background-color: #000; }
    .stTabs [data-baseweb="tab"] { height: 50px; color: #888; border-bottom: 2px solid #333; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #00FF00; }
    
    /* Horizontal Rule */
    hr { border: 0; border-top: 1px solid #333; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. Enhanced Database (Corrected Tickers)
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
    "Regional/Local": {
        "KSE 100 (Pakistan)": "^KSE",
        "USD/PKR Exchange": "PKR=X",
        "Murban Crude": "MUR=F",
        "S&P 500": "^GSPC"
    }
}

@st.cache_data(ttl=300) # 5-minute cache
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
        except Exception:
            continue
    return results

# 4. Header
st.markdown("<h1 style='text-align: center; letter-spacing: 10px; margin-bottom: 0;'>TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #444 !important; font-size: 12px;'>REAL-TIME ENERGY & CURRENCY MONITOR</p>", unsafe_allow_html=True)
st.markdown("---")

# 5. Top Metric Bar (Hardened Logic)
m1, m2, m3 = st.columns(3)

def get_metric_data(symbol):
    try:
        data = yf.Ticker(symbol).history(period="2d")
        return data['Close'].iloc[-1] if not data.empty else None
    except:
        return None

# Brent
brent_val = get_metric_data("BZ=F")
if brent_val:
    m1.metric("BRENT CRUDE", f"${brent_val:.2f}")

# Gold in PKR (10 Grams)
gold_usd = get_metric_data("GC=F")
pkr_rate = get_metric_data("PKR=X")
if gold_usd and pkr_rate:
    # 1 Troy Oz = 31.103 grams. (Gold price / 31.103) * 10 * PKR rate
    gold_pkr_10g = (gold_usd / 31.103) * 10 * pkr_rate
    m2.metric("GOLD (10G PKR)", f"Rs {gold_pkr_10g:,.0f}")

# USD/PKR
if pkr_rate:
    m3.metric("USD / PKR", f"{pkr_rate:.2f}")

st.markdown("---")

# 6. Tables with Conditional Formatting
tabs = st.tabs(list(MARKET_DATABASE.keys()))

for i, (category, data_dict) in enumerate(MARKET_DATABASE.items()):
    with tabs[i]:
        raw_data = fetch_group_data(data_dict)
        if raw_data:
            df = pd.DataFrame(raw_data)
            
            # Helper to color the "Change %" column
            def color_changes(val):
                color = '#00FF00' if '+' in val else '#FF3333'
                return f'color: {color}'

            # Displaying a styled table
            st.table(df.style.applymap(color_changes, subset=['Change %']))
        else:
            st.error(f"Unable to reach {category} data stream.")

# 7. Sidebar Info
with st.sidebar:
    st.markdown("### SYSTEM CONTROL")
    if st.button('FORCE DATA REFRESH', use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption(f"Network Status: CONNECTED")
    st.caption(f"Internal Clock: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("Data provided by Yahoo Finance")
