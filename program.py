import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# 1. ANTI-BLOCK SESSION
# This makes Yahoo think a human is browsing from a Windows PC
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# 2. Page Config & Style
st.set_page_config(page_title="Executive Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label, .stDataFrame { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #00FF00 !important; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { 
        background-color: #222 !important; color: #ffffff !important; 
        border-radius: 4px !important; width: 100% !important; border: 1px solid #444 !important;
    }
    header, footer, #MainMenu {visibility: hidden;}
    hr { border-top: 1px solid #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. The Index Database
COMMODITY_DICT = {
    "WTI Crude": "CL=F", "Brent Crude": "BZ=F", "Natural Gas": "NG=F", "Heating Oil": "HO=F",
    "Gold Spot": "GC=F", "Silver Spot": "SI=F", "Copper": "HG=F", "Iron Ore": "TIO=F",
    "Wheat": "W=F", "Corn": "C=F", "Soybeans": "S=F", "Coffee": "KC=F", "Sugar": "SB=F",
    "US Dollar Index": "DX=F", "Bitcoin": "BTC-USD", "10Y Treasury": "^TNX"
}

@st.cache_data(ttl=600) # Cache for 10 mins to avoid spamming Yahoo
def fetch_safe_data(tickers):
    data_list = []
    for name, sym in tickers.items():
        try:
            # Pass the fake browser session here
            t = yf.Ticker(sym, session=session)
            hist = t.history(period="5d")
            if not hist.empty:
                last_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                pct_chg = ((last_price - prev_price) / prev_price) * 100
                data_list.append({
                    "INDEX": name,
                    "PRICE (USD)": f"{last_price:,.2f}",
                    "DAY CHG %": f"{pct_chg:+.2f}%"
                })
        except Exception:
            # If one fails, we skip it instead of crashing the app
            continue
    return data_list

# 4. Interface
st.markdown("<h1 style='text-align: center; letter-spacing: 10px;'>EXECUTIVE TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("---")

# FEATURED TOP BAR
c1, c2, c3 = st.columns(3)
featured = {"BRENT": "BZ=F", "GOLD": "GC=F", "NAT GAS": "NG=F"}

for col, (label, sym) in zip([c1, c2, c3], featured.items()):
    try:
        val = yf.Ticker(sym, session=session).history(period="2d")['Close']
        col.metric(label, f"${val.iloc[-1]:.2f}", f"{((val.iloc[-1]-val.iloc[-2])/val.iloc[-2]*100):+.2f}%")
    except:
        col.metric(label, "OFFLINE")

st.markdown("---")

# FULL LIST
st.subheader("GLOBAL MARKET INDEX
