
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
symbols = [symbol for symbol in markets if "/USDT" in symbol]

col1, col2 = st.columns(2)
with col1:
    selected_symbol = st.selectbox("🔎 اختر العملة", symbols, index=symbols.index("AIDOGE/USDT") if "AIDOGE/USDT" in symbols else 0)
with col2:
    timeframe = st.selectbox("🕒 اختر الفريم الزمني", ["1m", "5m", "15m", "1h", "1d", "1w"])

def get_data(symbol, timeframe):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
        df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")
        return None

df = get_data(selected_symbol, timeframe)

if df is not None:
    current_price = df["close"].iloc[-1]
    st.subheader(f"💰 السعر الحالي: :green[{current_price:.12f}] USDT")

    st.markdown("## ⚙️ المؤشرات الفنية")

    rsi = ta.momentum.RSIIndicator(close=df["close"]).rsi().iloc[-1]
    macd = ta.trend.MACD(close=df["close"])
    macd_value = macd.macd_diff().iloc[-1]
    bb = ta.volatility.BollingerBands(close=df["close"])
    bb_status = "-"
    if df["close"].iloc[-1] > bb.bollinger_hband().iloc[-1]:
        bb_status = "📈 فوق النطاق العلوي"
    elif df["close"].iloc[-1] < bb.bollinger_lband().iloc[-1]:
        bb_status = "📉 تحت النطاق السفلي"
    else:
        bb_status = "داخل النطاق"

    col1, col2, col3 = st.columns(3)
    col1.metric("RSI", f"{rsi:.2f}")
    col2.metric("MACD", f"{macd_value:.2f}")
    col3.markdown(f"**Bollinger Band:** {bb_status}")

    # استنتاج عام
    st.markdown("## ✅ الاستنتاج الاستراتيجي")
    recommendation = "⚠️ إشارة غير مؤكدة – يُفضل الانتظار لمزيد من التأكيد."
    if rsi < 30 and macd_value > 0:
        recommendation = "✅ فرصة شراء – المؤشرات تدعم دخول إيجابي."
    elif rsi > 70 and macd_value < 0:
        recommendation = "❌ إشارة بيع – السوق في حالة تشبع شرائي."
    st.info(recommendation)

    # تحليل اتجاه السوق
    st.markdown("## 📊 اتجاه السوق")
    if rsi < 35 and macd_value > 0:
        market_trend = "📈 السوق في صعود قوي"
    elif rsi > 65 and macd_value < 0:
        market_trend = "📉 السوق في هبوط قوي"
    elif 45 <= rsi <= 55 and abs(macd_value) < 0.1:
        market_trend = "➖ السوق مستقر أو جانبي"
    else:
        market_trend = "⚠️ الاتجاه غير واضح حالياً"
    st.info(market_trend)

    # الدعم والمقاومة
    st.markdown("## 📌 Niveaux de Support & Résistance")
    high = df["high"].max()
    low = df["low"].min()
    pivot = (high + low + current_price) / 3
    support1 = (2 * pivot) - high
    resistance1 = (2 * pivot) - low
    support2 = pivot - (resistance1 - support1)
    resistance2 = pivot + (resistance1 - support1)
    support3 = low - 2 * (high - pivot)
    resistance3 = high + 2 * (pivot - low)

    support_resistance_data = pd.DataFrame({
        "Niveau": [
            "Support 3", "Support 2", "Support 1", "Pivot",
            "Résistance 1", "Résistance 2", "Résistance 3"
        ],
        "Valeur": [
            support3, support2, support1, pivot,
            resistance1, resistance2, resistance3
        ]
    })

    support_resistance_data["Valeur"] = support_resistance_data["Valeur"].apply(lambda x: f"{x:.12f}")
    st.table(support_resistance_data)

    st.caption("🧠 يتم التحديث تلقائياً عند كل تشغيل – يعرض أحدث 100 شمعة.")

    # أسعار الفائدة الفيدرالية وتأثيرها
    st.markdown("## 🏦 تأثير الفائدة الأمريكية")

    # مثال يدوي (يمكن استبداله بـ API لاحقاً)
    federal_rate = 5.25

    if federal_rate > 5.0:
        message = "❌ أسعار الفائدة مرتفعة - تأثير سلبي على العملات الرقمية (ضغط بيعي محتمل)."
    elif federal_rate < 2.0:
        message = "✅ أسعار الفائدة منخفضة - تأثير إيجابي على العملات الرقمية (تشجيع على الشراء)."
    else:
        message = "⚠️ أسعار الفائدة معتدلة - تأثير محدود على السوق."

    st.info(f"نسبة الفائدة الحالية: {federal_rate}%")
    st.warning(message)
