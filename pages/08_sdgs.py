import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="직업 위험도 분석", layout="wide")

st.title("🤖 직업 자동화 위험도 분석 앱")

# -----------------------------
# 1. 데이터 불러오기 및 전처리
# -----------------------------
@st.cache_data
def load_data():
    # 예시 위험도 데이터
    job_risk_data = {
        "job": [
            "속기사", "행정사", "취업알선원", "한식조리사", "중식조리사",
            "AI 엔지니어", "콜센터 상담원", "택배기사", "변호사", "의사",
            "간호사", "초등학교 교사", "마트 계산원", "영업사원", "청소원",
            "건축가", "치과의사", "약사", "연구원", "그래픽 디자이너"
        ],
        "risk_score": [
            0.75, 0.55, 0.7, 0.3, 0.35,
            0.1, 0.95, 0.9, 0.2, 0.1,
            0.3, 0.25, 0.92, 0.6, 0.88,
            0.45, 0.15, 0.2, 0.3, 0.55
        ]
    }
    job_risk_df = pd.DataFrame(job_risk_data)

    # 직업 분류 파일 (사전 업로드되어 있어야 함)
    job_detail_df = pd.read_csv("직업세세분류.CSV", encoding="euc-kr")

    # 병합
    merged = pd.merge(job_detail_df, job_risk_df, left_on="KNOW직업명", right_on="job")

    return merged

merged_df = load_data()

# -----------------------------
# 2. 회귀분석: 직업소분류 코드 → 평균 위험도
# -----------------------------
grouped_df = merged_df.groupby("KNOW직업소분류")["risk_score"].mean().reset_index()
grouped_df.rename(columns={"risk_score": "avg_risk_score"}, inplace=True)

# 회귀분석
X = grouped_df[["KNOW직업소분류"]]
y = grouped_df["avg_risk_score"]
reg = LinearRegression().fit(X, y)

grouped_df["predicted_risk"] = reg.predict(X)

# -----------------------------
# 3. 위험도 탐색 및 정렬
# -----------------------------
st.sidebar.header("🎚️ 위험도 필터")
min_risk, max_risk = st.sidebar.slider("위험도 범위 선택", 0.0, 1.0, (0.0, 1.0), 0.05)

filtered = merged_df[(merged_df["risk_score"] >= min_risk) & (merged_df["risk_score"] <= max_risk)]
sorted_data = filtered.sort_values(by="risk_score", ascending=False)

st.subheader("📋 직업별 위험도 데이터")
st.dataframe(sorted_data[["KNOW직업명", "KNOW직업소분류", "risk_score"]].reset_index(drop=True), use_container_width=True)

# -----------------------------
# 4. 보조금 신청 대기열 (Queue)
# -----------------------------
st.subheader("💰 보조금 신청 대기열")

if "queue" not in st.session_state:
    st.session_state.queue = deque()

col1, col2 = st.columns([2, 1])
with col1:
    selected_job = st.selectbox("신청할 직업 선택", merged_df["KNOW직업명"].unique())
    if st.button("신청하기"):
        st.session_state.queue.append(selected_job)
        st.success(f"{selected_job} 신청 완료!")

with col2:
    if st.button("1명 처리"):
        if st.session_state.queue:
            done = st.session_state.queue.popleft()
            st.info(f"✅ {done} 처리 완료")
        else:
            st.warning("대기열이 비어있어요.")

if st.session_state.queue:
    st.markdown("**📦 현재 대기열**")
    for i, job in enumerate(st.session_state.queue, 1):
        st.write(f"{i}. {job}")
else:
    st.write("🚫 대기 중인 신청 없음")

# -----------------------------
# 5. 전직 가능성 그래프 시각화
# -----------------------------
st.subheader("🔄 전직 가능성 그래프")

G = nx.DiGraph()
G.add_edges_from([
    ("콜센터 상담원", "고객경험 설계자"),
    ("택배기사", "물류 자동화 관리자"),
    ("마트 계산원", "셀프 POS 관리자"),
    ("속기사", "AI 음성처리 전문가"),
    ("요리사", "식품 개발 연구원"),
])

plt.figure(figsize=(7, 5))
pos = nx.spring_layout(G, seed=42)
nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=2000)
nx.draw_networkx_edges(G, pos, edge_color='gray')
nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
plt.axis("off")
st.pyplot(plt)

# -----------------------------
# 6. 회귀분석 결과 시각화
# -----------------------------
st.subheader("📈 직업군별 평균 위험도 vs 회귀 예측값")
st.dataframe(grouped_df.rename(columns={
    "KNOW직업소분류": "직업군코드",
    "avg_risk_score": "평균 위험도",
    "predicted_risk": "예측 위험도"
}), use_container_width=True)
