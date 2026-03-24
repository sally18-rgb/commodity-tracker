import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Executive Terminal", layout="wide")

# 2. Noir Style CSS
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { font-size: 30px !important; color: #FFD700 !important; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { 
        background-color: #ffffff !important; color: #000000 !important; 
        border-radius: 0px !important; width: 100% !important; font-weight: bold !important;
    }
    header, footer, #MainMenu {visibility: hidden;}
    hr { border-top: 1px solid #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Core Data Logic
@st.cache_data(ttl=300)
def get_market_data():
    # Focused list for Pakistan & Global markets
    assets = {
        "Gold (10g) PKR": "GC=F", # We will calculate this below
        "Brent Crude": "BZ=F",
        "WTI Crude": "CL=F",
        "Silver": "SI=F",
        "KSE 100 (Pak)": "^KSE",
        "USD/PKR": "PKR=X"
    }
    
    results = []
    for name, sym in assets.items():
        try:
            data = yf.Ticker(sym).history(period="2d")
            if not data.empty:
                price = data['Close'].iloc[-1]
                # Calculation for Gold 10 grams in PKR (Approximate)
                if name == "Gold (10g) PKR":
                    pkr_rate = yf.Ticker("PKR=X").history(period="1d")['Close'].iloc[-1]
                    # (Gold Ounce / 31.103) * 10 * PKR Rate
                    price = (price / 31.103) * 10 * pkr_rate
                
                change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                results.append({"Index": name, "Price": f"{price:,.0f}", "Change %": f"{change:+.2f}%"})
        except:
            continue
    return results

# 4. Interface
st.markdown("<h1 style='text-align: center; letter-spacing: 10px;'>EXECUTIVE TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("---")

# Featured Metrics
col1, col2, col3 = st.columns(3)
try:
    # Brent Crude
    oil = yf.Ticker("BZ=F").history(period="2d")['Close']
    col1.metric("BRENT CRUDE", f"${oil.iloc[-1]:.2f}")
    
    # Gold Global
    gold = yf.Ticker("GC=F").history(period="2d")['Close']
    col2.metric("GOLD (GLOBAL)", f"${gold.iloc[-1]:.0f}")
    
    # Gold Pakistan (Estimated 10 Grams)
    pkr = yf.Ticker("PKR=X").history(period="2d")['Close'].iloc[-1]
    gold_pkr = (gold.iloc[-1] / 31.1035) * 10 * pkr
    col3.metric("GOLD 10G (PKR)", f"Rs {gold_pkr:,.0f}")
except:
    st.write("Syncing Market Data...")

st.markdown("---")

# Market Table
st.subheader("LOCAL & GLOBAL SNAPSHOT")
data_feed = get_market_data()
if data_feed:
    st.table(pd.DataFrame(data_feed))

# Footer
if st.button('REFRESH TERMINAL'):
    st.cache_data.clear()
    st.rerun()

st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} PKT")
