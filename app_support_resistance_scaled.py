
import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import ta

st.set_page_config(page_title="AIDOGE Analyzer", layout="wide")

st.title("📊 AIDOGE Analyzer – Analyse Technique Combinée")

# واجهة المستخدم لاختيار العملة والفريم الزمني
st.sidebar.header("🔧 Paramètres de l'analyse")
symbol = st.sidebar.selectbox("Sélectionner la crypto :", ["AIDOGE/USDT"])
timeframe = st.sidebar.selectbox("Cadre temporel :", ["1m", "5m", "15m", "1h", "1d", "1w"])

# إعداد البورصة
exchange = ccxt.okx()
symbol_okx = symbol.replace("/", "-")

# جلب البيانات
limit = 100
ohlcv = exchange.fetch_ohlcv(symbol_okx, timeframe=timeframe, limit=limit)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

# المؤشرات الفنية
df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
macd = ta.trend.MACD(df["close"])
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()
boll = ta.volatility.BollingerBands(df["close"])
df["boll_haut"] = boll.bollinger_hband()
df["boll_bas"] = boll.bollinger_lband()

dernier_close = df["close"].iloc[-1]
rsi_value = df["rsi"].iloc[-1]
macd_value = df["macd"].iloc[-1]
macd_signal = df["macd_signal"].iloc[-1]
boll_bas = df["boll_bas"].iloc[-1]
boll_haut = df["boll_haut"].iloc[-1]

# عرض السعر
st.markdown(f"### 🪙 Prix actuel : <span style='color:#00ff99;font-size:24px;'>0.{str(int(dernier_close * 1e11)).zfill(11)}</span> USDT", unsafe_allow_html=True)

# تحليل المؤشرات
def interprétation_rsi(val):
    if val > 70: return "🔴 Suracheté"
    elif val < 30: return "🟢 Survendu"
    else: return "⏸️ Neutre"

def interprétation_macd(macd_val, signal_val):
    if macd_val > signal_val: return "📈 Haussier"
    elif macd_val < signal_val: return "📉 Baissier"
    else: return "⏸️ Neutre"

def interprétation_boll(close, bas, haut):
    if close < bas: return "🟢 Proche bas"
    elif close > haut: return "🔴 Proche haut"
    else: return "⏸️ Entre bandes"

rsi_result = interprétation_rsi(rsi_value)
macd_result = interprétation_macd(macd_value, macd_signal)
boll_result = interprétation_boll(dernier_close, boll_bas, boll_haut)

# جدول المؤشرات
st.subheader("🧾 Synthèse des indicateurs")
indicateurs = pd.DataFrame({
    "Indicateur": ["RSI", "MACD", "Bandes de Bollinger"],
    "Valeur": [f"{rsi_value:.2f}", f"{macd_value:.2e} / {macd_signal:.2e}", f"{dernier_close:.2e}"],
    "Interprétation": [rsi_result, macd_result, boll_result]
})
st.table(indicateurs)

# التوصية الاستراتيجية
st.subheader("✅ Conclusion stratégique")
if "🟢" in [rsi_result, boll_result] and "📈" in macd_result:
    st.success("🔊 Signal LONG détecté – Opportunité d'achat potentielle.")
elif "🔴" in [rsi_result, boll_result] and "📉" in macd_result:
    st.error("🔊 Signal SHORT détecté – Opportunité de vente possible.")
else:
    st.info("🕒 Signal mitigé – Attendez confirmation claire de plusieurs indicateurs.")

# --------------------- دعم ومقاومة ---------------------
st.markdown("### 📌 Niveaux de Support & Résistance")

high = df["high"].max()
low = df["low"].min()
pivot = (high + low + dernier_close) / 3

res1 = (2 * pivot) - low
res2 = pivot + (high - low)
res3 = high + 2 * (pivot - low)

sup1 = (2 * pivot) - high
sup2 = pivot - (high - low)
sup3 = low - 2 * (high - pivot)

# جدول المستويات مضروبة في 10^11
levels = {
    "Niveau": ["Support 3", "Support 2", "Support 1", "Pivot", "Résistance 1", "Résistance 2", "Résistance 3"],
    "Valeur (x10¹¹)": [f"{v * 1e11:.2f}" for v in [sup3, sup2, sup1, pivot, res1, res2, res3]]
}
st.table(pd.DataFrame(levels))

st.caption("🧠 Mise à jour automatique à chaque rechargement – Derniers 100 chandeliers")
