import streamlit as st
from yahooquery import Ticker
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Global Terminal", layout="wide")

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

# 3. Expanded 100+ Index Database (Categorized)
COMMODITY_LIST = {
    "WTI Crude": "CL=F", "Brent Crude": "BZ=F", "Natural Gas": "NG=F", "Heating Oil": "HO=F",
    "Gasoline": "RB=F", "Low Sulphur Gasoil": "G=F", "Coal": "MTF=F", "Uranium": "UX=F",
    "Gold": "GC=F", "Silver": "SI=F", "Platinum": "PL=F", "Palladium": "PA=F",
    "Copper": "HG=F", "Aluminum": "ALI=F", "Zinc": "ZNC=F", "Nickel": "NICK",
    "Wheat": "W=F", "Corn": "C=F", "Soybeans": "S=F", "Coffee": "KC=F", "Sugar": "SB=F",
    "Cotton": "CT=F", "Live Cattle": "LC=F", "Lean Hogs": "LH=F", "Bitcoin": "BTC-USD",
    "USD Index": "DX=F", "10Y Treasury": "^TNX", "S&P 500": "ES=F"
    # You can continue adding tickers here to reach 100+
}

@st.cache_data(ttl=600)
def get_all_market_data(tickers_dict):
    symbols = list(tickers_dict.values())
    t = Ticker(symbols, retry=5, status_forcelist=[429, 500, 502])
    
    # Fetching price and change data
    try:
        data = t.price
        results = []
        for name, symbol in tickers_dict.items():
            details = data.get(symbol, {})
            if isinstance(details, dict):
                price = details.get('regularMarketPrice', 0)
                change = details.get('regularMarketChangePercent', 0) * 100
                results.append({
                    "Index": name,
                    "Price (USD)": f"{price:,.2f}",
                    "24h Change": f"{change:+.2f}%"
                })
        return results
    except Exception:
        return []

# 4. Main Interface
st.markdown("<h1 style='text-align: center; letter-spacing: 8px;'>COMMODITY TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("---")

# FEATURED TOP BAR (Brent, Gold, Nat Gas)
c1, c2, c3 = st.columns(3)
featured_symbols = ["BZ=F", "GC=F", "NG=F"]
featured_data = Ticker(featured_symbols).price

for col, sym, label in zip([c1, c2, c3], featured_symbols, ["BRENT CRUDE", "GOLD SPOT", "NATURAL GAS"]):
    try:
        p = featured_data[sym]['regularMarketPrice']
        chg = featured_data[sym]['regularMarketChangePercent'] * 100
        col.metric(label, f"${p:,.2f}", f"{chg:+.2f}%")
    except:
        col.metric(label, "DATA OFFLINE")

st.markdown("---")

# FULL SEARCHABLE INDEX
st.subheader("GLOBAL MARKET OVERVIEW")
search = st.text_input("SEARCH TICKER (e.g., Oil, Gold, Wheat)...", "").lower()

with st.spinner("UPDATING GLOBAL FEED..."):
    results_list = get_all_market_data(COMMODITY_LIST)
    if results_list:
        df = pd.DataFrame(results_list)
        if search:
            df = df[df['Index'].str.lower().str.contains(search)]
        st.table(df)
    else:
        st.error("Terminal Rate Limited. System will auto-retry in 10 minutes.")

# FOOTER
if st.button("REBOOT DATA FEED"):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Last Terminal Sync: {datetime.now().strftime('%H:%M:%S')} PKT")
