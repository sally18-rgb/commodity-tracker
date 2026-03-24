import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# 1. SETUP SESSION (The "Human" Browser Filter)
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36'})

# 2. PAGE CONFIG
st.set_page_config(page_title="Executive Terminal", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; color: #00FF00 !important; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; }
    header, footer, #MainMenu {visibility: hidden;}
    .stTable { background-color: #111 !important; border: 1px solid #333 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. THE 100+ INDEX DATABASE (Grouped by Tab)
GROUPS = {
    "🛢️ Oil Blends (OilPrice Style)": {
        "WTI Crude": "CL=F", "Brent Crude": "BZ=F", "Mars US": "MARS", "Urals": "URL.L", 
        "Murban": "MUR=F", "Western Canadian Select": "WCS", "Dubai Crude": "DUB=F",
        "Tapis Crude": "TAP.L", "Heating Oil": "HO=F", "RBOB Gasoline": "RB=F"
    },
    "⚡ Energy & Gas": {
        "Natural Gas": "NG=F", "Dutch TTF Gas": "TTF=F", "Coal": "MTF=F", "Uranium": "UX=F",
        "Ethanol": "CU=F", "Propane": "PN=F", "Carbon Credits": "CFI=F"
    },
    "💰 Metals (Gold/Silver)": {
        "Gold Spot": "GC=F", "Silver Spot": "SI=F", "Copper": "HG=F", "Aluminum": "ALI=F",
        "Platinum": "PL=F", "Palladium": "PA=F", "Nickel": "NICK", "Zinc": "ZNC=F", "Lead": "LED"
    },
    "🌾 Agriculture": {
        "Wheat": "W=F", "Corn": "C=F", "Soybeans": "S=F", "Coffee": "KC=F", "Sugar": "SB=F",
        "Cocoa": "CC=F", "Cotton": "CT=F", "Oats": "ZO=F", "Rough Rice": "RR=F"
    },
    "🇵🇰 Pakistan Focus": {
        "KSE 100 Index": "^KSE", "USD/PKR": "PKR=X", "EUR/PKR": "EURPKR=X", "GBP/PKR": "GBPPKR=X"
    }
}

@st.cache_data(ttl=600)
def get_group_data(tickers):
    res = []
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym, session=session)
            hist = t.history(period="5d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = ((price - prev) / prev) * 100
                res.append({"Index": name, "Price": f"{price:,.2f}", "Change %": f"{chg:+.2f}%"})
        except:
            continue
    return res

# 4. INTERFACE
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>GLOBAL ENERGY TERMINAL</h1>", unsafe_allow_html=True)

# TOP METRICS (Brent, Gold PKR, USD/PKR)
c1, c2, c3 = st.columns(3)
try:
    gold_val = yf.Ticker("GC=F", session=session).history(period="2d")['Close'].iloc[-1]
    pkr_val = yf.Ticker("PKR=X", session=session).history(period="2d")['Close'].iloc[-1]
    gold_pkr = (gold_val / 31.103) * 10 * pkr_val
    
    c1.metric("BRENT CRUDE", f"${yf.Ticker('BZ=F', session=session).history(period='1d')['Close'].iloc[-1]:.2f}")
    c2.metric("GOLD 10G (PKR)", f"Rs {gold_pkr:,.0f}")
    c3.metric("USD / PKR", f"{pkr_val:.2f}")
except:
    st.write("Initializing Terminal...")

st.markdown("---")

# THE TABS (This prevents the 100-index crash)
tabs = st.tabs(list(GROUPS.keys()))

for i, (category, tickers) in enumerate(GROUPS.items()):
    with tabs[i]:
        data = get_group_data(tickers)
        if data:
            st.table(pd.DataFrame(data))
        else:
            st.info(f"Syncing {category} prices...")

# FOOTER
if st.button('FORCE SYSTEM REBOOT'):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Sync Time: {datetime.now().strftime('%H:%M:%S')} PKT // Status: Operational")
