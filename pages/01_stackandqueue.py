import streamlit as st
import plotly.graph_objects as go

# 초기 설정
st.set_page_config(page_title="자료구조: 스택 & 큐", layout="centered")
st.title("📚 자료구조 시각화: 스택(Stack)과 큐(Queue)")
st.markdown("아래에서 각각의 자료구조 개념을 확인하고, 동작 원리를 시각적으로 체험해보세요!")

# 공통 스타일링 함수
def draw_structure(title, items, mode="stack"):
    fig = go.Figure()

    if mode == "stack":
        for i, val in enumerate(reversed(items)):
            fig.add_trace(go.Bar(
                x=["스택"],
                y=[1],
                base=i,
                name=val,
                orientation='v',
                text=[val],
                textposition="inside",
                marker_color='skyblue'
            ))
        fig.update_layout(title=title, showlegend=False, height=400)

    elif mode == "queue":
        fig.add_trace(go.Bar(
            y=["큐"],
            x=[1] * len(items),
            orientation='h',
            text=items,
            textposition="inside",
            marker_color='lightgreen'
        ))
        fig.update_layout(title=title, showlegend=False, height=200)

    st.plotly_chart(fig, use_container_width=True)

# 스택 섹션
st.header("📦 스택 (Stack)")
st.markdown("""
**스택**은 *Last-In, First-Out (LIFO)* 구조입니다.  
즉, 나중에 들어온 데이터가 먼저 나갑니다.

예시: 책 더미, 웹 브라우저 뒤로 가기 기록 등
""")

# 스택 시뮬레이션
if "stack_data" not in st.session_state:
    st.session_state.stack_data = []

stack_col1, stack_col2 = st.columns(2)
with stack_col1:
    stack_push = st.text_input("스택에 값 추가 (Push)", key="stack_push")
    if st.button("Push"):
        if stack_push:
            st.session_state.stack_data.append(stack_push)

with stack_col2:
    if st.button("Pop"):
        if st.session_state.stack_data:
            st.success(f"Pop: {st.session_state.stack_data.pop()}")
        else:
            st.warning("스택이 비어 있습니다.")

draw_structure("🗂️ 스택 구조", st.session_state.stack_data, mode="stack")

st.markdown("---")

# 큐 섹션
st.header("🚶 큐 (Queue)")
st.markdown("""
**큐**는 *First-In, First-Out (FIFO)* 구조입니다.  
즉, 먼저 들어온 데이터가 먼저 나갑니다.

예시: 은행 대기열, 인쇄 작업 순서 등
""")

# 큐 시뮬레이션
if "queue_data" not in st.session_state:
    st.session_state.queue_data = []

queue_col1, queue_col2 = st.columns(2)
with queue_col1:
    queue_enqueue = st.text_input("큐에 값 추가 (Enqueue)", key="queue_push")
    if st.button("Enqueue"):
        if queue_enqueue:
            st.session_state.queue_data.append(queue_enqueue)

with queue_col2:
    if st.button("Dequeue"):
        if st.session_state.queue_data:
            st.success(f"Dequeue: {st.session_state.queue_data.pop(0)}")
        else:
            st.warning("큐가 비어 있습니다.")

draw_structure("🚃 큐 구조", st.session_state.queue_data, mode="queue")

st.markdown("---")
st.markdown("🔗 더 많은 AI 학습 도구는 [GPTOnline.ai](https://gptonline.ai/ko/)에서 확인해보세요!")
