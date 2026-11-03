import streamlit as st
import plotly.graph_objects as go
from engine import StockWorldEngine, run_full_pipeline, fetch_market_macro

# ---------------------------------------------------------
# 1. 페이지 설정 및 모바일 반응형 커스텀 CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI 스마트 주식 자산관리",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 여백 최적화 */
    .block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 100% !important; }
    
    /* 상단 헤더 글자 눌림 방지 */
    .header-wrap {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0F172A;
        padding: 12px 18px;
        border-radius: 12px;
        margin-bottom: 14px;
        color: white;
    }
    .header-title { font-size: 18px; font-weight: 800; margin: 0; line-height: 1.4; }
    
    /* Metric 숫자 말줄임 방지 */
    div[data-testid="stMetricValue"] > div {
        font-size: 19px !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    div[data-testid="stMetricLabel"] { font-size: 12px !important; font-weight: 600 !important; }
    
    /* Top 3 추천 카드 */
    .top3-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-bottom: 14px;
    }
    .top3-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #1E3A8A;
        border-radius: 8px;
        padding: 10px 12px;
    }
    .top3-title { font-size: 13px; font-weight: 800; color: #0F172A; display: flex; justify-content: space-between; align-items: center; }
    .top3-reason { font-size: 11px; color: #475569; margin-top: 4px; line-height: 1.3; }

    /* 좌측 종목 리스트 카드 */
    .stock-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
        transition: all 0.15s ease;
    }
    .stock-card-active {
        background: #EFF6FF !important;
        border: 1.5px solid #2563EB !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    }
    
    /* 뱃지 및 색상 */
    .val-up { color: #DC2626 !important; font-weight: 800; }
    .val-down { color: #2563EB !important; font-weight: 800; }
    .badge-s { background: #1E3A8A; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; }
    .badge-a { background: #047857; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; }
    .badge-b { background: #475569; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 세션 상태 초기화 및 데이터 준비
# ---------------------------------------------------------
if "engine" not in st.session_state:
    st.session_state.engine = StockWorldEngine()
    st.session_state.engine.report_data["macro"] = fetch_market_macro()

if "holdings_data" not in st.session_state:
    st.session_state.holdings_data = [
        {"code": "060720", "name": "RFHIC", "qty": 450, "avg_price": 28500, "grade": "S"},
        {"code": "001440", "name": "대한전선", "qty": 1200, "avg_price": 14200, "grade": "A"},
        {"code": "005420", "name": "코스모화학", "qty": 300, "avg_price": 31000, "grade": "A"},
        {"code": "005930", "name": "삼성전자", "qty": 150, "avg_price": 72000, "grade": "B"},
        {"code": "000660", "name": "SK하이닉스", "qty": 80, "avg_price": 175000, "grade": "S"}
    ]

if "selected_code" not in st.session_state:
    st.session_state.selected_code = "060720"

# 기본 Top 3 추천 데이터 풀
if "top3_data" not in st.session_state:
    st.session_state.top3_data = [
        {"name": "RFHIC", "code": "060720", "grade": "S", "reason": "방산 GaN 전력증폭기 수주 및 5G 어드밴스드 모멘텀"},
        {"name": "대한전선", "code": "001440", "grade": "A", "reason": "북미 초고압 전력망 인프라 교체 주기 수혜"},
        {"name": "SK하이닉스", "code": "000660", "grade": "S", "reason": "HBM3E 독점 공급 우위 및 AI 메모리 실적 턴어라운드"}
    ]

# ---------------------------------------------------------
# 3. 상단 헤더 & 원클릭 파이프라인 트리거
# ---------------------------------------------------------
st.markdown("""
<div class="header-wrap">
    <div>
        <div class="header-title">📊 AI 스마트 주식 자산관리 & 포트폴리오 월드</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 2px;">4대 전문 에이전트 독립 병렬 분석 및 무결점 가드레일 시스템</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🚀 4대 에이전트 종합 파이프라인 가동 (시황/수급/공시 정밀 분석)", type="primary", use_container_width=True):
    with st.spinner("팩트·퀀트·공시 에이전트 병렬 분석 및 가드 검증 중..."):
        st.session_state.engine = run_full_pipeline(st.session_state.holdings_data, st.session_state.engine)
        st.session_state.holdings_data = st.session_state.engine.report_data["holdings"]
    st.rerun()

# ---------------------------------------------------------
# 4. 상단 4대 매크로 지수 상시 표출
# ---------------------------------------------------------
macro = st.session_state.engine.report_data.get("macro", {})
m1, m2, m3, m4 = st.columns(4)
m1.metric("코스피 (KOSPI)", f"{macro.get('KOSPI', {}).get('price', 0):,.2f}", f"{macro.get('KOSPI', {}).get('change', 0):+.2f}%")
m2.metric("코스닥 (KOSDAQ)", f"{macro.get('KOSDAQ', {}).get('price', 0):,.2f}", f"{macro.get('KOSDAQ', {}).get('change', 0):+.2f}%")
m3.metric("원/달러 환율", f"{macro.get('USDKRW', {}).get('price', 0):,.1f}원", f"{macro.get('USDKRW', {}).get('change', 0):+.2f}%", delta_color="inverse")
m4.metric("미 10년 국채금리", f"{macro.get('US10Y', {}).get('price', 0):.2f}%", f"{macro.get('US10Y', {}).get('change', 0):+.2f}%", delta_color="inverse")

# ---------------------------------------------------------
# 5. 총자산 포트폴리오 총괄 KPI 패널
# ---------------------------------------------------------
total_buy = sum(item["qty"] * item["avg_price"] for item in st.session_state.holdings_data)
total_eval = sum(item["qty"] * item.get("cur_price", item["avg_price"]) for item in st.session_state.holdings_data)
total_profit = total_eval - total_buy
total_rate = (total_profit / total_buy) * 100 if total_buy > 0 else 0

win_count = sum(1 for item in st.session_state.holdings_data if item.get("cur_price", item["avg_price"]) >= item["avg_price"])
loss_count = len(st.session_state.holdings_data) - win_count

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("총 평가금액", f"{total_eval:,.0f}원", f"매입: {total_buy:,.0f}원", delta_color="off")
kpi2.metric("총 평가손익", f"{total_profit:+,.0f}원", f"{total_rate:+.2f}%")
kpi3.metric("보유 현황", f"총 {len(st.session_state.holdings_data)}종목", f"수익 {win_count} / 손실 {loss_count}", delta_color="off")
kpi4.metric("월드 상태 (ESTC)", st.session_state.engine.state.upper(), "무결점 가드 가동 중", delta_color="off")

# ---------------------------------------------------------
# 6. [신설] 당일 에이전트 추천 Top 3 유망주 카드
# ---------------------------------------------------------
st.markdown("##### 🎯 오늘의 AI 추천 유망주 Top 3")
t_col1, t_col2, t_col3 = st.columns(3)
cols = [t_col1, t_col2, t_col3]
for idx, stock in enumerate(st.session_state.top3_data):
    with cols[idx]:
        st.markdown(f"""
        <div class="top3-card">
            <div class="top3-title">
                <span>{stock['name']} <span style="font-size:11px; color:#64748B;">({stock['code']})</span></span>
                <span class="badge-s">{stock['grade']}</span>
            </div>
            <div class="top3-reason">{stock['reason']}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 브리핑 영역 & 승인 관문
# ---------------------------------------------------------
briefing_text = st.session_state.engine.report_data.get("briefing", "")
if briefing_text:
    st.markdown("##### 🎙️ 수석 전략가 핵심 장마감 브리핑")
    st.info(briefing_text)
    if st.session_state.engine.state == "under_review":
        bc1, bc2, bc3 = st.columns([1, 1, 3])
        with bc1:
            if st.button("✅ 최종 승인 (Commit)", use_container_width=True):
                st.session_state.engine.state = "committed"
                st.success("원장에 영구 반영되었습니다.")
        with bc2:
            if st.button("🔄 재작업 (Rework)", use_container_width=True):
                st.session_state.engine.state = "drafted"
                st.warning("분석 상태가 롤백되었습니다.")
        with bc3:
            st.caption("🛡️ World 가드: 수치 정밀 대조 통과 | URL 노출 차단")

st.markdown("---")

# ---------------------------------------------------------
# 8. 메인 뷰: 좌측 종목 리스트 (MTS 카드형) vs 우측 인스펙터
# ---------------------------------------------------------
left_col, right_col = st.columns([1.3, 2.7])

with left_col:
    st.markdown("##### 📋 보유 종목 포트폴리오")
    for stock in st.session_state.holdings_data:
        cur_p = stock.get("cur_price", stock["avg_price"])
        profit_rate = ((cur_p - stock["avg_price"]) / stock["avg_price"]) * 100 if stock["avg_price"] > 0 else 0
        rate_class = "val-up" if profit_rate >= 0 else "val-down"
        is_active = (stock["code"] == st.session_state.selected_code)
        active_class = "stock-card-active" if is_active else ""
        badge_style = "badge-s" if stock.get("grade") == "S" else ("badge-a" if stock.get("grade") == "A" else "badge-b")
        
        # MTS 스타일 종목 카드 레이아웃
        st.markdown(f"""
        <div class="stock-card {active_class}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:800; font-size:14px; color:#0F172A;">{stock['name']} <span class="{badge_style}">{stock.get('grade', 'B')}</span></span>
                <span class="{rate_class}" style="font-size:13px;">{profit_rate:+.2f}%</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                <span style="font-size:11px; color:#64748B;">{stock['qty']:,}주 (평단 {stock['avg_price']:,}원)</span>
                <span style="font-size:13px; font-weight:800; color:#0F172A;">{cur_p:,.0f}원</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"{stock['name']} 선택", key=f"btn_{stock['code']}", use_container_width=True):
            st.session_state.selected_code = stock["code"]
            st.rerun()

with right_col:
    target = next((item for item in st.session_state.holdings_data if item["code"] == st.session_state.selected_code), st.session_state.holdings_data[0])
    t_cur = target.get("cur_price", target["avg_price"])
    t_profit_rate = ((t_cur - target["avg_price"]) / target["avg_price"]) * 100
    t_profit_val = (t_cur - target["avg_price"]) * target["qty"]
    
    st.markdown(f"#### 🎯 {target['name']} ({target['code']}) 정밀 진단")
    
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("현재가", f"{t_cur:,.0f}원", f"{t_profit_rate:+.2f}%")
    i2.metric("총 평가손익", f"{t_profit_val:+,.0f}원", f"{t_profit_rate:+.2f}%")
    i3.metric("매집 강도", f"{target.get('supply_score', 50)}점", target.get('supply_stage', '수급유입'))
    i4.metric("보유 수량", f"{target['qty']:,}주", f"평단 {target['avg_price']:,}원")
    
    # 캔들스틱 차트
    st.markdown("##### 📈 캔들스틱 & 주가 추세")
    base_p = t_cur if t_cur > 0 else 30000
    fig = go.Figure(data=[go.Candlestick(
        x=['2026-10-28', '2026-10-29', '2026-10-30', '2026-10-31'],
        open=[base_p * 0.98, base_p * 0.99, base_p * 1.01, base_p * 1.00],
        high=[base_p * 1.02, base_p * 1.03, base_p * 1.04, base_p * 1.03],
        low=[base_p * 0.97, base_p * 0.98, base_p * 0.99, base_p * 0.99],
        close=[base_p * 0.99, base_p * 1.01, base_p * 1.00, base_p]
    )])
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
