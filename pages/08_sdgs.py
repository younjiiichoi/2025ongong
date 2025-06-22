import streamlit as st
import pandas as pd
import heapq
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import networkx as nx

st.set_page_config(page_title="직업 위험도 예측", layout="wide")
st.title("🤖 직업 자동화 위험도 예측 앱 (전체 직업)")

# ---------------------------
# 1. 데이터 불러오기
# ---------------------------
@st.cache_data
def load_data():
    job_detail_df = pd.read_csv("직업세세분류.CSV", encoding="euc-kr")

    # 예시 위험도 학습용
    example_risks = {
        "속기사": 0.75, "행정사": 0.55, "취업알선원": 0.7, "한식조리사": 0.3, "중식조리사": 0.35,
        "AI 엔지니어": 0.1, "콜센터 상담원": 0.95, "택배기사": 0.9, "변호사": 0.2, "의사": 0.1,
        "간호사": 0.3, "초등학교 교사": 0.25, "마트 계산원": 0.92, "영업사원": 0.6, "청소원": 0.88,
        "건축가": 0.45, "치과의사": 0.15, "약사": 0.2, "연구원": 0.3, "그래픽 디자이너": 0.55
    }

    unique_jobs = job_detail_df["KNOW직업명"].drop_duplicates().reset_index(drop=True).to_frame()
    unique_jobs["job_index"] = unique_jobs.index

    # 학습 데이터 생성
    train_df = unique_jobs[unique_jobs["KNOW직업명"].isin(example_risks.keys())].copy()
    train_df["risk_score"] = train_df["KNOW직업명"].map(example_risks)

    # 회귀 모델 학습
    reg = LinearRegression().fit(train_df[["job_index"]], train_df["risk_score"])

    # 전체 예측
    unique_jobs["predicted_risk"] = reg.predict(unique_jobs[["job_index"]])

    return unique_jobs

jobs_df = load_data()

# ---------------------------
# 2. 슬라이더 필터 + 테이블
# ---------------------------
st.sidebar.header("🎚️ 위험도 범위")
min_r, max_r = st.sidebar.slider("예측 위험도", 0.0, 1.0, (0.0, 1.0), 0.05)

filtered = jobs_df[(jobs_df["predicted_risk"] >= min_r) & (jobs_df["predicted_risk"] <= max_r)]
filtered = filtered.sort_values("predicted_risk", ascending=False)

st.subheader("📋 전체 직업 예측 위험도")
st.dataframe(filtered.rename(columns={"KNOW직업명": "직업명", "predicted_risk": "예측 위험도"}), use_container_width=True)

# ---------------------------
# 3. 보조금 우선순위 큐
# ---------------------------
st.subheader("💰 보조금 신청 대기열 (예측 위험도 순)")

if "priority_queue" not in st.session_state:
    st.session_state.priority_queue = []

col1, col2 = st.columns([2, 1])
with col1:
    selected_job = st.selectbox("신청할 직업", jobs_df["KNOW직업명"].unique())
    if st.button("신청하기"):
        row = jobs_df[jobs_df["KNOW직업명"] == selected_job]
        risk = float(row["predicted_risk"].values[0])
        heapq.heappush(st.session_state.priority_queue, (-risk, selected_job))
        st.success(f"{selected_job} 신청 완료!")

with col2:
    if st.button("1명 처리"):
        if st.session_state.priority_queue:
            _, job_name = heapq.heappop(st.session_state.priority_queue)
            st.info(f"✅ {job_name} 처리 완료")
        else:
            st.warning("신청 없음")

if st.session_state.priority_queue:
    st.markdown("**📦 대기열**")
    for i, (risk, job) in enumerate(sorted(st.session_state.priority_queue, reverse=True), 1):
        st.write(f"{i}. {job} (예측 위험도: {-risk:.2f})")
else:
    st.write("🚫 대기열 없음")

# ---------------------------
# 4. 전직 가능성 그래프 (샘플)
# ---------------------------
st.subheader("🔄 전직 가능성 그래프")

G = nx.DiGraph()
G.add_edges_from([
    ("마트 계산원", "셀프 POS 관리자"),
    ("콜센터 상담원", "챗봇 튜너"),
    ("택배기사", "로봇 물류 기술자"),
    ("속기사", "AI 텍스트 엔지니어")
])

plt.figure(figsize=(7, 5))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=2000, font_weight='bold')
plt.axis("off")
st.pyplot(plt)
