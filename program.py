import streamlit as st
import yfinance as yf
import requests
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Terminal", page_icon="⚫", layout="centered")

# 2. Executive Noir Styling
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    div[data-testid="stMetricValue"] { font-size: 42px !important; color: #ffffff !important; font-weight: 200 !important; }
    div[data-testid="stMetricLabel"] { font-size: 12px !important; color: #666666 !important; text-transform: uppercase; letter-spacing: 3px; }
    .stButton>button { background-color: #ffffff; color: #000000; border-radius: 0px; width: 100%; height: 3.5em; font-weight: bold; }
    hr { border-top: 1px solid #222222; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. The Data Engine (Optimized for Mobile)
def get_market_data():
    try:
        # Fetch 5 days to ensure we have data on weekends
        g_ticker = yf.Ticker("GC=F").history(period="5d")
        o_ticker = yf.Ticker("BZ=F").history(period="5d")
        
        # Exchange Rate
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        pkr_rate = r.json()['rates']['PKR']

        if not g_ticker.empty and not o_ticker.empty:
            g_val = g_ticker['Close'].iloc[-1]
            o_val = o_ticker['Close'].iloc[-1]
            g_diff = g_val - g_ticker['Close'].iloc[-2]
            o_diff = o_val - o_ticker['Close'].iloc[-2]
        else:
            # Emergency fallback if API is throttled
            g_val, g_diff, o_val, o_diff = 4494.1, 0.0, 112.2, 0.0

        pk_gold = (g_val * 0.375 * pkr_rate) * 1.02
        
        return {
            "g": g_val, "gd": g_diff, 
            "pkg": pk_gold, 
            "o": o_val, "od": o_diff, 
            "rate": pkr_rate,
            "time": datetime.now().strftime("%H:%M:%S")
        }
    except Exception as e:
        return None

# 4. Main Interface
st.title("MARKET TERMINAL")
st.markdown("---")

# Force data fetch immediately on page load
data = get_market_data()

if data:
    st.metric(label="GOLD SPOT / USD", value=f"{data['g']:,.1f}", delta=f"{data['gd']:,.2f}")
    st.markdown("---")
    st.metric(label="PAKISTAN GOLD / PKR", value=f"{data['pkg']:,.0f}", delta="LIVE RATE")
    st.markdown("---")
    st.metric(label="BRENT CRUDE / USD", value=f"{data['o']:,.1f}", delta=f"{data['od']:,.2f}")
    st.markdown("---")
    
    st.caption(f"FX: {data['rate']:.2f} | LAST SYNC: {data['time']} PKT")

    if st.button('REFRESH TERMINAL'):
        st.cache_data.clear()
        st.rerun()
else:
    st.error("CONNECTION TIMEOUT - PLEASE REFRESH")
