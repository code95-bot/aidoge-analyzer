import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import ta

st.set_page_config(page_title="AIDOGE Analyzer", layout="wide")

st.title("📊 AIDOGE Analyzer – توصيات مرنة حسب ظروف السوق")

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
    ema50 = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator().iloc[-1]
    ema200 = ta.trend.EMAIndicator(df["close"], window=200).ema_indicator().iloc[-1]

    st.write(f"**RSI:** {rsi:.2f} | **MACD:** {macd_val:.2f} | **EMA50:** {ema50:.4f} | **EMA200:** {ema200:.4f}")

    st.markdown("## ✅ توصية التداول")

    recommendation = "⏸️ لا توجد فرصة واضحة – يُفضل الانتظار."
    if rsi < 30 and macd_val > 0 and ema50 > ema200:
        recommendation = "✅ إشارة شراء قوية – فرصة دخول قوية (LONG)"
    elif rsi > 70 and macd_val < 0 and ema50 < ema200:
        recommendation = "❌ إشارة بيع قوية – فرصة دخول قوية (SHORT)"
    elif 30 <= rsi <= 50 and macd_val > 0 and ema50 >= ema200 * 0.98:
        recommendation = "✅ فرصة شراء محتملة – دخول سريع لربح صغير"
    elif 50 < rsi < 70 and macd_val < 0 and ema50 <= ema200 * 1.02:
        recommendation = "❌ فرصة بيع محتملة – دخول سريع لربح صغير"

    st.info(recommendation)