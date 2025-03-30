
import streamlit as st
import pandas as pd
import ccxt
import ta
import numpy as np

st.set_page_config(page_title="AIDOGE Analyzer Plus", layout="centered")

st.title("📊 Crypto Analyzer – Analyse Technique Multi-Cadre")

# --------- Interface Utilisateur ---------
st.sidebar.header("🛠️ Paramètres de l'analyse")

# Liste des cryptos disponibles (peut être élargie)
cryptos = ["AIDOGE/USDT", "DOGE/USDT", "BTC/USDT", "ETH/USDT", "PEPE/USDT"]
selected_symbol = st.sidebar.selectbox("Sélectionner la crypto :", cryptos)

# Sélection de la période temporelle
timeframes = {
    "1 Minute": "1m",
    "5 Minutes": "5m",
    "15 Minutes": "15m",
    "1 Heure": "1h",
    "1 Jour": "1d",
    "1 Semaine": "1w"
}
selected_timeframe = st.sidebar.selectbox("Cadre temporel :", list(timeframes.keys()))
tf_value = timeframes[selected_timeframe]

# --------- Chargement des données ---------
exchange = ccxt.okx()
ohlcv = exchange.fetch_ohlcv(selected_symbol, timeframe=tf_value, limit=100)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

# --------- Indicateurs Techniques ---------
df["RSI"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
macd = ta.trend.MACD(close=df["close"])
df["MACD"] = macd.macd()
df["MACD_signal"] = macd.macd_signal()
boll = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
df["BOLL_upper"] = boll.bollinger_hband()
df["BOLL_lower"] = boll.bollinger_lband()

# Dernières valeurs
last_close = df["close"].iloc[-1]
rsi = df["RSI"].iloc[-1]
macd_val = df["MACD"].iloc[-1]
macd_sig = df["MACD_signal"].iloc[-1]
boll_up = df["BOLL_upper"].iloc[-1]
boll_low = df["BOLL_lower"].iloc[-1]

# --------- Affichage des résultats ---------
st.markdown(f"### 💰 Prix actuel ({selected_symbol}) sur {selected_timeframe} : `{last_close:.12f}` USDT")

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

# --------- Recommandation Finale ---------
st.subheader("✅ Conclusion stratégique")

if rsi < 30 and macd_val > macd_sig and last_close <= boll_low * 1.01:
    st.success("🟢 Forte opportunité LONG détectée – Tous les indicateurs sont favorables à l'achat.")
    st.audio("https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg", format="audio/ogg")
elif rsi > 70 and macd_val < macd_sig and last_close >= boll_up * 0.99:
    st.error("🔴 Forte pression de vente – Risque de retournement, possible SHORT.")
    st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg", format="audio/ogg")
else:
    st.info("🕒 Signal mitigé – Attendez confirmation claire de plusieurs indicateurs.")

st.caption("🔄 Mise à jour automatique à chaque rechargement – Derniers 100 chandeliers")
