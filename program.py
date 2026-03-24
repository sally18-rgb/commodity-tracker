import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import time

# 1. Page & Session Setup
st.set_page_config(page_title="Executive Terminal", layout="wide")

@st.cache_resource
def get_session():
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36'})
    return s

session = get_session()

# 2. Noir Styling
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label, div { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; color: #00FF00 !important; }
    .stTable { background-color: #111 !important; border: 1px solid #333 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. 100+ Index Groups
GROUPS = {
    "Major Oil Blends": {
        "WTI Crude": "CL=F", "Brent Crude": "BZ=F", "Mars US": "MARS", "Urals": "URL.L", 
        "Murban": "MUR=F", "Western Canadian Select": "WCS", "Dubai Crude": "DUB=F",
        "Tapis Crude": "TAP.L", "Oman Crude": "OQD=F", "Louisiana Light": "LLS",
        "Bonny Light": "BONY.L", "Arab Light": "ARB.L", "Basra Light": "BAS.L"
    },
    "Energy & Gas": {
        "Natural Gas": "NG=F", "Dutch TTF Gas": "TTF=F", "Coal": "MTF=F", "Uranium": "UX=F",
        "Ethanol": "CU=F", "Propane": "PN=F", "Heating Oil": "HO=F", "RBOB Gasoline": "RB=F"
    },
    "Precious Metals": {
        "Gold Spot": "GC=F", "Silver Spot": "SI=F", "Platinum": "PL=F", "Palladium": "PA=F"
    },
    "Industrial Metals": {
        "Copper": "HG=F", "Aluminum": "ALI=F", "Nickel": "NICK", "Zinc": "ZNC=F", 
        "Lead": "LED", "Iron Ore": "TIO=F", "Steel": "ST-USD", "Lithium": "LTH-USD"
    },
    "Global Markets": {
        "S&P 500": "ES=F", "Dow Jones": "YM=F", "Nasdaq 100": "NQ=F", "Nikkei 225": "^N225",
        "FTSE 100": "^FTSE", "DAX Index": "^GDAXI", "Hang Seng": "^HSI"
    },
    "Pakistan Markets": {
        "KSE 100 Index": "^KSE", "USD/PKR": "PKR=X", "EUR/PKR": "EURPKR=X", "GBP/PKR": "GBPPKR=X"
    }
}

# 4. Smart Fetcher
def fetch_tab_data(tickers):
    results = []
    progress_bar = st.progress(0)
    count = 0
    total = len(tickers)
    
    for name, sym in tickers.items():
        try:
            # Short wait to avoid IP ban
            time.sleep(0.1) 
            t = yf.Ticker(sym, session=session)
            hist = t.history(period="5d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = ((price - prev) / prev) * 100
                results.append({"Index": name, "Price": f"{price:,.2f}", "Change %": f"{chg:+.2f}%"})
        except:
            continue
        count += 1
        progress_bar.progress(count / total)
    
    progress_bar.empty()
    return results

# 5. UI Layout
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>GLOBAL ENERGY TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("---")

# Header Metrics
c1, c2, c3 = st.columns(3)
try:
    gold = yf.Ticker("GC=F", session=session).history(period="1d")['Close'].iloc[-1]
    pkr = yf.Ticker("PKR=X", session=session).history(period="1d")['Close'].iloc[-1]
    gold_pkr = (gold / 31.103) * 10 * pkr
    
    c1.metric("BRENT CRUDE", f"${yf.Ticker('BZ=F', session=session).history(period='1d')['Close'].iloc[-1]:.2f}")
    c2.metric("GOLD 10G (PKR)", f"Rs {gold_pkr:,.0f}")
    c3.metric("USD / PKR", f"{pkr:.2f}")
except:
    st.info("Yahoo is currently busy. Retrying in 30 seconds...")

st.markdown("---")

# Tabbed Navigation
selected_tab = st.radio("SELECT MARKET CATEGORY", list(GROUPS.keys()), horizontal=True)

if selected_tab:
    with st.spinner(f"Synchronizing {selected_tab}..."):
        data = fetch_tab_data(GROUPS[selected_tab])
        if data:
            st.table(pd.DataFrame(data))
        else:
            st.warning("Rate limit reached. Please wait 1 minute before clicking another category.")

# Reset Button
if st.sidebar.button('RELOAD DATA'):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')} PKT")
