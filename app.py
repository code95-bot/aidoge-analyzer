
import streamlit as st
import pandas as pd
import numpy as np
import requests
import ta
import ccxt
import matplotlib.pyplot as plt

# إعداد الصفحة
st.set_page_config(page_title="AIDOGE Analyzer + 🐳 Whale Activity", layout="wide")
st.title("📊 AIDOGE Analyzer + 🐳 Whale Activity")
st.markdown("✅ تمّ دمج التحليل الفني مع نشاط الحيتان بنجاح")

# 🛠️ إدخال المستخدم
col1, col2 = st.columns(2)
with col1:
    selected_symbol = st.selectbox("🔍 اختر العملة", ["AIDOGE/USDT", "BTC/USDT", "ETH/USDT"])
with col2:
    timeframe = st.selectbox("⏱️ اختر الفريم الزمني", ["1m", "5m", "15m", "1h", "1d", "1w"])

# 🧠 إعداد API وتحميل البيانات من Binance
exchange = ccxt.binance()
symbol = selected_symbol
limit = 100

try:
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # مؤشرات فنية
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df["close"])
    df["bb_low"] = bb.bollinger_lband()
    df["bb_high"] = bb.bollinger_hband()

    latest = df.iloc[-1]

    st.subheader("🧾 التحليل الفني")
    rsi_value = round(latest["rsi"], 2)
    macd_diff = latest["macd"] - latest["macd_signal"]
    bb_position = "قريب من الحد السفلي" if latest["close"] < latest["bb_low"] else "ضمن النطاق"

    rsi_signal = "🔵 محايد"
    if rsi_value < 30:
        rsi_signal = "🟢 شراء"
    elif rsi_value > 70:
        rsi_signal = "🔴 بيع"

    macd_signal = "🔵 محايد"
    if macd_diff > 0:
        macd_signal = "🟢 صعود"
    elif macd_diff < 0:
        macd_signal = "🔴 هبوط"

    # جدول
    st.table(pd.DataFrame({
        "المؤشر": ["RSI", "MACD", "Bollinger"],
        "القيمة": [rsi_value, f"{latest['macd']:.2e} / {latest['macd_signal']:.2e}", latest["bb_low"]],
        "الإشارة": [rsi_signal, macd_signal, bb_position]
    }))

    # دعم ومقاومة
    st.subheader("📌 مستويات الدعم والمقاومة")
    pivot = (latest["high"] + latest["low"] + latest["close"]) / 3
    r1 = 2 * pivot - latest["low"]
    r2 = pivot + (latest["high"] - latest["low"])
    r3 = latest["high"] + 2 * (pivot - latest["low"])
    s1 = 2 * pivot - latest["high"]
    s2 = pivot - (latest["high"] - latest["low"])
    s3 = latest["low"] - 2 * (latest["high"] - pivot)

    sr_df = pd.DataFrame({
        "المستوى": ["Support 3", "Support 2", "Support 1", "Pivot", "Resistance 1", "Resistance 2", "Resistance 3"],
        "القيمة": [s3, s2, s1, pivot, r1, r2, r3]
    })
    sr_df["القيمة"] = sr_df["القيمة"].apply(lambda x: f"{x:.20f}")
    st.dataframe(sr_df)

except Exception as e:
    st.error(f"خطأ في التحليل الفني: {e}")

# 🐳 تحليل نشاط الحيتان باستخدام Sentiment API
st.subheader("📊 تحليل الحيتان (Market Sentiment)")

try:
    api_key = "kw4znozi5u6m56et_jiriurfoyaqfixxo"  # ← هذا هو API KEY الخاص بك
    url = "https://api.senticrypt.io/v1/market-sentiment"
    headers = {"x-api-key": api_key}
    response = requests.get(url, headers=headers)
    data = response.json()

    if "sentiment" in data:
        sentiment = data["sentiment"]
        st.metric("📈 مؤشر الحيتان", f"{sentiment:.2f}")
        if sentiment > 0.5:
            st.success("🐳 نشاط الحيتان إيجابي! قد يكون السوق صاعدًا.")
        elif sentiment < -0.5:
            st.error("🐳 نشاط الحيتان سلبي! احذر من الضغط البيعي.")
        else:
            st.info("⚖️ النشاط الحيتاني متوازن حاليًا.")
    else:
        st.warning("لم يتم العثور على بيانات شعور السوق.")

except Exception as e:
    st.error(f"خطأ أثناء استدعاء بيانات الحيتان: {e}")

# ✅ ملحوظة
st.caption("💡 يتم التحديث تلقائيًا مع كل إعادة تحميل — يعرض أحدث 100 شمعة")
