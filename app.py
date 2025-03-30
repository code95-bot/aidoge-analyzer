
import streamlit as st
import pandas as pd
import ccxt
import ta
import numpy as np

st.set_page_config(page_title="AIDOGE Analyzer Complet", layout="centered")

st.title("📊 AIDOGE Analyzer – Analyse Technique Combinée")

# ---- Données ----
exchange = ccxt.okx()
symbol = "AIDOGE/USDT"
ohlcv = exchange.fetch_ohlcv(symbol, timeframe="5m", limit=100)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

# ---- Indicateurs ----
df["RSI"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
macd = ta.trend.MACD(close=df["close"])
df["MACD"] = macd.macd()
df["MACD_signal"] = macd.macd_signal()
boll = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
df["BOLL_upper"] = boll.bollinger_hband()
df["BOLL_lower"] = boll.bollinger_lband()

# ---- Dernières valeurs ----
last_close = df["close"].iloc[-1]
rsi = df["RSI"].iloc[-1]
macd_val = df["MACD"].iloc[-1]
macd_sig = df["MACD_signal"].iloc[-1]
boll_up = df["BOLL_upper"].iloc[-1]
boll_low = df["BOLL_lower"].iloc[-1]

# ---- Affichage du prix actuel ----
st.markdown(f"### 💰 Prix actuel : `{last_close:.12f}` USDT")

# ---- Tableau des indicateurs ----
st.subheader("📋 Synthèse des indicateurs")

rsi_status = "🔼 Surachat" if rsi > 70 else "🔽 Survente" if rsi < 30 else "⏸️ Neutre"
macd_status = "📈 Haussier" if macd_val > macd_sig else "📉 Baissier" if macd_val < macd_sig else "⏸️ Neutre"
boll_status = "🔽 Proche bas" if last_close <= boll_low * 1.01 else "🔼 Proche haut" if last_close >= boll_up * 0.99 else "⏸️ Au milieu"

data = {
    "Indicateur": ["RSI", "MACD", "Bandes de Bollinger"],
    "Valeur": [f"{rsi:.2f}", f"{macd_val:.2e} / {macd_sig:.2e}", f"{last_close:.2e}"],
    "Interprétation": [rsi_status, macd_status, boll_status],
}
st.table(pd.DataFrame(data))

# ---- Recommandation finale ----
st.subheader("✅ Conclusion stratégique")

if rsi < 30 and macd_val > macd_sig and last_close <= boll_low * 1.01:
    st.success("🟢 Forte opportunité LONG détectée – Tous les indicateurs sont favorables à l'achat.")
elif rsi > 70 and macd_val < macd_sig and last_close >= boll_up * 0.99:
    st.error("🔴 Forte pression de vente – Risque de retournement, possible SHORT.")
else:
    st.info("🕒 Signal mitigé – Attendez confirmation claire de plusieurs indicateurs.")

st.caption("🧠 Mise à jour automatique à chaque rechargement. Derniers 100 chandeliers en 5 min.")
