
import streamlit as st
import pandas as pd
import ccxt
import ta
import matplotlib.pyplot as plt

st.set_page_config(page_title="AIDOGE Analyzer", layout="centered")

st.title("📊 AIDOGE Analyzer – Analyse Technique en Temps Réel")

# --------- 1. Chargement des données ---------
exchange = ccxt.okx()
symbol = "AIDOGE/USDT"
ohlcv = exchange.fetch_ohlcv(symbol, timeframe="5m", limit=100)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

# --------- 2. Calcul des indicateurs ---------
df["RSI"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
macd = ta.trend.MACD(close=df["close"])
df["MACD"] = macd.macd()
df["MACD_signal"] = macd.macd_signal()

# --------- 3. Graphiques ---------
st.subheader("📈 Prix de AIDOGE")
st.line_chart(df["close"])

# Prix actuel formaté
latest_price = df["close"].iloc[-1]
formatted_price = f"{latest_price:.12f}"
st.markdown(f"### 💰 Prix actuel : `{formatted_price}` USDT")

# --------- 4. RSI ---------
st.subheader("📉 RSI")
st.line_chart(df["RSI"])

rsi = df["RSI"].iloc[-1]
st.markdown(f"- **RSI actuel :** `{rsi:.2f}`")
if rsi < 30:
    st.success("✅ RSI indique une *sous-évaluation* – possible **achat**.")
elif rsi > 70:
    st.error("❌ RSI indique une *suroévaluation* – possible **vente**.")
else:
    st.info("ℹ️ RSI dans une zone neutre.")

# --------- 5. MACD ---------
st.subheader("📊 MACD")
st.line_chart(df[["MACD", "MACD_signal"]])

macd_val = df["MACD"].iloc[-1]
macd_sig = df["MACD_signal"].iloc[-1]
st.markdown(f"- **MACD :** `{macd_val:.5e}`")
st.markdown(f"- **Signal :** `{macd_sig:.5e}`")
if macd_val > macd_sig:
    st.success("✅ MACD haussier – Momentum positif.")
elif macd_val < macd_sig:
    st.error("❌ MACD baissier – Pression vendeuse.")
else:
    st.info("ℹ️ MACD neutre – Aucun signal fort.")

# --------- 6. Recommandation générale ---------
st.markdown("### 📌 Recommandation finale")

if rsi < 30 and macd_val > macd_sig:
    st.success("📈 Opportunité d'achat (LONG) confirmée par RSI & MACD.")
elif rsi > 70 and macd_val < macd_sig:
    st.error("📉 Opportunité de vente (SHORT) confirmée par RSI & MACD.")
else:
    st.info("⏸️ Pas de signal clair – attendre confirmation.")

st.caption("🕒 Données mises à jour à chaque chargement.")
