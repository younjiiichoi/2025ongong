import streamlit as st
import pandas as pd
import plotly.express as px

# 파일 불러오기
@st.cache_data
def load_data():
# 파일 경로를 상대 경로로 지정
    df_gender = pd.read_excel('people_gender.xlsx')
    df_sum = pd.read_excel('people_sum.xlsx')
    return df_gender, df_sum

df_gender, df_sum = load_data()

# 지역 선택
regions = df_gender['행정구역'].unique()
selected_region = st.selectbox("지역을 선택하세요", regions)

# 연령대 슬라이더 설정
min_age = int(df_gender['연령(5세단위)'].min().replace('세', '').replace(' ', '').split('~')[0])
max_age = int(df_gender['연령(5세단위)'].max().replace('세', '').replace(' ', '').split('~')[0]) + 5
age_range = st.slider("연령대 범위 선택", min_value=min_age, max_value=max_age, value=(min_age, max_age), step=5)

# 연령대 필터링 함수
def parse_age(age_str):
    try:
        age_start = int(age_str.replace('세', '').split('~')[0])
        return age_start
    except:
        return 0  # '100세 이상' 처리용

df_filtered = df_gender[df_gender['행정구역'] == selected_region].copy()
df_filtered['나이시작'] = df_filtered['연령(5세단위)'].apply(parse_age)
df_filtered = df_filtered[(df_filtered['나이시작'] >= age_range[0]) & (df_filtered['나이시작'] < age_range[1])]

# 성별에 따라 값 조정 (여성은 음수로 설정하여 피라미드 구조)
df_filtered['남자'] = df_filtered['남자']
df_filtered['여자'] = -df_filtered['여자']

# Plotly 시각화
fig = px.bar(
    df_filtered,
    x='남자',
    y='연령(5세단위)',
    orientation='h',
    color_discrete_sequence=['blue'],
    labels={'남자': '인구수', '연령(5세단위)': '연령'},
    title=f"{selected_region} 지역의 성별 인구 피라미드"
)

fig.add_bar(
    x=df_filtered['여자'],
    y=df_filtered['연령(5세단위)'],
    orientation='h',
    name='여자',
    marker_color='pink'
)

fig.update_layout(barmode='relative', yaxis={'categoryorder': 'total ascending'})

st.plotly_chart(fig)
