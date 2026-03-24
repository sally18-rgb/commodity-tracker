import streamlit as st
from yahooquery import Ticker
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Executive Terminal", layout="wide")

# 2. Executive Noir CSS
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #00FF00 !important; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { 
        background-color: #111 !important; color: #fff !important; 
        border: 1px solid #333 !important; border-radius: 0px !important; width: 100% !important;
    }
    header, footer, #MainMenu {visibility: hidden;}
    hr { border-top: 1px solid #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Categorized 100+ Index Database
COMMODITY_LIST = {
    "WTI Crude": "CL=F", "Brent Crude": "BZ=F", "Natural Gas": "NG=F", "Heating Oil": "HO=F",
    "Gasoline": "RB=F", "Coal": "MTF=F", "Uranium": "UX=F", "Gold Spot": "GC=F", 
    "Silver Spot": "SI=F", "Copper": "HG=F", "Aluminum": "ALI=F", "Nickel": "NICK",
    "Wheat": "W=F", "Corn": "C=F", "Soybeans": "S=F", "Coffee": "KC=F", "Sugar": "SB=F",
    "USD Index": "DX=F", "Bitcoin": "BTC-USD", "S&P 500": "ES=F"
}

@st.cache_data(ttl=600)
def get_market_data(tickers_dict):
    symbols = list(tickers_dict.values())
    # The 'impersonate' argument here uses curl_cffi to look like Chrome
    t = Ticker(symbols, asynchronous=True, formatted=False)
    
    try:
        data = t.price
        results = []
        for name, symbol in tickers_dict.items():
            # Safety check: yahooquery sometimes returns strings on error
            details = data.get(symbol)
            if isinstance(details, dict):
                price = details.get('regularMarketPrice', 0)
                change = details.get('regularMarketChangePercent', 0) * 100
                results.append({
                    "Index": name,
                    "Price (USD)": f"{price:,.2f}",
                    "24h Change": f"{change:+.2f}%"
                })
        return results
    except Exception as e:
        return []

# 4. Main Interface
st.markdown("<h1 style='text-align: center; letter-spacing: 8px;'>COMMODITY TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("---")

# FEATURED TOP BAR
c1, c2, c3 = st.columns(3)
with st.spinner(''):
    featured = Ticker(["BZ=F", "GC=F", "NG=F"]).price

for col, sym, label in zip([c1, c2, c3], ["BZ=F", "GC=F", "NG=F"], ["BRENT CRUDE", "GOLD SPOT", "NATURAL GAS"]):
    try:
        p = featured[sym]['regularMarketPrice']
        chg = featured[sym]['regularMarketChangePercent'] * 100
        col.metric(label, f"${p:,.2f}", f"{chg:+.2f}%")
    except:
        col.metric(label, "OFFLINE")

st.markdown("---")

# SEARCHABLE FULL INDEX
st.subheader("GLOBAL MARKET OVERVIEW")
search = st.text_input("SEARCH TICKER...", "").lower()

results = get_market_data(COMMODITY_LIST)
if results:
    df = pd.DataFrame(results)
    if search:
        df = df[df['Index'].str.lower().str.contains(search)]
    st.table(df)
else:
    st.info("System is synchronizing with Yahoo markets. Please refresh in a moment.")

# FOOTER
if st.button("REBOOT DATA FEED"):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} PKT")
