import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# 1. SETUP SESSION (Browser Emulation)
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

# 3. EXPANDED DATABASE (Grouped by Category)
GROUPS = {
    "Oil Blends": {
        "WTI Crude": "CL=F", "Brent Crude": "BZ=F", "Mars US": "MARS", "Urals": "URL.L", 
        "Murban": "MUR=F", "Western Canadian Select": "WCS", "Dubai Crude": "DUB=F",
        "Tapis Crude": "TAP.L", "Oman Crude": "OQD=F", "Louisiana Light": "LLS",
        "Bonny Light": "BONY.L", "Arab Light": "ARB.L", "Basra Light": "BAS.L"
    },
    "Energy and Gas": {
        "Natural Gas": "NG=F", "Dutch TTF Gas": "TTF=F", "Coal": "MTF=F", "Uranium": "UX=F",
        "Ethanol": "CU=F", "Propane": "PN=F", "Carbon Credits": "CFI=F", "Heating Oil": "HO=F",
        "RBOB Gasoline": "RB=F", "Naphtha": "NPH=F"
    },
    "Precious Metals": {
        "Gold Spot": "GC=F", "Silver Spot": "SI=F", "Platinum": "PL=F", "Palladium": "PA=F"
    },
    "Industrial Metals": {
        "Copper": "HG=F", "Aluminum": "ALI=F", "Nickel": "NICK", "Zinc": "ZNC=F", 
        "Lead": "LED", "Iron Ore": "TIO=F", "Steel": "ST-USD", "Lithium": "LTH-USD"
    },
    "Agriculture": {
        "Wheat": "W=F", "Corn": "C=F", "Soybeans": "S=F", "Coffee": "KC=F", "Sugar": "SB=F",
        "Cocoa": "CC=F", "Cotton": "CT=F", "Oats": "ZO=F", "Rough Rice": "RR=F", "Palm Oil": "PO=F"
    },
    "Pakistan Focus": {
        "KSE 100 Index": "^KSE", "USD/PKR": "PKR=X", "EUR/PKR": "EURPKR=X", "GBP/PKR": "GBPPKR=X",
        "Gold 24K (Local Estimate)": "GC=F"
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
                
                # Custom calculation for Pakistan Gold
                if name == "Gold 24K (Local Estimate)":
                    pkr_rate = yf.Ticker("PKR=X", session=session).history(period="1d")['Close'].iloc[-1]
                    price = (price / 31.103) * 10 * pkr_rate
                
                res.append({"Index": name, "Price": f"{price:,.2f}", "Change %": f"{chg:+.2f}%"})
        except:
            continue
    return res

# 4. INTERFACE
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>GLOBAL ENERGY TERMINAL</h1>", unsafe_allow_html=True)

# TOP METRICS
c1, c2, c3 = st.columns(3)
try:
    gold_val = yf.Ticker("GC=F", session=session).history(period="2d")['Close'].iloc[-1]
    pkr_val = yf.Ticker("PKR=X", session=session).history(period="2d")['Close'].iloc[-1]
    gold_pkr = (gold_val / 31.103) * 10 * pkr_val
    
    c1.metric("BRENT CRUDE", f"${yf.Ticker('BZ=F', session=session).history(period='1d')['Close'].iloc[-1]:.2f}")
    c2.metric("GOLD 10G (PKR)", f"Rs {gold_pkr:,.0f}")
    c3.metric("USD / PKR", f"{pkr_val:.2f}")
except:
    st.write("System Syncing...")

st.markdown("---")

# SEARCHABLE TABS
tabs = st.tabs(list(GROUPS.keys()))

for i, (category, tickers) in enumerate(GROUPS.items()):
    with tabs[i]:
        data = get_group_data(tickers)
        if data:
            st.table(pd.DataFrame(data))
        else:
            st.info(f"Loading {category} data...")

# FOOTER
if st.button('REBOOT TERMINAL'):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')} PKT // Operational")
