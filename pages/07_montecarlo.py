import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.interpolate import interp1d

st.set_page_config(page_title="Ice Cream Monte Carlo", layout="centered")
st.title("🍦 Ice Cream Profits & Temperature 분석")

uploaded_file = st.file_uploader("📁 ice_cream_profits.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        st.success("✅ CSV 파일 로드 완료!")
        st.write("🔍 컬럼 확인:", df.columns.tolist())

        if "Temperature" not in df.columns or "Ice Cream Profits" not in df.columns:
            st.error("❌ 'Temperature' 또는 'Ice Cream Profits' 컬럼이 없습니다.")
            st.stop()

        st.subheader("1️⃣ Temperature vs Ice Cream Profits")
        fig = px.scatter(df, x="Temperature", y="Ice Cream Profits", trendline="ols")
        st.plotly_chart(fig, use_container_width=True)

        # 보간 함수
        x = df["Temperature"].values
        y = df["Ice Cream Profits"].values
        a, b = float(min(x)), float(max(x))
        f_interp = interp1d(x, y, kind='linear', fill_value="extrapolate")
        real_area = np.trapz(y, x)

        N = 10000
        results = {}

        st.subheader("2️⃣ 몬테카를로 적분 (3가지 방식)")

        # 1. Uniform Sampling
        x1 = np.random.uniform(a, b, N)
        area1 = (b - a) * np.mean(f_interp(x1))
        error1 = abs(area1 - real_area)
        results["Uniform"] = {"value": area1, "error": error1}

        # 2. Stratified Sampling (난수 기반 계층 샘플링)
        strata = np.linspace(a, b, N + 1)
        samples = np.array([
            np.random.uniform(strata[i], strata[i + 1])
            for i in range(N)
        ])
        area2 = (b - a) / N * np.sum(f_interp(samples))
        error2 = abs(area2 - real_area)
        results["Stratified"] = {"value": area2, "error": error2}

        # 3. Importance Sampling
        u = np.random.uniform(0, 1, N)
        x3 = a + (b - a) * np.sqrt(u)
        p_x = 2 * (x3 - a) / (b - a)**2
        w = f_interp(x3) / p_x
        area3 = np.mean(w)
        error3 = abs(area3 - real_area)
        results["Importance"] = {"value": area3, "error": error3}

        # 결과 출력
        result_df = pd.DataFrame([
            {"Algorithm": k, "Estimated Area": v["value"], "Absolute Error": v["error"]}
            for k, v in results.items()
        ]).sort_values("Absolute Error")

        st.table(result_df.style.format({"Estimated Area": "{:.2f}", "Absolute Error": "{:.4f}"}))

        # 3️⃣ 최적 알고리즘 설명
        best = result_df.iloc[0]["Algorithm"]
        st.subheader("3️⃣ 오차가 가장 작은 알고리즘: " + f"**{best} Sampling**")

        if best == "Uniform":
            explanation = """
            Uniform Sampling은 전체 구간에서 동일한 확률로 난수를 추출합니다.  
            간단하고 빠르지만, 함수 값이 특정 구간에 집중되어 있을 경우 효율이 떨어질 수 있습니다.
            """
        elif best == "Stratified":
            explanation = """
            Stratified Sampling은 구간을 N개의 계층으로 나누고, 각 계층 내부에서 난수를 1개씩 추출합니다.  
            구간 전체를 고르게 대표하면서도 난수성까지 유지하여 매우 안정적인 결과를 제공합니다.
            """
        elif best == "Importance":
            explanation = """
            Importance Sampling은 함수 값이 클 것으로 예상되는 구간에 더 많은 샘플을 생성합니다.  
            난수는 비선형 분포에서 생성되며, 각 샘플은 가중치로 보정됩니다.  
            특히 특정 구간에서 값이 급격히 증가하는 함수에 매우 효과적입니다.
            """

        st.markdown(f"🧠 **{best} Sampling 설명:**\n\n{explanation.strip()}")

    except Exception as e:
        st.error(f"❌ CSV 처리 중 오류 발생: {e}")
else:
    st.info("📂 CSV 파일을 먼저 업로드해 주세요. ('Temperature', 'Ice Cream Profits' 컬럼 필요)")
