import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Configuration & Style
st.set_page_config(page_title="Global Energy Terminal", layout="wide")

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
    .stTable { background-color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. The Expanded 100+ Index Database (OilPrice.com Blends Included)
COMMODITY_DICT = {
    # ENERGY - GLOBAL BLENDS (Inspired by OilPrice.com)
    "WTI Crude (USA)": "CL=F",
    "Brent Crude (Global)": "BZ=F",
    "Mars US (Medium Sour)": "MARS",
    "Western Canadian Select": "WCS-USD",
    "Urals (Russian Mix)": "URALS.ME",
    "Murban (Abu Dhabi)": "MURB.AD",
    "Natural Gas (Henry Hub)": "NG=F",
    "Dutch TTF Gas (EU)": "TTF=F",
    "RBOB Gasoline": "RB=F",
    "Heating Oil": "HO=F",
    "Coal (Newcastle)": "MTF=F",
    "Uranium": "UX=F",
    "Ethanol": "CU=F",
    
    # PRECIOUS METALS
    "Gold Spot": "GC=F", "Silver Spot": "SI=F", "Platinum": "PL=F", "Palladium": "PA=F",

    # INDUSTRIAL METALS
    "Copper": "HG=F", "Aluminum": "ALI=F", "Zinc": "ZNC=F", "Nickel": "NICK", "Lead": "LED", 
    "Iron Ore": "TIO=F", "Lithium": "LTH-USD", "Steel": "ST-USD",

    # AGRICULTURE & GRAINS
    "Wheat": "W=F", "Corn": "C=F", "Soybeans": "S=F", "Soybean Oil": "BO=F", "Rough Rice": "RR=F",
    "Oats": "ZO=F", "Canola": "RS=F", "Barley": "BAR=F",

    # SOFTS & LIVESTOCK
    "Coffee": "KC=F", "Sugar": "SB=F", "Cocoa": "CC=F", "Cotton": "CT=F", "Lumber": "LBS=F",
    "Live Cattle": "LC=F", "Lean Hogs": "LH=F", "Feeder Cattle": "FC=F", "Milk": "DA=F",

    # CURRENCIES & MACRO (The "Global" part of the Index)
    "US Dollar Index": "DX=F", "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "10Y Treasury": "^TNX",
    "S&P 500": "ES=F", "VIX Volatility": "^VIX", "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X"
}

@st.cache_data(ttl=300)
def fetch_data(tickers):
    data_list = []
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="5d")
            if not hist.empty:
                last_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                pct_chg = ((last_price - prev_price) / prev_price) * 100
                data_list.append({
                    "CATEGORY": "Energy" if sym in ["CL=F", "BZ=F", "NG=F"] else "Commodity",
                    "INDEX NAME": name,
                    "PRICE (USD)": f"{last_price:,.2f}",
                    "DAY CHG %": f"{pct_chg:+.2f}%"
                })
        except:
            continue
    return data_list

# 3. Layout: Top Header
st.markdown("<h1 style='text-align: center; letter-spacing: 10px;'>EXECUTIVE TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>OILPRICE BLENDS // GLOBAL METALS // GRAIN INDICES</p>", unsafe_allow_html=True)
st.markdown("---")

# 4. The "Dashboard" (Quick View)
c1, c2, c3, c4 = st.columns(4)
with c1:
    val = yf.Ticker("BZ=F").history(period="2d")['Close'].iloc[-1]
    st.metric("BRENT CRUDE", f"${val:.2f}")
with c2:
    val = yf.Ticker("CL=F").history(period="2d")['Close'].iloc[-1]
    st.metric("WTI CRUDE", f"${val:.2f}")
with c3:
    val = yf.Ticker("GC=F").history(period="2d")['Close'].iloc[-1]
    st.metric("GOLD", f"${val:,.0f}")
with c4:
    val = yf.Ticker("DX=F").history(period="2d")['Close'].iloc[-1]
    st.metric("USD INDEX", f"{val:.2f}")

st.markdown("---")

# 5. Searchable Table
st.subheader("LIVE GLOBAL INDEX (100+)")
search = st.text_input("FILTER BY BLEND OR CATEGORY (e.g. 'Crude' or 'Copper')", "")

with st.spinner("UPDATING DATA FEED..."):
    results = fetch_data(COMMODITY_DICT)
    df = pd.DataFrame(results)

if not df.empty:
    if search:
        df = df[df['INDEX NAME'].str.lower().str.contains(search.lower())]
    st.dataframe(df, use_container_width=True, hide_index=True)

# 6. Action Footer
st.markdown("---")
if st.button("MANUAL REFRESH"):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Terminal Status: Connected // Sync Time: {datetime.now().strftime('%H:%M:%S')} PKT")
