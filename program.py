import streamlit as st
import yfinance as yf
import requests

# 1. Page Config - 'centered' usually looks better on mobile than 'wide'
st.set_page_config(page_title="Executive Tracker", page_icon="📈", layout="centered")

# Custom CSS to make metrics look great on mobile
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
    .stButton>button { width: 100%; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Market Terminal")

def get_commodity_data():
    try:
        # Fetching Data
        gold = yf.Ticker("GC=F").history(period="1d")
        oil = yf.Ticker("BZ=F").history(period="1d")
        pkr_rate = requests.get("https://open.er-api.com/v6/latest/USD").json()['rates']['PKR']
        
        gold_usd = gold['Close'].iloc[-1]
        brent_price = oil['Close'].iloc[-1]
        pkr_gold_tola = (gold_usd * 0.375 * pkr_rate) * 1.02 # 2% premium

        return {
            "gold_usd": gold_usd,
            "gold_pkr": pkr_gold_tola,
            "oil_brent": brent_price,
            "pkr_rate": pkr_rate
        }
    except Exception as e:
        return f"Error: {e}"

# --- Mobile-Ready UI ---

if st.button('🔄 Refresh Market Prices'):
    with st.spinner('Syncing...'):
        data = get_commodity_data()

        if isinstance(data, str):
            st.error(data)
        else:
            # On mobile, these will stack vertically automatically
            st.metric(label="Gold Int. (USD/oz)", value=f"${data['gold_usd']:,.2f}")
            st.metric(label="Gold Price Pakistan (PKR/Tola)", value=f"Rs. {data['gold_pkr']:,.0f}")
            st.metric(label="Brent Crude Oil (USD/bbl)", value=f"${data['oil_brent']:,.2f}")

            st.divider()
            st.caption(f"Rate: 1 USD = {data['pkr_rate']:.2f} PKR")
            st.success("Market Data Live")
else:
    st.info("Tap the button to update prices.")