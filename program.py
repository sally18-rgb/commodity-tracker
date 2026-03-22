import streamlit as st
import yfinance as yf
import requests
from datetime import datetime

# 1. Force Page Config
st.set_page_config(page_title="Terminal", layout="centered")

# 2. Bulletproof Noir CSS
st.markdown("""
    <style>
    /* Force background to Black */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Force general text to White */
    h1, h2, h3, p, span, label {
        color: #ffffff !important;
    }

    /* Metric Value Styling */
    div[data-testid="stMetricValue"] { 
        font-size: 42px !important; 
        color: #ffffff !important; 
        font-weight: 200 !important; 
    }

    /* Metric Label Styling */
    div[data-testid="stMetricLabel"] p { 
        font-size: 12px !important; 
        color: #888888 !important; 
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
    }

    /* BUTTON FIX: White background with BLACK text */
    .stButton>button { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        border-radius: 0px !important; 
        width: 100% !important; 
        font-weight: bold !important;
        border: none !important;
        text-transform: uppercase !important;
    }
    
    /* Ensure the text inside the button stays black even when forced */
    .stButton>button p {
        color: #000000 !important;
    }

    /* Hide standard Streamlit elements */
    header, footer, #MainMenu {visibility: hidden;}
    
    hr { border-top: 1px solid #333333 !important; }
    </style>
    """, unsafe_allow_html=True)

def get_market_data():
    try:
        g_data = yf.Ticker("GC=F").history(period="5d")
        o_data = yf.Ticker("BZ=F").history(period="5d")
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        pkr_rate = r.json()['rates']['PKR']

        if not g_data.empty and not o_data.empty:
            g_val = g_data['Close'].iloc[-1]
            o_val = o_data['Close
