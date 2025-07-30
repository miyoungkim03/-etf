import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import plotly.graph_objs as go

# 기본 설정
st.set_page_config(layout="wide")
st.title("📈 ETF 예측 웹앱 (S&P500, QYLD, SCHD 등)")
st.markdown("👉 주요 ETF를 예측하고, RSI 및 이동평균 기반 매수 타이밍을 확인할 수 있어요.")

# ETF 리스트
etfs = ["SPY", "QQQ", "QYLD", "JEPI", "SCHD", "VOO", "TLT", "AGNC"]
selected_etf = st.selectbox("📊 관심 ETF 선택:", etfs)

# 데이터 불러오기
@st.cache_data
def load_data(ticker):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=365 * 2)
    data = yf.download(ticker, start=start, end=end)
    data['MA20'] = data['Close'].rolling(20).mean()
    data['RSI'] = compute_rsi(data['Close'])
    return data

# RSI 계산 함수
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 차트 그리기
def plot_chart(df, name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='가격'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines', name='20일선'))
    fig.update_layout(title=f"{name} 가격 추이", xaxis_title="날짜", yaxis_title="가격")
    st.plotly_chart(fig, use_container_width=True)

    # RSI 차트
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI'))
    fig_rsi.add_hline(y=30, line_dash='dot', line_color='green')
    fig_rsi.add_hline(y=70, line_dash='dot', line_color='red')
    fig_rsi.update_layout(title=f"{name} RSI (상대강도지수)", xaxis_title="날짜", yaxis_title="RSI")
    st.plotly_chart(fig_rsi, use_container_width=True)

# 예측 신호
def signal(df):
    last = df.iloc[-1]
    if last['RSI'] < 30 and last['Close'] > last['MA20']:
        return "✅ 매수 유망 (RSI 과매도 & 20일선 위)"
    elif last['RSI'] > 70:
        return "⚠️ 과열 신호 (RSI 과매수)"
    else:
        return "⏳ 관망"

# 실행
df = load_data(selected_etf)
plot_chart(df, selected_etf)
st.subheader("📌 현재 예측 신호")
st.write(signal(df))
