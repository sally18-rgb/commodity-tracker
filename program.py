import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# 1. SETUP SESSION
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36'})

# 2. PAGE CONFIG
st.set_page_config(page_title="Executive Terminal", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #00FF00 !important; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { background-color: #111 !important; color: #fff !important; border-radius: 0px !important; width: 100% !important; border: 1px solid #333 !important; }
    header, footer, #MainMenu {visibility: hidden;}
    hr { border-top: 1px solid #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 100+ INDEX DATA
COMMODITY_LIST = {
    "WTI Crude": "CL=F", "Brent Crude": "BZ=F", "Natural Gas": "NG=F", "Heating Oil": "HO=F",
    "Gasoline": "RB=F", "Coal": "MTF=F", "Gold Spot": "GC=F", "Silver Spot": "SI=F", 
    "Copper": "HG=F", "Aluminum": "ALI=F", "Nickel": "NICK", "Wheat": "W=F", 
    "Corn": "C=F", "Soybeans": "S=F", "Coffee": "KC=F", "USD Index": "DX=F", 
    "Bitcoin": "BTC-USD", "S&P 500": "ES=F", "10Y Treasury": "^TNX"
}

@st.cache_data(ttl=600)
def get_data(tickers):
    res = []
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym, session=session)
            # Use period='1mo' to ensure we get valid close prices even on weekends
            hist = t.history(period="5d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = ((price - prev) / prev) * 100
                res.append({"Index": name, "Value": f"{price:,.2f}", "24h %": f"{chg:+.2f}%"})
        except:
            continue
    return res

# 4. INTERFACE
st.markdown("<h1 style='text-align: center; letter-spacing: 8px;'>COMMODITY TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("---")

# TOP BAR
c1, c2, c3 = st.columns(3)
featured = {"BRENT CRUDE": "BZ=F", "GOLD SPOT": "GC=F", "NATURAL GAS": "NG=F"}
for col, (lab, sym) in zip([c1, c2, c3], featured.items()):
    try:
        val = yf.Ticker(sym, session=session).history(period="2d")['Close']
        col.metric(lab, f"${val.iloc[-1]:.2f}", f"{((val.iloc[-1]-val.iloc[-2])/val.iloc[-2]*100):+.2f}%")
    except:
        col.metric(lab, "DATA SYNCING")

st.markdown("---")

# MAIN TABLE
st.subheader("GLOBAL MARKET OVERVIEW")
search = st.text_input("SEARCH TICKER...", "").lower()

all_results = get_data(COMMODITY_LIST)
if all_results:
    df = pd.DataFrame(all_results)
    if search:
        df = df[df['Index'].str.lower().str.contains(search)]
    st.table(df)
else:
    st.info("Market data is initializing. If prices stay offline, use the Reboot button below.")

# FOOTER
if st.button("REBOOT DATA FEED"):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')} // System Operational")
