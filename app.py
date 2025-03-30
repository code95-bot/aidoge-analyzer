# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import ccxt
import numpy as np
import ta

st.set_page_config(page_title="AIDOGE Analyzer", layout="wide")

st.title("📊 AIDOGE Analyzer")
st.markdown("✅ تم دمج المؤشرات الفنية مع التحليل الاستراتيجي بنجاح")

# إعدادات
exchange = ccxt.okx()
markets = exchange.load_markets()
symbols = sorted([s for s in markets if "/USDT" in s])

symbol = st.selectbox("🔍 اختر العملة", symbols, index=symbols.index("AIDOGE/USDT") if "AIDOGE/USDT" in symbols else 0)
timeframes = {"1m": "1 دقيقة", "5m": "5 دقائق", "15m": "15 دقيقة", "1h": "1 ساعة", "1d": "1 يوم", "1w": "1 أسبوع"}
tf_key = st.selectbox("🕒 اختر الفريم الزمني", list(timeframes.keys()), format_func=lambda x: timeframes[x])

# بيانات
data = exchange.fetch_ohlcv(symbol, timeframe=tf_key, limit=100)
df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("timestamp", inplace=True)

# المؤشرات
df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
macd = ta.trend.MACD(df["close"])
df["macd"] = macd.macd_diff()
bb = ta.volatility.BollingerBands(df["close"])
df["bb_upper"] = bb.bollinger_hband()
df["bb_lower"] = bb.bollinger_lband()

price = df["close"].iloc[-1]
rsi_val = df["rsi"].iloc[-1]
macd_val = df["macd"].iloc[-1]
bb_pos = "داخل النطاق"
if price > df["bb_upper"].iloc[-1]:
    bb_pos = "فوق الباند العلوي"
elif price < df["bb_lower"].iloc[-1]:
    bb_pos = "تحت الباند السفلي"

col1, col2 = st.columns(2)
with col1:
    st.metric("السعر الحالي:", f"{price:.12f} USDT", delta=None)
with col2:
    st.subheader("⚙️ المؤشرات الفنية")
    st.write(f"**RSI:** `{rsi_val:.2f}` - {'شراء' if rsi_val < 30 else 'بيع' if rsi_val > 70 else 'محايد'}")
    st.write(f"**MACD:** `{macd_val:.2f}` - {'اتجاه صاعد' if macd_val > 0 else 'اتجاه هابط' if macd_val < 0 else 'محايد'}")
    st.write(f"**Bollinger Band:** {bb_pos}")

# الاستنتاج
st.markdown("### ✅ الاستنتاج الاستراتيجي")
if rsi_val < 30 and macd_val > 0:
    st.success("إشارة شراء مؤكدة – يمكنك التفكير في Long")
elif rsi_val > 70 and macd_val < 0:
    st.error("إشارة بيع مؤكدة – يمكن التفكير في Short")
else:
    st.warning("إشارة غير مؤكدة – يُفضل الانتظار لمزيد من التأكيد.")

# الدعم والمقاومة
pivot = (df["high"].iloc[-1] + df["low"].iloc[-1] + price) / 3
r1 = 2 * pivot - df["low"].iloc[-1]
s1 = 2 * pivot - df["high"].iloc[-1]
r2 = pivot + (r1 - s1)
s2 = pivot - (r1 - s1)
r3 = df["high"].iloc[-1] + 2 * (pivot - df["low"].iloc[-1])
s3 = df["low"].iloc[-1] - 2 * (df["high"].iloc[-1] - pivot)

levels = {
    "Support 3": s3,
    "Support 2": s2,
    "Support 1": s1,
    "Pivot": pivot,
    "Resistance 1": r1,
    "Resistance 2": r2,
    "Resistance 3": r3,
}

support_df = pd.DataFrame(list(levels.items()), columns=["Niveau", "Valeur"])
support_df["Valeur"] = support_df["Valeur"].apply(lambda x: f"{x:.12f}")
st.markdown("### 📌 Niveaux de Support & Résistance")
st.table(support_df)