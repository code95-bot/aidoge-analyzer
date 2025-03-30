
import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import ta

st.set_page_config(page_title="AIDOGE Analyzer", layout="wide")

# واجهة المستخدم
st.title("📊 AIDOGE Analyzer")
st.markdown("### اختر العملة والفريم الزمني:")

exchange = ccxt.okx()
markets = exchange.load_markets()
symbols = sorted([s for s in markets if "/USDT" in s])
symbol = st.selectbox("اختر العملة", symbols, index=symbols.index("AIDOGE/USDT") if "AIDOGE/USDT" in symbols else 0)

timeframes = {
    "1 دقيقة": "1m", "5 دقائق": "5m", "15 دقيقة": "15m",
    "1 ساعة": "1h", "يومي": "1d", "أسبوعي": "1w"
}
tf_display = list(timeframes.keys())
tf_select = st.selectbox("اختر الفريم الزمني", tf_display)
tf = timeframes[tf_select]

def get_ohlcv(symbol, timeframe, limit=100):
    try:
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        st.error(f"فشل تحميل البيانات: {e}")
        return pd.DataFrame()

def calculate_indicators(df):
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    macd = ta.trend.MACD(df["close"])
    df["MACD"] = macd.macd_diff()
    boll = ta.volatility.BollingerBands(df["close"])
    df["Bollinger_H"] = boll.bollinger_hband()
    df["Bollinger_L"] = boll.bollinger_lband()
    df["EMA50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    df["EMA200"] = ta.trend.EMAIndicator(df["close"], window=200).ema_indicator()
    return df

def interpret_signals(df):
    rsi = df["RSI"].iloc[-1]
    macd = df["MACD"].iloc[-1]
    price = df["close"].iloc[-1]
    upper = df["Bollinger_H"].iloc[-1]
    lower = df["Bollinger_L"].iloc[-1]
    ema50 = df["EMA50"].iloc[-1]
    ema200 = df["EMA200"].iloc[-1]

    rsi_status = "شراء" if rsi < 30 else "بيع" if rsi > 70 else "محايد"
    macd_status = "اتجاه صاعد" if macd > 0 else "اتجاه هابط"
    bb_status = "تحت الباند السفلي" if price < lower else "فوق الباند العلوي" if price > upper else "داخل النطاق"
    ema_trend = "صاعد" if ema50 > ema200 else "هابط"

    signals = {
        "RSI": (rsi, rsi_status),
        "MACD": (macd, macd_status),
        "Bollinger Band": (price, bb_status),
        "EMA الاتجاه": ema_trend
    }

    # تحليل استراتيجي بسيط
    if rsi < 30 and macd > 0 and ema50 > ema200:
        conclusion = "✅ إشارة شراء قوية"
    elif rsi > 70 and macd < 0 and ema50 < ema200:
        conclusion = "❌ إشارة بيع قوية"
    else:
        conclusion = "⚠️ إشارة غير مؤكدة – يُفضل الانتظار لمزيد من التأكيد."

    return signals, conclusion

def support_resistance(df):
    pivot = (df["high"] + df["low"] + df["close"]) / 3
    r1 = 2 * pivot - df["low"]
    s1 = 2 * pivot - df["high"]
    r2 = pivot + (r1 - s1)
    s2 = pivot - (r1 - s1)
    r3 = df["high"] + 2 * (pivot - df["low"])
    s3 = df["low"] - 2 * (df["high"] - pivot)

    return {
        "Support 3": s3.iloc[-1],
        "Support 2": s2.iloc[-1],
        "Support 1": s1.iloc[-1],
        "Pivot": pivot.iloc[-1],
        "Resistance 1": r1.iloc[-1],
        "Resistance 2": r2.iloc[-1],
        "Resistance 3": r3.iloc[-1]
    }

# تنفيذ التحليل
df = get_ohlcv(symbol, tf)
if not df.empty:
    df = calculate_indicators(df)
    signals, summary = interpret_signals(df)

    st.markdown(f"### السعر الحالي: `{df['close'].iloc[-1]:.12f}` USDT")

    st.header("⚙️ المؤشرات الفنية")
    for k, (v, s) in signals.items():
        st.write(f"**{k}:** {v:.2f} – {s}" if isinstance(v, float) else f"**{k}:** {s}")

    st.success("الاستنتاج الاستراتيجي")
    st.info(summary)

    st.subheader("📌 Niveaux de Support & Résistance")
    sr = support_resistance(df)
    df_sr = pd.DataFrame(sr.items(), columns=["Niveau", "Valeur"])
    st.dataframe(df_sr)
