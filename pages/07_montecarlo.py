import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.interpolate import interp1d

st.set_page_config(page_title="Ice Cream Monte Carlo", layout="centered")
st.title("🍦 Ice Cream Profits & Temperature 분석")

# 1️⃣ CSV 업로드
uploaded_file = st.file_uploader("📁 ice_cream_profits.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        st.success("✅ CSV 파일 로드 완료!")
        st.write("🔍 컬럼 확인:", df.columns.tolist())

        if "Temperature" not in df.columns or "Ice Cream Profits" not in df.columns:
            st.error("❌ 'Temperature' 또는 'Ice Cream Profits' 컬럼이 없습니다.")
            st.stop()

        # 2️⃣ 산점도 출력
        st.subheader("1️⃣ Temperature vs Ice Cream Profits")
        fig = px.scatter(df, x="Temperature", y="Ice Cream Profits", trendline="ols")
        st.plotly_chart(fig, use_container_width=True)

        # 3️⃣ 적분용 함수 보간
        x = df["Temperature"].values
        y = df["Ice Cream Profits"].values
        a, b = float(min(x)), float(max(x))
        f_interp = interp1d(x, y, kind='linear', fill_value="extrapolate")
        real_area = np.trapz(y, x)

        N = 10000
        results = {}

        st.subheader("2️⃣ 몬테카를로 적분 (3가지 방식)")

        # Uniform Sampling
        x1 = np.random.uniform(a, b, N)
        area1 = (b - a) * np.mean(f_interp(x1))
        error1 = abs(area1 - real_area)
        results["Uniform"] = {"value": area1, "error": error1}

        # Stratified Sampling
        strata = np.linspace(a, b, N + 1)
        mids = (strata[:-1] + strata[1:]) / 2
        area2 = (b - a) / N * np.sum(f_interp(mids))
        error2 = abs(area2 - real_area)
        results["Stratified"] = {"value": area2, "error": error2}

        # Importance Sampling
        u = np.random.uniform(0, 1, N)
        x3 = a + (b - a) * np.sqrt(u)
        p_x = 2 * (x3 - a) / (b - a)**2
        w = f_interp(x3) / p_x
        area3 = np.mean(w)
        error3 = abs(area3 - real_area)
        results["Importance"] = {"value": area3, "error": error3}

        # 결과 테이블
        result_df = pd.DataFrame([
            {"Algorithm": k, "Estimated Area": v["value"], "Absolute Error": v["error"]}
            for k, v in results.items()
        ]).sort_values("Absolute Error")

        st.table(result_df.style.format({"Estimated Area": "{:.2f}", "Absolute Error": "{:.4f}"}))

        # 오차 최소 알고리즘 설명
        best = result_df.iloc[0]["Algorithm"]
        st.subheader("3️⃣ 오차가 가장 작은 알고리즘: " + f"**{best} Sampling**")

        if best == "Uniform":
            explanation = """
            Uniform Sampling은 전체 구간에서 동일 확률로 난수를 생성하는 방식입니다.  
            간단하지만 데이터 분포가 고르지 않으면 정확도가 떨어질 수 있습니다.
            """
        elif best == "Stratified":
            explanation = """
            Stratified Sampling은 전체 구간을 일정 간격으로 나누고, 각 구간을 대표하는 점(중앙값 등)을 샘플링합니다.  
            데이터가 고르게 퍼지지 않은 경우에도 안정적인 적분값을 제공합니다.
            """
        elif best == "Importance":
            explanation = """
            Importance Sampling은 함수값이 높은 구간에서 더 많은 샘플을 생성합니다.  
            이 방식은 효율적으로 정확도를 높이고, 오차를 줄이는 데 매우 효과적입니다.
            """

        st.markdown(f"🧠 **{best} Sampling 설명:**\n\n{explanation.strip()}")

    except Exception as e:
        st.error(f"❌ CSV 처리 중 오류 발생: {e}")
else:
    st.info("📂 CSV 파일을 먼저 업로드해 주세요. ('Temperature', 'Ice Cream Profits' 컬럼 필요)")
