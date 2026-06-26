import streamlit as st
import yfinance as yf
import requests
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

    .feed-tag {
        text-align: center;
        color: #333 !important;
        font-size: 11px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)


# 3. Gold fetcher — goldprice.org API (per gram, USD + PKR)
@st.cache_data(ttl=60)
def fetch_gold_goldprice():
    url = "https://data-asg.goldprice.org/dbXRates/USD,PKR"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://goldprice.org/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        result = {}
        for item in data.get("items", []):
            curr = item.get("curr")
            price_per_oz = item.get("xauPrice")
            if curr and price_per_oz:
                result[curr] = price_per_oz / 31.1034768  # convert to per gram
        return result
    except:
        return {}


# 4. Brent fetcher — yfinance
@st.cache_data(ttl=300)
def fetch_brent():
    try:
        hist = yf.Ticker("BZ=F").history(period="2d")
        if not hist.empty and len(hist) >= 2:
            price = hist['Close'].iloc[-1]
            prev  = hist['Close'].iloc[-2]
            change = ((price - prev) / prev) * 100
            return price, change
    except:
        pass
    return None, None


# 5. Header
st.markdown("<h1 style='text-align: center; letter-spacing: 10px; margin-bottom: 0;'>TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #444 !important; font-size: 11px; letter-spacing: 4px;'>LIVE MARKET MONITOR</p>", unsafe_allow_html=True)
st.markdown("---")

# 6. Fetch all data
gold  = fetch_gold_goldprice()
brent_price, brent_change = fetch_brent()

gold_usd_gram = gold.get("USD")
gold_pkr_gram = gold.get("PKR")

# 7. Metrics — 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    if gold_usd_gram:
        st.metric("GOLD (USD / gram)", f"${gold_usd_gram:,.4f}")
    else:
        st.metric("GOLD (USD / gram)", "OFFLINE")

with col2:
    if gold_pkr_gram:
        st.metric("GOLD (PKR / gram)", f"Rs {gold_pkr_gram:,.2f}")
    else:
        st.metric("GOLD (PKR / gram)", "OFFLINE")

with col3:
    if brent_price:
        st.metric("BRENT CRUDE (USD/bbl)", f"${brent_price:,.2f}", f"{brent_change:+.2f}%")
    else:
        st.metric("BRENT CRUDE", "OFFLINE")

st.markdown("---")

# 8. Refresh + Timestamp
col_a, col_b, col_c = st.columns([2, 1, 2])
with col_b:
    if st.button("⟳  REFRESH"):
        st.cache_data.clear()
        st.rerun()

st.markdown(
    f"<p class='feed-tag'>LAST UPDATED: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}"
    f" · GOLD: GOLDPRICE.ORG · BRENT: YAHOO FINANCE</p>",
    unsafe_allow_html=True
)
