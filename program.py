import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Global Energy Terminal", layout="wide")

# 2. Executive Noir CSS
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; color: #00FF00 !important; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; }
    header, footer, #MainMenu {visibility: hidden;}
    .stTable { background-color: #111 !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Categorized Database (Major Global Benchmarks)
MARKET_DATABASE = {
    "Global Benchmarks": {
        "Brent Crude (London)": "BZ=F",
        "WTI Crude (US)": "CL=F",
        "Dubai Crude": "DUB=F",
        "OPEC Basket": "OPEC",
    },
    "Refined Products": {
        "RBOB Gasoline": "RB=F",
        "Heating Oil": "HO=F",
        "Natural Gas": "NG=F",
        "Ethanol": "CU=F"
    },
    "Regional Indices": {
        "Urals (Russia)": "URL.L",
        "Murban (UAE)": "MUR=F",
        "Western Canadian Select": "WCS",
        "KSE 100 (Pakistan)": "^KSE",
        "USD/PKR Exchange": "PKR=X"
    }
}

@st.cache_data(ttl=600)
def fetch_group_data(category_dict):
    results = []
    for name, sym in category_dict.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="2d")
            if not hist.empty:
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

# 4. Main Interface
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>GLOBAL ENERGY TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("---")

# FEATURED BAR (Gold, Brent, PKR)
c1, c2, c3 = st.columns(3)
try:
    gold = yf.Ticker("GC=F").history(period="2d")['Close']
    pkr = yf.Ticker("PKR=X").history(period="2d")['Close'].iloc[-1]
    gold_pkr = (gold.iloc[-1] / 31.103) * 10 * pkr
    
    c1.metric("BRENT CRUDE", f"${yf.Ticker('BZ=F').history(period='1d')['Close'].iloc[-1]:.2f}")
    c2.metric("GOLD (10G PKR)", f"Rs {gold_pkr:,.0f}")
    c3.metric("USD / PKR", f"{pkr:.2f}")
except:
    st.write("Initializing Data Feed...")

st.markdown("---")

# CATEGORIZED TABLES
tabs = st.tabs(["Global Benchmarks", "Refined Products", "Regional/Local"])

for i, (category, data_dict) in enumerate(MARKET_DATABASE.items()):
    with tabs[i]:
        res = fetch_group_data(data_dict)
        if res:
            st.table(pd.DataFrame(res))
        else:
            st.info(f"Checking {category} connection...")

# REFRESH
if st.sidebar.button('FORCE SYNC'):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
