
import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import ta

st.set_page_config(page_title="AIDOGE Analyzer", layout="wide")

st.markdown("## 🧠 AIDOGE Analyzer – التحليل الفني")

st.sidebar.markdown("### ⚙️ إعدادات التحليل")
exchange = ccxt.okx()

markets = exchange.load_markets()
symbols = sorted([s for s in markets if "/USDT" in s])
symbol = st.sidebar.selectbox("🔍 اختر العملة", symbols, index=symbols.index("AIDOGE/USDT"))

timeframes = {"1m": "1 دقيقة", "5m": "5 دقائق", "15m": "15 دقيقة", "1h": "1 ساعة", "1d": "1 يوم", "1w": "1 أسبوع"}
tf_key = st.sidebar.selectbox("🕒 اختر الفريم الزمني", list(timeframes.keys()), format_func=lambda x: timeframes[x])

limit = 100
ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf_key, limit=limit)
df = pd.DataFrame(ohlcv, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
df.set_index("Timestamp", inplace=True)

# تحليل المؤشرات
df["rsi"] = ta.momentum.RSIIndicator(close=df["Close"]).rsi()
macd = ta.trend.MACD(close=df["Close"])
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()
bb = ta.volatility.BollingerBands(close=df["Close"])
df["bb_upper"] = bb.bollinger_hband()
df["bb_lower"] = bb.bollinger_lband()

current = df.iloc[-1]
price = current["Close"]

st.markdown(f"### السعر الحالي: `{price:.12f}` USDT")

st.markdown("### **المؤشرات الفنية**")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**RSI:** `{current['rsi']:.2f}`")
    st.caption("محايد" if 45 < current["rsi"] < 55 else ("شراء" if current["rsi"] < 30 else "بيع"))

with col2:
    macd_val = current["macd"] - current["macd_signal"]
    st.markdown(f"**MACD:** `{macd_val:.2f}`")
    st.caption("اتجاه صاعد" if macd_val > 0 else "اتجاه هابط")

with col3:
    if price < current["bb_lower"]:
        bb_status = "تحت الباند السفلي"
    elif price > current["bb_upper"]:
        bb_status = "فوق الباند العلوي"
    else:
        bb_status = "داخل النطاق"
    st.markdown("**Bollinger Band:**")
    st.caption(bb_status)

# دعم و مقاومة
st.markdown("### 📌 Niveaux de Support & Résistance")
high = df["High"].iloc[-1]
low = df["Low"].iloc[-1]
pivot = (high + low + price) / 3
res1 = 2 * pivot - low
res2 = pivot + (high - low)
res3 = high + 2 * (pivot - low)
sup1 = 2 * pivot - high
sup2 = pivot - (high - low)
sup3 = low - 2 * (high - pivot)

s_r_data = {
    "Niveau": ["Support 3", "Support 2", "Support 1", "Pivot", "Résistance 1", "Résistance 2", "Résistance 3"],
    "Valeur": [sup3, sup2, sup1, pivot, res1, res2, res3]
}
s_r_df = pd.DataFrame(s_r_data)
s_r_df["Valeur"] = s_r_df["Valeur"].apply(lambda x: f"{x:.12f}")
st.table(s_r_df)

# استنتاج التداول
st.markdown("### ✅ **الاستنتاج الاستراتيجي**")
long_cond = current["rsi"] < 35 and macd_val > 0 and price < current["bb_lower"]
short_cond = current["rsi"] > 70 and macd_val < 0 and price > current["bb_upper"]

if long_cond:
    st.success("فرصة شراء محتملة – المؤشرات تدعم صفقة **LONG**.")
elif short_cond:
    st.error("فرصة بيع محتملة – المؤشرات تدعم صفقة **SHORT**.")
else:
    st.warning("إشارة غير مؤكدة – يُفضل الانتظار لمزيد من التأكيد.")
