
import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import plotly.express as px
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

# ========== Configuration ==========
st.set_page_config(layout="wide")
API_KEY = "kw4znozi5u6m56et_jiriurfoyaqfixxo"
sentiment_url = "https://api.senticrypt.io/v1/market-sentiment"

# ========== Helper Functions ==========
def get_sentiment_data(symbol="BTC"):
    try:
        response = requests.get(
            sentiment_url,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        data = response.json()
        return data.get("data", {})
    except Exception as e:
        return {"error": str(e)}

def calculate_indicators(df):
    close = df["close"]
    rsi = RSIIndicator(close=close).rsi()
    macd = MACD(close=close)
    bb = BollingerBands(close=close)
    return {
        "RSI": rsi.iloc[-1],
        "MACD": macd.macd().iloc[-1],
        "MACD_signal": macd.macd_signal().iloc[-1],
        "BOLL_upper": bb.bollinger_hband().iloc[-1],
        "BOLL_lower": bb.bollinger_lband().iloc[-1],
        "Last Price": close.iloc[-1]
    }

def pivot_points(df):
    high = df["high"].iloc[-1]
    low = df["low"].iloc[-1]
    close = df["close"].iloc[-1]
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)
    return [s3, s2, s1, pivot, r1, r2, r3]

# ========== Streamlit Layout ==========
st.title("📊 AIDOGE Analyzer – Analyse Technique + Sentiment Whale")

col1, col2 = st.columns(2)
symbol = col1.selectbox("Sélectionner la crypto :", ["AIDOGE/USDT", "BTC/USDT", "ETH/USDT"])
interval = col2.selectbox("Cadre temporel :", ["1m", "5m", "15m", "1h", "1d", "1w"])

# Dummy OHLC data (replace with real exchange data)
np.random.seed(42)
df = pd.DataFrame({
    "close": np.random.normal(0.00000000008, 0.000000000005, 100),
    "high": np.random.normal(0.000000000085, 0.000000000004, 100),
    "low": np.random.normal(0.000000000075, 0.000000000004, 100)
})

# ========== Indicator Calculation ==========
indicators = calculate_indicators(df)

# ========== Pivot Points ==========
levels = pivot_points(df)
level_names = ["Support 3", "Support 2", "Support 1", "Pivot", "Résistance 1", "Résistance 2", "Résistance 3"]
levels_df = pd.DataFrame({
    "Niveau": level_names,
    "Valeur": [f"{val:.20f}" for val in levels]
})

# ========== Display Indicators ==========
st.subheader("📈 Synthèse des indicateurs")
st.table(pd.DataFrame({
    "Indicateur": ["RSI", "MACD", "Bandes de Bollinger"],
    "Valeur": [f"{indicators['RSI']:.2f}", f"{indicators['MACD']:.2e} / {indicators['MACD_signal']:.2e}", f"{indicators['BOLL_lower']:.2e} - {indicators['BOLL_upper']:.2e}"],
    "Interprétation": ["🟦 Neutre", "📉 Baissier" if indicators['MACD'] < indicators['MACD_signal'] else "📈 Haussier", "🔻 Proche bas" if indicators["Last Price"] <= indicators["BOLL_lower"] else "🔺 Proche haut"]
}))

# ========== Display Pivot Table ==========
st.subheader("📌 Niveaux de Support & Résistance")
st.table(levels_df)

# ========== Market Sentiment ==========
st.subheader("📊 Analyse des Sentiments du Marché")
sentiment_data = get_sentiment_data()
if "error" in sentiment_data:
    st.error(f"Erreur lors de la récupération des données : {sentiment_data['error']}")
else:
    overall = sentiment_data.get("overall_sentiment", "neutral").capitalize()
    impact = sentiment_data.get("impact_score", 50)
    pie = px.pie(
        names=["Positive", "Negative", "Neutral"],
        values=[impact, 100-impact, 0],
        title="Sentiment Global du Marché"
    )
    st.plotly_chart(pie, use_container_width=True)
    st.info(f"🐳 Sentiment actuel : **{overall}** – Impact sur le marché estimé à **{impact}%**")

    if overall.lower() == "positive":
        st.success("✅ Recommandation : Opportunité d’achat si confirmé techniquement.")
    elif overall.lower() == "negative":
        st.error("🚨 Risque de vente – le marché montre une pression vendeuse.")
    else:
        st.warning("⚠️ Marché hésitant – attendez confirmation technique.")
