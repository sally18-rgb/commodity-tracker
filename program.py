import streamlit as st
import yfinance as yf
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Terminal",
    page_icon="⚫",
    layout="centered"
)

# 2. Executive Noir Styling (Pure Black & White)
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    
    /* Metrics */
    div[data-testid="stMetricValue"] { 
        font-size: 42px !important; 
        color: #ffffff !important; 
        font-weight: 200 !important;
    }
    div[data-testid="stMetricLabel"] { 
        font-size: 12px !important; 
        color: #666666 !important; 
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    div[data-testid="stMetricDelta"] { font-family: monospace; font-size: 14px !important; }

    /* Buttons */
    .stButton>button { 
        background-color: #ffffff; 
        color: #000000; 
        border: none;
        border-radius: 0px;
        width: 100%; 
        height: 3.5em;
        font-weight: bold;
        letter-spacing: 2px;
    }
    .stButton>button:hover {
        background-color: #cccccc;
        color: #000000;
    }

    /* Clean up UI */
    hr { border-top: 1px solid #222222; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Data Engine (Cache removed for instant sync)
def get_market_data():
    try:
        # Fetching 5 days to ensure no 'weekend' errors
        gold_ticker = yf.Ticker("GC=F")
        oil_ticker = yf.Ticker("BZ=F")
        
        gold_hist = gold_ticker.history(period="5d")
        oil_hist = oil_ticker.history(period="5d")

        # Live PKR Rate
        pkr_rate = requests.get("https://open.er-api.com/v6/latest/USD").json()['rates']['PKR']

        if not gold_hist.empty and not oil_hist.empty:
            g_val = gold_hist['Close'].iloc[-1]
            o_val = oil_hist['Close'].iloc[-1]
            g_delta = g_val - gold_hist['Close'].iloc[-2]
            o_delta = o_val - oil_hist['Close'].iloc[-2]
        else:
            # Fallback values
            g_val, g_delta, o_val, o_delta = 4494.1, 0.0, 112.2, 0.0

        pk_gold = (g_val * 0.375 * pkr_rate) * 1.02

        return g_val, g_delta, pk_gold, o_val, o_delta, pkr_rate
    except:
        return None

# 4. Interface
st.title("MARKET TERMINAL")
st.markdown("---")

# The Fixed Sync Button
if st.button('SYNC LIVE DATA'):
    st.cache_data.clear() # This kills the old memory
    st.rerun() # This forces a fresh pull

data = get_market_data()

if data:
    g_val, g_delta, pk_gold, o_val, o_delta, pkr_rate = data

    st.metric(label="GOLD SPOT / USD", value=f"{g_val:,.1f}", delta=f"{g_delta:,.2f}")
    st.markdown("---")
    st.metric(label="PAKISTAN GOLD / PKR", value=f"{pk_gold:,.0f}", delta="SPOT + 2%")
    st.markdown("---")
    st.metric(label="BRENT CRUDE / USD", value=f"{o_val:,.1f}", delta=f"{o_delta:,.2f}")
    st.markdown("---")
    
    st.caption(f"FX RATE: 1 USD = {pkr_rate:.2f} PKR")
else:
    st.error("OFFLINE")
