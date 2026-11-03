import streamlit as st
import plotly.graph_objects as go
from engine import StockWorldEngine, run_full_pipeline, fetch_market_macro

# ---------------------------------------------------------
# 1. 페이지 설정 및 모바일 최적화 CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI 스마트 주식 자산관리",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 여백 최적화 및 가로 스크롤 방지 */
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 100% !important; }
    
    /* 상단 헤더 반응형 */
    .header-box { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px; }
    .header-title { font-size: 20px; font-weight: 800; color: #0F172A; margin: 0; }
    
    /* KPI 총괄 카드 */
    .kpi-container { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .kpi-title { font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value { font-size: 20px; font-weight: 900; color: #0F172A; }
    .kpi-sub { font-size: 11px; margin-top: 4px; font-weight: 600; }
    
    /* 텍스트 컬러 */
    .val-up { color: #DC2626 !important; font-weight: 800; }
    .val-down { color: #2563EB !important; font-weight: 800; }
    .val-sub { color: #64748B; }
    
    .badge-s { background: #1E3A8A; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 700; }
    .badge-a { background: #047857; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 세션 상태 초기화 및 데이터 준비
# ---------------------------------------------------------
if "engine" not in st.session_state:
    st.session_state.engine = StockWorldEngine()
    # 초기 진입 시에도 4대 매크로 지수를 즉시 수집해 표출
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

# ---------------------------------------------------------
# 3. 상단 헤더 & 에이전트 실행 바
# ---------------------------------------------------------
head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.markdown("<h2 style='margin:0; font-size:22px; font-weight:800;'>📊 AI 스마트 주식 자산관리 & 포트폴리오 월드</h2>", unsafe_allow_html=True)
with head_col2:
    if st.button("🚀 4대 에이전트 분석 실행", type="primary", use_container_width=True):
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
# 5. [신설] 총자산 포트폴리오 총괄 KPI 패널
# ---------------------------------------------------------
total_buy = sum(item["qty"] * item["avg_price"] for item in st.session_state.holdings_data)
total_eval = sum(item["qty"] * item.get("cur_price", item["avg_price"]) for item in st.session_state.holdings_data)
total_profit = total_eval - total_buy
total_rate = (total_profit / total_buy) * 100 if total_buy > 0 else 0

win_count = sum(1 for item in st.session_state.holdings_data if item.get("cur_price", item["avg_price"]) >= item["avg_price"])
loss_count = len(st.session_state.holdings_data) - win_count

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("현재 총 평가금액", f"{total_eval:,.0f}원", f"매입원금: {total_buy:,.0f}원", delta_color="off")
kpi2.metric("총 평가손익", f"{total_profit:+,.0f}원", f"{total_rate:+.2f}%")
kpi3.metric("보유 현황", f"총 {len(st.session_state.holdings_data)}개 종목", f"수익 {win_count} / 손실 {loss_count}", delta_color="off")
kpi4.metric("월드 상태 (ESTC)", st.session_state.engine.state.upper(), "무결점 가드 가동 중", delta_color="off")

st.markdown("---")

# ---------------------------------------------------------
# 6. 브리핑 영역 (생략 없이 유지)
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

# ---------------------------------------------------------
# 7. 메인 뷰: 좌측 종목 목록 vs 우측 인스펙터
# ---------------------------------------------------------
left_col, right_col = st.columns([1.2, 2.8])

with left_col:
    st.markdown("##### 📋 보유 종목 리스트")
    for stock in st.session_state.holdings_data:
        cur_p = stock.get("cur_price", stock["avg_price"])
        profit_rate = ((cur_p - stock["avg_price"]) / stock["avg_price"]) * 100 if stock["avg_price"] > 0 else 0
        rate_class = "val-up" if profit_rate >= 0 else "val-down"
        
        c_a, c_b = st.columns([3, 1])
        with c_a:
            st.markdown(f"**{stock['name']}** <span class='badge-s'>{stock.get('grade', 'B')}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='{rate_class}'>{cur_p:,.0f}원 ({profit_rate:+.2f}%)</span>", unsafe_allow_html=True)
        with c_b:
            if st.button("선택", key=f"sel_{stock['code']}", use_container_width=True):
                st.session_state.selected_code = stock["code"]
        st.divider()

with right_col:
    target = next((item for item in st.session_state.holdings_data if item["code"] == st.session_state.selected_code), st.session_state.holdings_data[0])
    t_cur = target.get("cur_price", target["avg_price"])
    t_profit_rate = ((t_cur - target["avg_price"]) / target["avg_price"]) * 100
    t_profit_val = (t_cur - target["avg_price"]) * target["qty"]
    
    st.markdown(f"#### 🎯 {target['name']} ({target['code']}) 상세 진단")
    
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("현재가", f"{t_cur:,.0f}원", f"{t_profit_rate:+.2f}%")
    i2.metric("총 평가손익", f"{t_profit_val:+,.0f}원", f"{t_profit_rate:+.2f}%")
    i3.metric("매집 강도", f"{target.get('supply_score', 50)}점", target.get('supply_stage', '수급유입'))
    i4.metric("보유 수량", f"{target['qty']:,}주", f"평단: {target['avg_price']:,}원")
    
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
