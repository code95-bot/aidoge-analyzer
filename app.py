
import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import time
import datetime
import ta

# ------------------------- إعدادات الواجهة -------------------------
st.set_page_config(page_title="AIDOGE Analyzer", layout="wide")

st.title("📊 AIDOGE Analyzer – Analyse Technique Combinée")

# ------------------------- اختيار العملة والفريم -------------------------
col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox("Sélectionner la crypto :", ["AIDOGE/USDT", "DOGE/USDT", "BTC/USDT", "ETH/USDT", "PEPE/USDT"])
with col2:
    timeframe = st.selectbox("Cadre temporel :", ["1m", "5m", "15m", "1h", "1d", "1w"])

# ------------------------- جلب السعر والمعلومات السوقية -------------------------
try:
    exchange = ccxt.okx()
    ticker = exchange.fetch_ticker(symbol)
    current_price = ticker["last"]
    daily_change = ticker["percentage"]
    daily_volume = ticker["quoteVolume"]

    st.markdown(f"""
    ### 💰 Prix actuel : <span style='color:green'>{current_price:.12f}</span> USDT  
    🔻 Variation 24h : **{daily_change:.2f}%**  
    📊 Volume 24h : **{daily_volume:.2f} USDT**
    """, unsafe_allow_html=True)
except Exception as e:
    st.error("❌ Échec de la récupération des données de prix. Vérifiez votre connexion ou symbol.")

# ------------------------- التحليل الفني -------------------------
def fetch_ohlcv(symbol, timeframe, limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

try:
    df = fetch_ohlcv(symbol, timeframe)
    rsi = ta.momentum.RSIIndicator(df["close"]).rsi().iloc[-1]
    macd = ta.trend.MACD(df["close"])
    macd_value = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]
    boll = ta.volatility.BollingerBands(df["close"])
    boll_lower = boll.bollinger_lband().iloc[-1]
    boll_upper = boll.bollinger_hband().iloc[-1]

    # ------------------------- الجدول -------------------------
    st.subheader("🧾 Synthèse des indicateurs")
    data = {
        "Indicateur": ["RSI", "MACD", "Bandes de Bollinger"],
        "Valeur": [f"{rsi:.2f}", f"{macd_value:.2e} / {macd_signal:.2e}", f"{df['close'].iloc[-1]:.2e}"],
        "Interprétation": []
    }

    # التفسير
    if rsi > 70:
        data["Interprétation"].append("🔺 Surachat")
    elif rsi < 30:
        data["Interprétation"].append("🔻 Survente")
    else:
        data["Interprétation"].append("⏸️ Neutre")

    if macd_value > macd_signal:
        data["Interprétation"].append("📈 Haussier")
    elif macd_value < macd_signal:
        data["Interprétation"].append("📉 Baissier")
    else:
        data["Interprétation"].append("⏸️ Stable")

    if df["close"].iloc[-1] < boll_lower:
        data["Interprétation"].append("🔻 Proche bas")
    elif df["close"].iloc[-1] > boll_upper:
        data["Interprétation"].append("🔺 Proche haut")
    else:
        data["Interprétation"].append("🟡 Zone neutre")

    st.table(pd.DataFrame(data))

    # ------------------------- التوصية -------------------------
    st.subheader("✅ Conclusion stratégique")
    if rsi < 35 and macd_value > macd_signal and df["close"].iloc[-1] < boll_lower:
        st.success("📢 Signal LONG détecté – Opportunité d'achat potentielle.")
    elif rsi > 65 and macd_value < macd_signal and df["close"].iloc[-1] > boll_upper:
        st.error("📢 Signal SHORT détecté – Risque de vente.")
    else:
        st.info("⏳ Signal mitigé – Attendez confirmation claire de plusieurs indicateurs.")
except:
    st.warning("🔄 En attente de données valides pour l'analyse technique.")

st.caption("💬 Mise à jour automatique à chaque rechargement – Derniers 100 chandeliers")
