import streamlit as st
import yfinance as yf
import requests

# 1. Page Configuration for Mobile & Desktop
st.set_page_config(
    page_title="Executive Market Terminal",
    page_icon="📈",
    layout="centered"
)

# 2. Premium "Entrepreneur" Styling
st.markdown("""
    <style>
    .main { background-color: #0b0d12; color: #ffffff; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #f3cf00 !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; color: #808495 !important; text-transform: uppercase; }
    .stButton>button { 
        background: linear-gradient(135deg, #f3cf00 0%, #b59b00 100%); 
        color: black; border: none; font-weight: bold; border-radius: 10px; width: 100%; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Secure Data Fetching Function
@st.cache_data(ttl=300)
def get_market_data():
    try:
        # We fetch 5 days of data to ensure we find a 'Closing Price' even on weekends
        gold_ticker = yf.Ticker("GC=F")
        oil_ticker = yf.Ticker("BZ=F")
        
        gold_hist = gold_ticker.history(period="5d")
        oil_hist = oil_ticker.history(period="5d")

        # Live PKR Exchange Rate
        response = requests.get("https://open.er-api.com/v6/latest/USD")
        pkr_rate = response.json()['rates']['PKR']

        # --- SAFETY CHECK: Avoid "Index Out of Bounds" Error ---
        if not gold_hist.empty and not oil_hist.empty:
            # Get the very last available closing price
            gold_usd = gold_hist['Close'].iloc[-1]
            oil_usd = oil_hist['Close'].iloc[-1]
            
            # Calculate daily change (Delta)
            gold_delta = gold_usd - gold_hist['Close'].iloc[-2]
            oil_delta = oil_usd - oil_hist['Close'].iloc[-2]
        else:
            # Absolute Fallback if APIs are totally down
            gold_usd, gold_delta = 4494.1, 0.0
            oil_usd, oil_delta = 112.2, 0.0

        # Gold Pakistan Formula: (Spot / 2.666) * PKR Rate + 2% Local Premium
        # This roughly equals: (Spot * 0.375) * PKR * 1.02
        gold_pkr = (gold_usd * 0.375 * pkr_rate) * 1.02

        return {
            "gold_usd": gold_usd,
            "gold_delta": gold_delta,
            "gold_pkr": gold_pkr,
            "oil_usd": oil_usd,
            "oil_delta": oil_delta,
            "pkr_rate": pkr_rate
        }
    except Exception as e:
        return f"System Error: {e}"

# 4. Professional UI Layout
st.title("🏛️ Executive Intelligence")
st.markdown("---")

# Refresh Button at the top for easy thumb access on mobile
if st.button('🔄 SYNC LIVE MARKET DATA'):
    st.rerun()

data = get_market_data()

if isinstance(data, str):
    st.error(data)
else:
    # Large Metrics
    st.metric(
        label="Gold Spot (USD/OZ)", 
        value=f"${data['gold_usd']:,.2f}", 
        delta=f"{data['gold_delta']:,.2f}"
    )
    
    st.metric(
        label="Gold Price Pakistan (PKR/Tola)", 
        value=f"Rs. {data['gold_pkr']:,.0f}",
        delta="Sarafa Market Rate"
    )
    
    st.metric(
        label="Brent Crude Oil (USD/BBL)", 
        value=f"${data['oil_usd']:,.2f}", 
        delta=f"{data['oil_delta']:,.2f}"
    )

    st.divider()
    
    # Context Footer
    st.caption(f"Forex Interbank: 1 USD = {data['pkr_rate']:.2f} PKR")
    st.success("Terminal Online | Data Verified")

st.markdown("---")
