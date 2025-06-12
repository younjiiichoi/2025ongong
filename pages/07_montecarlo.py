import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import zipfile
import io

st.set_page_config(page_title="Ice Cream Monte Carlo", layout="centered")
st.title("🍦 Ice Cream Sales & Temperature 분석")

# 🔽 1. ZIP 파일에서 CSV 읽기
uploaded_zip = st.file_uploader("📁 archive.zip 파일을 업로드하세요", type=["zip"])

if uploaded_zip:
    with zipfile.ZipFile(uploaded_zip) as archive:
        # 첫 번째 CSV 파일 자동 선택
        csv_name = [f for f in archive.namelist() if f.endswith(".csv")][0]
        with archive.open(csv_name) as csv_file:
            df = pd.read_csv(csv_file)

    st.success(f"✅ 파일 로드 완료: `{csv_name}`")
    
    # 컬럼 정리
    df.columns = df.columns.str.lower().str.strip()

    if "temperature" not in df.columns or "ice cream sales" not in df.columns:
        st.error("❌ 'temperature' 또는 'ice cream sales' 컬럼이 존재하지 않습니다.")
        st.stop()

    # 🔹 1단계: 산점도 그래프
    st.subheader("1️⃣ 기온 vs 아이스크림 판매량 산점도")
    fig = px.scatter(df, x="temperature", y="ice cream sales", trendline="ols")
    st.plotly_chart(fig, use_container_width=True)

    # 🔹 적분할 함수 정의 (보간 기반)
    from scipy.interpolate import interp1d
    x = df["temperature"].values
    y = df["ice cream sales"].values
    a, b = float(min(x)), float(max(x))

    f_interp = interp1d(x, y, kind='linear', fill_value="extrapolate")

    # 실제 넓이 (근사 기준값)
    real_area = np.trapz(y, x)

    N = 10000  # 샘플 수
    results = {}

    st.subheader("2️⃣ 몬테카를로 적분 (3가지 난수 알고리즘 사용)")

    # 1. Uniform Sampling
    x1 = np.random.uniform(a, b, N)
    area1 = (b - a) * np.mean(f_interp(x1))
    error1 = abs(area1 - real_area)
    results["Uniform"] = {"value": area1, "error": error1}

    # 2. Stratified Sampling
    strata = np.linspace(a, b, N + 1)
    mids = (strata[:-1] + strata[1:]) / 2
    area2 = (b - a) / N * np.sum(f_interp(mids))
    error2 = abs(area2 - real_area)
    results["Stratified"] = {"value": area2, "error": error2}

    # 3. Importance Sampling (ex: p(x) ~ (x-a)/(b-a)^2)
    u = np.random.uniform(0, 1, N)
    x3 = a + (b - a) * np.sqrt(u)
    p_x = 2 * (x3 - a) / (b - a)**2
    w = f_interp(x3) / p_x
    area3 = np.mean(w)
    error3 = abs(area3 - real_area)
    results["Importance"] = {"value": area3, "error": error3}

    # 결과 표
    result_df = pd.DataFrame([
        {"Algorithm": k, "Estimated Area": v["value"], "Absolute Error": v["error"]}
        for k, v in results.items()
    ]).sort_values("Absolute Error")

    st.table(result_df.style.format({"Estimated Area": "{:.2f}", "Absolute Error": "{:.4f}"}))

    # 🔹 3단계: 오차 최소 알고리즘 설명
    best = result_df.iloc[0]["Algorithm"]
    st.subheader("3️⃣ 오차가 가장 작은 알고리즘: " + f"**{best} Sampling**")

    if best == "Uniform":
        explanation = """
        Uniform Sampling은 전체 구간에서 균등하게 난수를 생성해 함수 값을 평균냅니다. 
        단순하지만 특정 구간에 데이터가 집중되어 있는 경우에는 정확도가 떨어질 수 있습니다.
        """
    elif best == "Stratified":
        explanation = """
        Stratified Sampling은 구간을 N등분하고 각 구간의 중심값을 샘플링합니다. 
        이를 통해 전체 영역을 고르게 대표하며, 특히 데이터가 균등 분포되지 않은 경우에도 안정적인 추정을 제공합니다.
        """
    elif best == "Importance":
        explanation = """
        Importance Sampling은 함수 값이 클 것으로 예상되는 구간에서 더 많은 샘플을 뽑는 전략입니다. 
        확률 밀도 함수(p(x))를 기반으로 가중치를 조절하며 오차를 줄입니다. 
        특히 함수가 특정 구간에서 급격히 변할 때 효과적입니다.
        """

    st.markdown(f"🧠 **{best} Sampling의 논리:**\n\n{explanation.strip()}")

else:
    st.info("📂 ZIP 파일을 먼저 업로드해 주세요. (CSV 내부에 'temperature'와 'ice cream sales' 컬럼 필요)")
