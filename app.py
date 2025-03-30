
import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import ta
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📊 AIDOGE Analyzer – التحليل الفني بالذكاء الاصطناعي")

# --- إعدادات ---
st.sidebar.header("⚙️ إعدادات التحليل")
exchange = ccxt.okx()
markets = exchange.load_markets()
symbols = [s for s in markets if "/USDT" in s]
selected_symbol = st.sidebar.selectbox("🔍 اختر العملة", symbols, index=symbols.index("AIDOGE/USDT"))
timeframes = ["1m", "5m", "15m", "1h", "1d", "1w"]
selected_timeframe = st.sidebar.selectbox("⏱️ اختر الفريم الزمني", timeframes)

# --- جلب البيانات ---
def get_ohlcv(symbol, timeframe):
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

try:
    df = get_ohlcv(selected_symbol, selected_timeframe)
    close = df["close"]

    # --- المؤشرات الفنية ---
    rsi = ta.momentum.RSIIndicator(close).rsi()
    macd = ta.trend.MACD(close)
    bb = ta.volatility.BollingerBands(close)

    macd_line = macd.macd()
    macd_signal = macd.macd_signal()
    bb_middle = bb.bollinger_mavg()
    bb_lower = bb.bollinger_lband()
    bb_upper = bb.bollinger_hband()

    current_price = close.iloc[-1]

    # --- استنتاج ---
    st.subheader("💹 السعر الحالي:")
    st.markdown(f"<h2 style='color:lime'>{current_price:.12f} USDT</h2>", unsafe_allow_html=True)

    st.subheader("📊 المؤشرات الفنية")
    analysis = []

    rsi_value = rsi.iloc[-1]
    if rsi_value > 70:
        analysis.append("تشبع شراء")
    elif rsi_value < 30:
        analysis.append("تشبع بيع")
    else:
        analysis.append("محايد")

    macd_diff = macd_line.iloc[-1] - macd_signal.iloc[-1]
    if macd_diff > 0:
        analysis.append("اتجاه صاعد")
    elif macd_diff < 0:
        analysis.append("اتجاه هابط")
    else:
        analysis.append("محايد")

    if current_price < bb_lower.iloc[-1]:
        analysis.append("قريب من الدعم")
    elif current_price > bb_upper.iloc[-1]:
        analysis.append("قريب من المقاومة")
    else:
        analysis.append("داخل النطاق")

    st.write("**RSI:**", round(rsi_value, 2), "-", analysis[0])
    st.write("**MACD:**", round(macd_diff, 8), "-", analysis[1])
    st.write("**Bollinger Band:**", "-", analysis[2])

    # --- الدعم والمقاومة ---
    st.subheader("📌 Niveaux de Support & Résistance")
    high = df["high"].iloc[-1]
    low = df["low"].iloc[-1]
    pivot = (high + low + current_price) / 3
    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    r3 = r1 + (high - low)
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)
    s3 = s1 - (high - low)

    levels = {
        "Support 3": s3,
        "Support 2": s2,
        "Support 1": s1,
        "Pivot": pivot,
        "Résistance 1": r1,
        "Résistance 2": r2,
        "Résistance 3": r3,
    }

    support_df = pd.DataFrame(levels.items(), columns=["Niveau", "Valeur"])
    st.dataframe(support_df.style.format({"Valeur": "{:.12f}"}), use_container_width=True)

except Exception as e:
    st.error(f"خطأ أثناء التحليل: {e}")
