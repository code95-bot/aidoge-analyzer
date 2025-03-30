
import streamlit as st
import pandas as pd
import ccxt
import ta
import matplotlib.pyplot as plt

st.title("📊 AIDOGE Analyzer – Analyse Technique en Temps Réel")

# Récupération des données depuis OKX
exchange = ccxt.okx()
symbol = "AIDOGE/USDT"
ohlcv = exchange.fetch_ohlcv(symbol, timeframe="5m", limit=100)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

# Indicateurs
df["RSI"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
macd = ta.trend.MACD(close=df["close"])
df["MACD"] = macd.macd()
df["MACD_signal"] = macd.macd_signal()

# Graphique du prix
st.subheader("📈 Prix de AIDOGE")
st.line_chart(df["close"])

# RSI
st.subheader("📉 RSI")
st.line_chart(df["RSI"])

# MACD
st.subheader("📊 MACD")
st.line_chart(df[["MACD", "MACD_signal"]])

# Analyse et recommandation
rsi = df["RSI"].iloc[-1]
macd_val = df["MACD"].iloc[-1]
macd_sig = df["MACD_signal"].iloc[-1]

st.markdown("### ✅ Recommandation")

if rsi < 30 and macd_val > macd_sig:
    st.success("🔼 Opportunité d'achat (LONG) détectée – RSI < 30 et MACD haussier.")
elif rsi > 70 and macd_val < macd_sig:
    st.error("🔽 Opportunité de vente (SHORT) détectée – RSI > 70 et MACD baissier.")
else:
    st.info("⏸️ Pas de signal clair pour le moment. Attendez une meilleure confirmation.")
