import streamlit as st

st.set_page_config(page_title="MBTI 분석기", layout="centered")

st.title("🧠 MBTI 성격 유형 분석기")
st.markdown("아래 질문에 답하면, 당신의 MBTI 성격 유형을 실시간으로 분석합니다!")

# 질문 정의
questions = {
    "EI": {
        "question": "사교 활동이 많을 때 나는...",
        "options": {
            "E": "에너지가 충전된다 (외향형)",
            "I": "에너지가 소모된다 (내향형)"
        }
    },
    "SN": {
        "question": "정보를 이해할 때 나는...",
        "options": {
            "S": "현실적이고 구체적인 정보를 선호한다 (감각형)",
            "N": "아이디어와 가능성 중심으로 생각한다 (직관형)"
        }
    },
    "TF": {
        "question": "결정할 때 나는...",
        "options": {
            "T": "논리와 객관적인 사실을 중시한다 (사고형)",
            "F": "감정과 사람 간의 조화를 중시한다 (감정형)"
        }
    },
    "JP": {
        "question": "일정과 계획에 대해서 나는...",
        "options": {
            "J": "계획적으로 움직이고 마감일을 지킨다 (판단형)",
            "P": "즉흥적으로 대응하고 유연하게 처리한다 (인식형)"
        }
    }
}

# 사용자의 선택 저장
answers = {}

for key, q in questions.items():
    st.subheader(q["question"])
    answer = st.radio(
        label="선택하세요:",
        options=list(q["options"].keys()),
        format_func=lambda x: q["options"][x],
        key=key
    )
    answers[key] = answer

# MBTI 결과 출력
if len(answers) == 4:
    mbti_result = answers["EI"] + answers["SN"] + answers["TF"] + answers["JP"]
    st.success(f"🎉 당신의 MBTI는 **{mbti_result}** 입니다!")
    
    # 유형별 간단 설명 추가 (옵션)
    descriptions = {
        "INTJ": "전략가: 독립적이고 분석적인 성격입니다.",
        "INFP": "중재자: 이상주의적이고 따뜻한 감성을 가졌습니다.",
        "ESTJ": "경영자: 체계적이고 리더십이 뛰어납니다.",
        # 필요한 만큼 추가 가능
    }

    if mbti_result in descriptions:
        st.info(f"📌 설명: {descriptions[mbti_result]}")
    else:
        st.info("📌 이 유형에 대한 설명은 준비 중입니다.")

---

st.markdown("---")
st.markdown("🔗 더 많은 AI 도구는 [GPTOnline.ai](https://gptonline.ai/ko/)에서 만나보세요!")
