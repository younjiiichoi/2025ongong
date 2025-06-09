import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="글로벌 Top10 주가 분석", layout="wide")
st.title("📈 글로벌 시가총액 Top 10 기업 주가 분석")

# 시가총액 Top 10 기업 티커
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
selected = st.multiselect(
    "분석할 기업을 선택하세요 (1개 이상)", 
    options=list(top10_tickers.keys()), 
    default=["Apple (AAPL)", "Microsoft (MSFT)"]
)

if not selected:
    st.warning("⚠️ 최소 하나의 기업을 선택해 주세요.")
    st.stop()

# 날짜 설정
end = pd.Timestamp.today()
start = end - pd.DateOffset(years=1)

# 주가 데이터 불러오기 함수
@st.cache_data
def load_prices(tickers):
    data = yf.download(tickers, start=start, end=end)
    if "Close" in data.columns:
        return data["Close"]
    elif isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        return data
    else:
        raise ValueError("❌ 유효한 'Close' 데이터를 찾을 수 없습니다.")

tickers = [top10_tickers[name] for name in selected]

try:
    df_price = load_prices(tickers)

    # 단일 선택 시 Series → DataFrame 변환
    if isinstance(df_price, pd.Series):
        df_price = df_price.to_frame(name=tickers[0])

    if df_price.empty:
        st.warning("🔍 선택한 기업의 데이터가 없습니다. 다른 기업을 선택해 주세요.")
        st.stop()

    # 누적 수익률 계산
    df_return = (df_price / df_price.iloc[0] - 1) * 100

    # 주가 시각화
    st.subheader("📊 주가 추이 (최근 1년)")
    fig_price = px.line(
        df_price,
        x=df_price.index,
        y=df_price.columns,
        labels={"value": "주가 (USD)", "index": "날짜"},
        title="최근 1년 주가"
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # 누적 수익률 시각화
    st.subheader("📈 누적 수익률 (%)")
    fig_return = px.line(
        df_return,
        x=df_return.index,
        y=df_return.columns,
        labels={"value": "수익률 (%)", "index": "날짜"},
        title="누적 수익률 변화"
    )
    st.plotly_chart(fig_return, use_container_width=True)

except Exception as e:
    st.error(f"❌ 데이터 로딩 중 오류 발생: {e}")
