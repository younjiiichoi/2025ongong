import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.title("📈 글로벌 시가총액 Top 10 기업 주가 분석")

# Top 10 기업 티커
top10_tickers = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Saudi Aramco (2222.SR)": "2222.SR",
    "Alphabet (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Nvidia (NVDA)": "NVDA",
    "Meta (META)": "META",
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "Eli Lilly (LLY)": "LLY",
    "TSMC (TSM)": "TSM"
}

# 기업 선택
selected = st.multiselect("기업을 선택하세요 (1개 이상)", options=list(top10_tickers.keys()), default=["Apple (AAPL)", "Microsoft (MSFT)"])

if not selected:
    st.warning("⚠️ 하나 이상의 기업을 선택해 주세요.")
    st.stop()

# 날짜 범위
end = pd.Timestamp.today()
start = end - pd.DateOffset(years=1)

# 주가 데이터 가져오기
@st.cache_data
def load_prices(tickers):
    data = yf.download(tickers, start=start, end=end)['Adj Close']
    return data

tickers = [top10_tickers[name] for name in selected]

try:
    df_price = load_prices(tickers)

    # 단일 기업 선택 시 DataFrame 형식 유지
    if isinstance(df_price, pd.Series):
        df_price = df_price.to_frame()

    df_price = df_price.dropna()

    # 누적 수익률 계산
    df_return = (df_price / df_price.iloc[0] - 1) * 100

    st.subheader("📊 주가 차트")
    fig_price = px.line(df_price, x=df_price.index, y=df_price.columns, labels={"value": "가격 (USD)", "index": "날짜"}, title="주가 추이")
    st.plotly_chart(fig_price, use_container_width=True)

    st.subheader("📈 누적 수익률 (%)")
    fig_return = px.line(df_return, x=df_return.index, y=df_return.columns, labels={"value": "수익률 (%)", "index": "날짜"}, title="누적 수익률")
    st.plotly_chart(fig_return, use_container_width=True)

except Exception as e:
    st.error(f"❌ 데이터 로딩 중 오류가 발생했습니다: {e}")
