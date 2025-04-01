import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import ta

st.set_page_config(page_title="AIDOGE Analyzer", layout="wide")

st.title("📊 AIDOGE Analyzer")
st.markdown("✅ تحليل فني فوري لعملات OKX")

exchange = ccxt.okx()
markets = exchange.load_markets()
symbols = sorted([s for s in markets if "/USDT" in s])
symbol = st.selectbox("🔍 اختر العملة", symbols, index=symbols.index("AIDOGE/USDT") if "AIDOGE/USDT" in symbols else 0)

timeframes = {"1 دقيقة": "1m", "5 دقائق": "5m", "15 دقيقة": "15m", "1 ساعة": "1h", "يومي": "1d", "أسبوعي": "1w"}
tf_display = list(timeframes.keys())
tf_select = st.selectbox("🕒 اختر الفريم الزمني", tf_display)
tf = timeframes[tf_select]

def get_data(symbol, timeframe):
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

df = get_data(symbol, tf)

if not df.empty:
    price = df["close"].iloc[-1]
    st.subheader(f"💰 السعر الحالي: :green[{price:.12f}] USDT")

    st.markdown("## ⚙️ المؤشرات الفنية")

    rsi = ta.momentum.RSIIndicator(df["close"]).rsi().iloc[-1]
    macd_val = ta.trend.MACD(df["close"]).macd_diff().iloc[-1]
    bb = ta.volatility.BollingerBands(df["close"])
    bb_status = "-"
    if price > bb.bollinger_hband().iloc[-1]:
        bb_status = "📈 فوق النطاق العلوي"
    elif price < bb.bollinger_lband().iloc[-1]:
        bb_status = "📉 تحت النطاق السفلي"
    else:
        bb_status = "داخل النطاق"

    ema50 = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator().iloc[-1]
    ema200 = ta.trend.EMAIndicator(df["close"], window=200).ema_indicator().iloc[-1]

    st.write(f"**RSI:** {rsi:.2f} | **MACD:** {macd_val:.2f} | **Bollinger:** {bb_status}")
    st.write(f"**EMA50:** {ema50:.4f} | **EMA200:** {ema200:.4f}")

    st.markdown("## ✅ توصية التداول")

    if rsi < 30 and macd_val > 0 and ema50 > ema200:
        st.success("✅ إشارة شراء قوية – دخول LONG مؤكد")
    elif rsi > 70 and macd_val < 0 and ema50 < ema200:
        st.error("❌ إشارة بيع قوية – دخول SHORT مؤكد")
    elif 30 <= rsi <= 50 and (macd_val > 0 or ema50 > ema200):
        st.info("✅ فرصة شراء محتملة – دخول سريع لربح صغير")
    elif 50 < rsi < 70 and (macd_val < 0 or ema50 < ema200):
        st.warning("❌ فرصة بيع محتملة – فرصة تصحيح أو مضاربة")
    else:
        st.write("⏸️ لا توجد فرصة واضحة حالياً – يُفضل الانتظار.")

    st.markdown("## 📌 الدعم والمقاومة")
    pivot = (df["high"].iloc[-1] + df["low"].iloc[-1] + price) / 3
    r1 = 2 * pivot - df["low"].iloc[-1]
    s1 = 2 * pivot - df["high"].iloc[-1]
    r2 = pivot + (r1 - s1)
    s2 = pivot - (r1 - s1)
    r3 = df["high"].iloc[-1] + 2 * (pivot - df["low"].iloc[-1])
    s3 = df["low"].iloc[-1] - 2 * (df["high"].iloc[-1] - pivot)

    sr_data = pd.DataFrame({
        "Niveau": ["Support 3", "Support 2", "Support 1", "Pivot", "Resistance 1", "Resistance 2", "Resistance 3"],
        "Valeur": [s3, s2, s1, pivot, r1, r2, r3]
    })

    sr_data["Valeur"] = sr_data["Valeur"].apply(lambda x: f"{x:.12f}")
    st.table(sr_data)