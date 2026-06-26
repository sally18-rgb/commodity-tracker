import streamlit as st
import yfinance as yf
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Market Terminal", layout="wide")

# 2. CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #000000 !important; font-family: 'JetBrains Mono', monospace !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'JetBrains Mono', monospace !important; }
    
    div[data-testid="stMetricValue"] { font-size: 36px !important; color: #00FF00 !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] p { color: #888888 !important; text-transform: uppercase; letter-spacing: 2px; font-size: 12px; }
    div[data-testid="stMetricDelta"] { font-size: 14px !important; }

    header, footer, #MainMenu { visibility: hidden; }
    hr { border: 0; border-top: 1px solid #222; margin: 20px 0; }

    /* Refresh button */
    div[data-testid="stButton"] > button {
        background-color: #000 !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: 3px;
        width: 100%;
        padding: 10px;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #00FF00 !important;
        color: #000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Data Fetcher
@st.cache_data(ttl=300)
def fetch_prices():
    results = {}
    symbols = {
        "gold": "GC=F",
        "pkr": "PKR=X",
        "brent": "BZ=F"
    }
    for key, sym in symbols.items():
        try:
            hist = yf.Ticker(sym).history(period="2d")
            if not hist.empty and len(hist) >= 2:
                results[key] = {
                    "price": hist['Close'].iloc[-1],
                    "prev": hist['Close'].iloc[-2],
                }
            else:
                results[key] = None
        except:
            results[key] = None
    return results

def calc_change(data):
    if not data:
        return None, None
    price = data["price"]
    change = ((price - data["prev"]) / data["prev"]) * 100
    return price, change

# 4. Header
st.markdown("<h1 style='text-align: center; letter-spacing: 10px; margin-bottom: 0;'>TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #444 !important; font-size: 11px; letter-spacing: 4px;'>LIVE MARKET MONITOR</p>", unsafe_allow_html=True)
st.markdown("---")

# 5. Fetch
data = fetch_prices()

gold_price, gold_change = calc_change(data.get("gold"))
pkr_price, pkr_change   = calc_change(data.get("pkr"))
brent_price, brent_change = calc_change(data.get("brent"))

# Gold in PKR (per 10g)
if gold_price and pkr_price:
    gold_pkr_10g = (gold_price / 31.103) * 10 * pkr_price
    gold_pkr_change = (gold_change or 0) + (pkr_change or 0)  # approximate combined change
else:
    gold_pkr_10g = None
    gold_pkr_change = None

# 6. Metrics
col1, col2, col3 = st.columns(3)

with col1:
    if gold_price:
        st.metric("GOLD (USD/oz)", f"${gold_price:,.2f}", f"{gold_change:+.2f}%")
    else:
        st.metric("GOLD (USD/oz)", "OFFLINE")

with col2:
    if gold_pkr_10g:
        st.metric("GOLD (PKR/10g)", f"Rs {gold_pkr_10g:,.0f}", f"{gold_pkr_change:+.2f}%")
    else:
        st.metric("GOLD (PKR/10g)", "DATA ERROR")

with col3:
    if brent_price:
        st.metric("BRENT CRUDE (USD/bbl)", f"${brent_price:,.2f}", f"{brent_change:+.2f}%")
    else:
        st.metric("BRENT CRUDE", "OFFLINE")

st.markdown("---")

# 7. Refresh Button + Timestamp
col_a, col_b, col_c = st.columns([2, 1, 2])
with col_b:
    if st.button("⟳  REFRESH"):
        st.cache_data.clear()
        st.rerun()

st.markdown(f"<p style='text-align: center; color: #333 !important; font-size: 11px; margin-top: 10px;'>LAST UPDATED: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')} · FEED: YAHOO FINANCE</p>", unsafe_allow_html=True)
