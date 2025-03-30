
import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import ta

# إعداد الصفحة
st.set_page_config(page_title="AIDOGE Analyzer", layout="wide")

st.title("📊 AIDOGE Analyzer – Analyse Technique Combinée")

# جلب العملات المتاحة من OKX
exchange = ccxt.okx()
markets = exchange.load_markets()
symbols = sorted([s for s in markets if "/USDT" in s and s.endswith("/USDT")])

# واجهة الاختيار
col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox("Sélectionner la crypto :", symbols, index=symbols.index("AIDOGE/USDT") if "AIDOGE/USDT" in symbols else 0)
with col2:
    timeframe = st.selectbox("Cadre temporel :", ["1m", "5m", "15m", "1h", "1d", "1w"], index=1)

# جلب البيانات
limit = 100
ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("timestamp", inplace=True)

# حساب المؤشرات
rsi = ta.momentum.RSIIndicator(df["close"]).rsi()
macd = ta.trend.MACD(df["close"])
boll = ta.volatility.BollingerBands(df["close"])
df["rsi"] = rsi
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()
df["boll_low"] = boll.bollinger_lband()
df["boll_high"] = boll.bollinger_hband()

# السعر الحالي
current_price = df["close"].iloc[-1]
price_change = ((df["close"].iloc[-1] - df["close"].iloc[-2]) / df["close"].iloc[-2]) * 100
price_color = "green" if price_change >= 0 else "red"

st.markdown(f"### 💰 Prix actuel : <span style='color:{price_color}; font-size:28px'> {current_price:.12f}</span> USDT", unsafe_allow_html=True)

# ملخص المؤشرات
st.subheader("📝 Synthèse des indicateurs")
latest = df.iloc[-1]
summary_data = {
    "Indicateur": ["RSI", "MACD", "Bandes de Bollinger"],
    "Valeur": [
        f"{latest['rsi']:.2f}",
        f"{latest['macd']:.2e} / {latest['macd_signal']:.2e}",
        f"{latest['close']:.2e}"
    ],
    "Interprétation": [
        "🟦 Neutre" if 40 < latest["rsi"] < 60 else ("🟩 Surachat" if latest["rsi"] > 60 else "🟥 Survente"),
        "📉 Baissier" if latest["macd"] < latest["macd_signal"] else "📈 Haussier",
        "🔽 Proche bas" if latest["close"] <= latest["boll_low"] else ("🔼 Proche haut" if latest["close"] >= latest["boll_high"] else "➖ Neutre")
    ]
}
st.dataframe(pd.DataFrame(summary_data))

# الاستنتاج
st.subheader("✅ Conclusion stratégique")
if latest["rsi"] < 35 and latest["macd"] > latest["macd_signal"] and latest["close"] <= latest["boll_low"]:
    st.success("🟢 Opportunité d'achat détectée")
elif latest["rsi"] > 65 and latest["macd"] < latest["macd_signal"] and latest["close"] >= latest["boll_high"]:
    st.error("🔴 Opportunité de vente détectée")
else:
    st.info("⏸️ Signal mitigé – Attendez confirmation claire de plusieurs indicateurs.")

# حساب خطوط الدعم والمقاومة
high = df["high"].max()
low = df["low"].min()
pivot = (high + low + current_price) / 3
r1 = 2 * pivot - low
s1 = 2 * pivot - high
r2 = pivot + (r1 - s1)
s2 = pivot - (r1 - s1)
r3 = high + 2 * (pivot - low)
s3 = low - 2 * (high - pivot)

support_resistance_data = {
    "Niveau": ["Support 3", "Support 2", "Support 1", "Pivot", "Résistance 1", "Résistance 2", "Résistance 3"],
    "Valeur (USDT)": [f"{s3:.12f}", f"{s2:.12f}", f"{s1:.12f}", f"{pivot:.12f}", f"{r1:.12f}", f"{r2:.12f}", f"{r3:.12f}"]
}
st.subheader("📌 Niveaux de Support & Résistance")
st.dataframe(pd.DataFrame(support_resistance_data))

st.caption("🧠 Mise à jour automatique à chaque rechargement – Derniers 100 chandeliers")
