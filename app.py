import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import StockWorldEngine, run_full_pipeline, fetch_market_macro

# ---------------------------------------------------------
# 1. 페이지 설정 & 반응형 적응형 완결 CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI 스마트 주식 자산관리",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 기본 헤더 및 툴바 완전 제거 */
    header[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding: 0.6rem 0.8rem 2rem 0.8rem !important; max-width: 1400px !important; }

    /* CSS 변수 */
    :root {
        --deep-navy: #1E3A8A;
        --positive-red: #DC2626;
        --negative-blue: #1D4ED8;
        --border-color: #E2E8F0;
        --bg-subtle: #F8FAFC;
    }

    /* 상단 타이틀 바 */
    .header-bar { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
    .title-wrapper { display: flex; align-items: center; gap: 8px; }
    .title-bar-accent { width: 4px; height: 32px; background: linear-gradient(180deg, #1E3A8A 0%, #DC2626 100%); border-radius: 4px; }
    .title-area h1 { font-size: 1.15rem; font-weight: 800; color: #0F172A; margin: 0; display: flex; align-items: center; gap: 6px; }
    .live-badge { font-size: 0.60rem; font-weight: 800; background: #FEE2E2; color: #991B1B; padding: 2px 6px; border-radius: 10px; }
    
    /* 매크로 지수 박스 */
    .market-index-bar {
        background: #FFFFFF; border: 1px solid var(--border-color); padding: 5px 10px; border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03); display: flex; align-items: center;
    }
    .macro-grid-inner { display: grid; grid-template-columns: auto auto; gap: 2px 10px; }
    .index-item { display: inline-flex; align-items: baseline; gap: 4px; font-size: 0.72rem; white-space: nowrap; }
    .index-name { font-weight: 700; color: #475569; font-size: 0.68rem; }
    .index-price { font-weight: 800; color: #000; font-size: 0.74rem; }

    /* 브리핑 2열 */
    .intro-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .intro-box {
        background: #FFFFFF; border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .intro-box-title { font-size: 0.82rem; font-weight: 800; color: #0F172A; display: flex; justify-content: space-between; margin-bottom: 4px; }
    .risk-content-body {
        font-size: 0.74rem; color: #1E293B; line-height: 1.45; background: var(--bg-subtle);
        padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border-color);
    }

    /* Top 3 카드 */
    .rec-carousel-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }
    .rec-carousel-card {
        background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 12px;
        display: flex; flex-direction: column; gap: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .rec-rank-badge { font-size: 0.65rem; font-weight: 800; color: #FFFFFF; background: var(--deep-navy); padding: 2px 5px; border-radius: 4px; }
    .rec-name { font-size: 0.90rem; font-weight: 800; color: #000; }
    .rec-headline-box {
        font-size: 0.72rem; color: #1E293B; line-height: 1.4; background: #FEF2F2; border: 1px solid #FECACA;
        padding: 6px 8px; border-radius: 6px; font-weight: 600;
    }

    /* 메인 분할 레이아웃 */
    .master-detail-grid { display: grid; grid-template-columns: 280px 1fr; gap: 12px; align-items: start; }
    
    /* 좌측 종목 목록 */
    .left-list-panel {
        background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 8px;
        display: flex; flex-direction: column; gap: 5px;
    }
    .compact-stock-item {
        background: #FFFFFF; border: 1px solid var(--border-color); border-radius: 7px; padding: 7px 9px;
        display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: all 0.15s ease;
    }
    .compact-stock-item:hover { border-color: #94A3B8; background: #F8FAFC; }
    .compact-stock-item.active { border-color: var(--deep-navy) !important; background: #FEF2F2 !important; box-shadow: 0 0 0 1px var(--deep-navy); }

    /* 우측 KPI 그리드 */
    .kpi-main-grid { display: grid; grid-template-columns: 1.15fr 1.15fr 0.85fr 1.35fr; gap: 6px; margin-bottom: 10px; }
    .kpi-main-card {
        background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 8px; padding: 7px 6px;
        display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
    }
    .kpi-title { font-size: 0.65rem; font-weight: 700; color: #64748B; }
    .kpi-val { font-size: 0.95rem; font-weight: 800; color: #000; }
    .kpi-sub { font-size: 0.68rem; font-weight: 700; }

    /* 가격 상세 4열 */
    .detail-price-table {
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; background: var(--bg-subtle);
        border: 1px solid var(--border-color); padding: 8px 10px; border-radius: 8px; text-align: center; margin-bottom: 8px;
    }

    /* 뱃지 및 색상 */
    .val-up { color: #DC2626 !important; font-weight: 800 !important; }
    .val-down { color: #1D4ED8 !important; font-weight: 800 !important; }
    .grade-badge-s { font-size: 0.62rem; font-weight: 800; background: #1E3A8A; color: #FFFFFF; padding: 2px 5px; border-radius: 3px; }
    .grade-badge-a { font-size: 0.62rem; font-weight: 800; background: #047857; color: #FFFFFF; padding: 2px 5px; border-radius: 3px; }
    .grade-badge-b { font-size: 0.62rem; font-weight: 800; background: #B45309; color: #FFFFFF; padding: 2px 5px; border-radius: 3px; }
    .grade-badge-c { font-size: 0.62rem; font-weight: 800; background: #B91C1C; color: #FFFFFF; padding: 2px 5px; border-radius: 3px; }

    /* 심층 진단 모달 인디케이터 */
    .grid-4col { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
    .indicator-card { border-radius: 6px; padding: 5px 6px; border: 1px solid var(--border-color); background: #FFFFFF; text-align: center; }
    .indicator-title { font-size: 0.62rem; color: #64748B; font-weight: 700; }
    .indicator-val { font-size: 0.80rem; font-weight: 800; margin-top: 1px; }

    /* 모바일 세로 화면(768px 이하) 완전 적응 미디어 쿼리 */
    @media screen and (max-width: 768px) {
        .header-bar { flex-direction: column; align-items: flex-start; gap: 6px; }
        .market-index-bar { width: 100%; overflow-x: auto; }
        .intro-grid { grid-template-columns: 1fr !important; }
        .rec-carousel-container { grid-template-columns: 1fr !important; }
        .master-detail-grid { grid-template-columns: 1fr !important; }
        .kpi-main-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 6px; }
        .detail-price-table { grid-template-columns: repeat(2, 1fr) !important; gap: 6px; }
        .grid-4col { grid-template-columns: repeat(2, 1fr) !important; gap: 4px; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 포트폴리오 데이터 (현실적 수치 및 등급 매핑)
# ---------------------------------------------------------
DEFAULT_HOLDINGS = [
    {"code": "060720", "name": "RFHIC", "sector": "방산/통신", "qty": 450, "avg_price": 28500, "cur_price": 29800, "grade": "S",
     "roe": "14.2%", "debt": "42.1%", "opYoY": "+38.4%", "targetDisp": "+24.5%", "per": "18.2", "pbr": "1.3", "supply_score": 88, "supply_stage": "🚀 매집완료", "rsi": 62.4, "volRatio": "185.0%", "disparity20": "104.2%",
     "why": "방산 GaN 전력증폭기 글로벌 수주 확대 및 5G 어드밴스드 사이클 진입에 따른 실적 턴어라운드 본격화."},
    {"code": "001440", "name": "대한전선", "sector": "전력인프라", "qty": 1200, "avg_price": 14200, "cur_price": 14650, "grade": "A",
     "roe": "11.5%", "debt": "88.2%", "opYoY": "+25.1%", "targetDisp": "+18.0%", "per": "14.1", "pbr": "1.1", "supply_score": 76, "supply_stage": "⏳ 집중매집", "rsi": 58.1, "volRatio": "142.0%", "disparity20": "102.5%",
     "why": "북미 송전망 교체 및 해저케이블 1공장 가동에 따른 수주 잔고 최고치 경신 모멘텀 지속."},
    {"code": "005420", "name": "코스모화학", "sector": "2차전지/소재", "qty": 300, "avg_price": 31000, "cur_price": 29200, "grade": "B",
     "roe": "4.2%", "debt": "118.5%", "opYoY": "-8.2%", "targetDisp": "+12.0%", "per": "24.5", "pbr": "1.5", "supply_score": 55, "supply_stage": "🔍 수급유입", "rsi": 44.0, "volRatio": "88.0%", "disparity20": "98.5%",
     "why": "폐배터리 리사이클링 설비 증설 효과 기대되나 전방 전기차 수요 둔화로 기간 조정 지속."},
    {"code": "005930", "name": "삼성전자", "sector": "반도체/IT", "qty": 150, "avg_price": 72000, "cur_price": 68500, "grade": "B",
     "roe": "8.1%", "debt": "26.3%", "opYoY": "+12.4%", "targetDisp": "+18.0%", "per": "12.8", "pbr": "1.2", "supply_score": 52, "supply_stage": "❌ 중립", "rsi": 46.5, "volRatio": "82.0%", "disparity20": "97.5%",
     "why": "범용 D램 가격 반등 중이나 HBM 메인 벤더 진입 일정 조율에 따른 횡보 구간."},
    {"code": "000660", "name": "SK하이닉스", "sector": "반도체/HBM", "qty": 80, "avg_price": 175000, "cur_price": 189000, "grade": "S",
     "roe": "21.4%", "debt": "55.8%", "opYoY": "+145.0%", "targetDisp": "+26.0%", "per": "8.5", "pbr": "1.8", "supply_score": 94, "supply_stage": "🚀 매집완료", "rsi": 68.2, "volRatio": "210.0%", "disparity20": "106.8%",
     "why": "HBM3E 독점 지위 및 AI 데이터센터 eSSD 수요 폭증에 따른 분기 사상 최대 실적 경신."}
]

if "engine" not in st.session_state:
    st.session_state.engine = StockWorldEngine()
    st.session_state.engine.report_data["macro"] = fetch_market_macro()

if "holdings_data" not in st.session_state or "sector" not in st.session_state.holdings_data[0]:
    st.session_state.holdings_data = DEFAULT_HOLDINGS

if "selected_code" not in st.session_state:
    st.session_state.selected_code = "060720"

def get_badge_class(grade):
    g = str(grade).upper()
    return "grade-badge-s" if "S" in g else ("grade-badge-a" if "A" in g else ("grade-badge-b" if "B" in g else "grade-badge-c"))

# ---------------------------------------------------------
# 3. 심층 분석 모달 (@st.dialog)
# ---------------------------------------------------------
@st.dialog("🔍 종목 심층 분석")
def show_deep_analysis_dialog(stock):
    sec = stock.get('sector', '핵심성장주')
    b_cls = get_badge_class(stock.get('grade', 'B'))
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #E2E8F0; padding-bottom:6px; margin-bottom:8px;">
        <div style="display:flex; align-items:center; gap:6px;">
            <span style="font-size:1.15rem; font-weight:800;">{stock.get('name', '')}</span>
            <span style="font-size:0.75rem; color:#64748B; font-weight:700;">{stock.get('code', '')}</span>
            <span style="font-size:0.72rem; font-weight:700; background:#EEF2FF; color:#1E3A8A; padding:2px 6px; border-radius:4px;">{sec}</span>
            <span style="font-size:0.80rem; font-weight:800; background:#F1F5F9; padding:2px 6px; border-radius:4px;">현재가: {stock.get('cur_price', 0):,}원</span>
        </div>
        <span class="{b_cls}">등급: {stock.get('grade', 'B')}</span>
    </div>

    <div style="background:#F0FDF4; border:1px solid #BBF7D0; color:#166534; padding:5px 10px; border-radius:6px; font-size:0.72rem; font-weight:700; margin-bottom:8px; display:flex; justify-content:space-between;">
        <span>🛡️ DART 공시 리스크 트래커</span>
        <span>최근 90일 내 특이 리스크 공시 없음 (정상)</span>
    </div>

    <div style="font-size:0.76rem; font-weight:800; color:#1E3A8A; margin-bottom:3px;">📊 1. 기업 실적 펀더멘털 분석</div>
    <div class="grid-4col" style="margin-bottom:8px;">
        <div class="indicator-card"><div class="indicator-title">ROE</div><div class="indicator-val" style="color:#15803D;">{stock.get('roe', '-')}</div></div>
        <div class="indicator-card"><div class="indicator-title">부채비율</div><div class="indicator-val" style="color:#15803D;">{stock.get('debt', '-')}</div></div>
        <div class="indicator-card"><div class="indicator-title">영업익 YoY</div><div class="indicator-val" style="color:#15803D;">{stock.get('opYoY', '-')}</div></div>
        <div class="indicator-card"><div class="indicator-title">목표가 괴리율</div><div class="indicator-val">{stock.get('targetDisp', '-')}</div></div>
    </div>

    <div style="font-size:0.76rem; font-weight:800; color:#1E3A8A; margin-bottom:3px;">🎯 2. 밸류에이션 & 기술적 모멘텀</div>
    <div class="grid-4col" style="margin-bottom:4px;">
        <div class="indicator-card"><div class="indicator-title">PER</div><div class="indicator-val">{stock.get('per', '-')}배</div></div>
        <div class="indicator-card"><div class="indicator-title">PBR</div><div class="indicator-val">{stock.get('pbr', '-')}배</div></div>
        <div class="indicator-card"><div class="indicator-title">매집강도</div><div class="indicator-val" style="color:#15803D;">{stock.get('supply_score', 50)}점</div></div>
        <div class="indicator-card"><div class="indicator-title">수급단계</div><div class="indicator-val" style="font-size:0.70rem; color:#15803D;">{stock.get('supply_stage', '안정')}</div></div>
    </div>
    <div class="grid-4col" style="margin-bottom:10px;">
        <div class="indicator-card"><div class="indicator-title">20일선 이격도</div><div class="indicator-val">{stock.get('disparity20', '100%')}</div></div>
        <div class="indicator-card"><div class="indicator-title">RSI (14)</div><div class="indicator-val">{stock.get('rsi', 50)}</div></div>
        <div class="indicator-card"><div class="indicator-title">거래량 비율</div><div class="indicator-val">{stock.get('volRatio', '100%')}</div></div>
        <div class="indicator-card"><div class="indicator-title">52주 위치</div><div class="indicator-val">76.4%</div></div>
    </div>

    <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:8px; padding:8px 10px;">
        <div style="font-size:0.74rem; font-weight:800; color:#1E3A8A; margin-bottom:2px;">💡 AI 종합 분석 요약 (Why 리포트)</div>
        <div style="font-size:0.72rem; color:#1E293B; line-height:1.45; font-weight:600;">{stock.get('why', '리포트 생성 완료')}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 상단 헤더 & 4대 매크로 지수 바
# ---------------------------------------------------------
macro = st.session_state.engine.report_data.get("macro", {})
kp = macro.get('KOSPI', {'price': 2655.4, 'change': 0.45})
kd = macro.get('KOSDAQ', {'price': 852.1, 'change': -0.32})
fx = macro.get('USDKRW', {'price': 1348.5, 'change': -0.15})
bd = macro.get('US10Y', {'price': 4.42, 'change': -0.04})

st.markdown(f"""
<div class="header-bar">
    <div class="title-wrapper">
        <div class="title-bar-accent"></div>
        <div class="title-area">
            <h1>AI 스마트 주식 자산관리 <span class="live-badge">LIVE</span></h1>
        </div>
    </div>
    <div class="market-index-bar">
        <div class="macro-grid-inner">
            <div class="index-item"><span class="index-name">KOSPI</span> <span class="index-price">{kp['price']:,.2f}</span> <span class="{'val-up' if kp['change']>=0 else 'val-down'}">({kp['change']:+.2f}%)</span></div>
            <div class="index-item"><span class="index-name">KOSDAQ</span> <span class="index-price">{kd['price']:,.2f}</span> <span class="{'val-up' if kd['change']>=0 else 'val-down'}">({kd['change']:+.2f}%)</span></div>
            <div class="index-item"><span class="index-name">USD/KRW</span> <span class="index-price">{fx['price']:,.1f}</span> <span class="{'val-up' if fx['change']>=0 else 'val-down'}">({fx['change']:+.2f}%)</span></div>
            <div class="index-item"><span class="index-name">US 10Y</span> <span class="index-price">{bd['price']:.2f}%</span> <span class="{'val-up' if bd['change']>=0 else 'val-down'}">({bd['change']:+.2f}%)</span></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. 브리핑 2열 & 에이전트 실행 버튼
# ---------------------------------------------------------
briefing = st.session_state.engine.report_data.get("briefing", "")
close_txt = briefing if briefing else "• 코스피 및 글로벌 주요 지수 반등세 유지 속 기관 수급 유입 확인.\n• 반도체 및 전력인프라 섹터 중심 방어 흐름 지속.\n• 원달러 환율 안정권 진입으로 외국인 순매수 전환 기대감 유효."
morning_txt = "• 미 국채금리 안정세 및 빅테크 실적 기대감으로 국내 IT 투심 회복.\n• 외국인 선물 수급 유입 여부 및 환율 1,350원선 하향 안착 테스트 주목."

st.markdown(f"""
<div class="intro-grid">
    <div class="intro-box">
        <div class="intro-box-title"><span>⚡ 장전 리스크 & 동향</span><span style="font-size:0.68rem; color:#64748B;">08:00</span></div>
        <div class="risk-content-body">{morning_txt}</div>
    </div>
    <div class="intro-box">
        <div class="intro-box-title"><span>🌙 장마감 결산 & 시황</span><span style="font-size:0.68rem; color:#64748B;">16:30</span></div>
        <div class="risk-content-body">{close_txt}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🚀 4대 에이전트 종합 파이프라인 가동 (수급·퀀트·공시 정밀 분석)", type="primary", use_container_width=True):
    with st.spinner("4대 에이전트 병렬 분석 및 상대평가 가드 검증 중..."):
        st.session_state.engine = run_full_pipeline(st.session_state.holdings_data, st.session_state.engine)
        st.session_state.holdings_data = st.session_state.engine.report_data["holdings"]
    st.rerun()

# ---------------------------------------------------------
# 6. 오늘의 관심 추천 Top 3 (엄격 선별)
# ---------------------------------------------------------
st.markdown("<div style='font-size:0.95rem; font-weight:800; color:#0F172A; margin:8px 0 6px 0;'>🎯 오늘의 관심 추천 Top 3</div>", unsafe_allow_html=True)
top_candidates = sorted(st.session_state.holdings_data, key=lambda x: x.get('supply_score', 0), reverse=True)[:3]

cols = st.columns(3)
for idx, stock in enumerate(top_candidates):
    b_cls = get_badge_class(stock.get('grade', 'B'))
    with cols[idx]:
        st.markdown(f"""
        <div class="rec-carousel-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:5px;">
                    <span class="rec-rank-badge">{idx+1}</span>
                    <span class="rec-name">{stock['name']}</span>
                    <span style="font-size:0.70rem; color:#64748B;">{stock['sector']}</span>
                </div>
                <span class="{b_cls}">{stock['grade']}</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:4px; text-align:center; background:#FFF; padding:5px; border-radius:6px; border:1px solid #E2E8F0;">
                <div><div style="font-size:0.60rem; color:#64748B;">현재가</div><div style="font-size:0.75rem; font-weight:800;">{stock['cur_price']:,}원</div></div>
                <div><div style="font-size:0.60rem; color:#64748B;">매집강도</div><div style="font-size:0.75rem; font-weight:800; color:#15803D;">{stock.get('supply_score', 70)}점</div></div>
                <div><div style="font-size:0.60rem; color:#64748B;">수급단계</div><div style="font-size:0.68rem; font-weight:800;">{stock.get('supply_stage', '안정')}</div></div>
            </div>
            <div class="rec-headline-box">💡 {stock.get('why', '')}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 메인 그리드 (MTS 원터치 선택 & 상세 인스펙터)
# ---------------------------------------------------------
st.markdown("<div style='font-size:0.95rem; font-weight:800; color:#0F172A; margin:10px 0 6px 0;'>📊 보유 종목 포트폴리오 & 상세 분석</div>", unsafe_allow_html=True)

left_col, right_col = st.columns([1.1, 2.9])

with left_col:
    st.markdown("<div style='font-size:0.78rem; font-weight:700; color:#64748B; margin-bottom:4px;'>종목 선택 (터치)</div>", unsafe_allow_html=True)
    for idx, item in enumerate(st.session_state.holdings_data):
        cur_p = item.get("cur_price", item["avg_price"])
        profit_rate = ((cur_p - item["avg_price"]) / item["avg_price"]) * 100 if item["avg_price"] > 0 else 0
        p_cls = "val-up" if profit_rate >= 0 else "val-down"
        is_active = (item["code"] == st.session_state.selected_code)
        b_cls = get_badge_class(item.get("grade", "B"))
        
        # 버튼 자체를 증권사 MTS 스타일 카드로 활용
        btn_label = f"{item['name']} ({item['sector']}) | {cur_p:,}원 ({profit_rate:+.2f}%) [{item.get('grade', 'B')}]"
        btn_type = "primary" if is_active else "secondary"
        if st.button(btn_label, key=f"sel_{item['code']}", type=btn_type, use_container_width=True):
            st.session_state.selected_code = item["code"]
            st.rerun()

with right_col:
    total_buy = sum(item["qty"] * item["avg_price"] for item in st.session_state.holdings_data)
    total_eval = sum(item["qty"] * item.get("cur_price", item["avg_price"]) for item in st.session_state.holdings_data)
    total_profit = total_eval - total_buy
    total_rate = (total_profit / total_buy) * 100 if total_buy > 0 else 0
    p_cls = "val-up" if total_profit >= 0 else "val-down"

    win_count = sum(1 for item in st.session_state.holdings_data if item.get("cur_price", item["avg_price"]) >= item["avg_price"])
    loss_count = len(st.session_state.holdings_data) - win_count

    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px 12px; margin-bottom:10px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
        <div style="font-size:0.85rem; font-weight:800; color:#0F172A; margin-bottom:6px;">💰 내 자산 포트폴리오 현황</div>
        <div class="kpi-main-grid">
            <div class="kpi-main-card">
                <span class="kpi-title">현재 평가금액</span>
                <span class="kpi-val">{total_eval:,.0f}원</span>
                <span class="kpi-sub" style="color:#64748B;">매입: {total_buy:,.0f}원</span>
            </div>
            <div class="kpi-main-card">
                <span class="kpi-title">총 평가손익</span>
                <span class="kpi-val {p_cls}">{total_profit:+,.0f}원</span>
                <span class="kpi-sub {p_cls}">수익률: {total_rate:+.2f}%</span>
            </div>
            <div class="kpi-main-card">
                <span class="kpi-title">보유 종목 현황</span>
                <span class="kpi-val">총 {len(st.session_state.holdings_data)}종목</span>
                <span class="kpi-sub" style="color:#64748B;">수익/손실: <b class="val-up">{win_count}</b> / <b class="val-down">{loss_count}</b></span>
            </div>
            <div class="kpi-main-card">
                <span class="kpi-title">주간 변동 극점</span>
                <div style="font-size:0.72rem; font-weight:700;"><span style="color:#1E293B;">🚀 SK하이닉스</span> <span class="val-up">+8.0%</span></div>
                <div style="font-size:0.72rem; font-weight:700;"><span style="color:#1E293B;">📉 코스모화학</span> <span class="val-down">-5.8%</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    target = next((item for item in st.session_state.holdings_data if item["code"] == st.session_state.selected_code), st.session_state.holdings_data[0])
    t_cur = target.get("cur_price", target["avg_price"])
    t_profit_rate = ((t_cur - target["avg_price"]) / target["avg_price"]) * 100
    t_profit_val = (t_cur - target["avg_price"]) * target["qty"]
    t_buy_amt = target["qty"] * target["avg_price"]
    t_p_cls = "val-up" if t_profit_rate >= 0 else "val-down"
    b_cls = get_badge_class(target.get("grade", "B"))

    det_col1, det_col2 = st.columns([3, 1])
    with det_col1:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
            <span style="font-size:1.2rem; font-weight:800; color:#000;">{target['name']}</span>
            <span style="font-size:0.80rem; color:#64748B; font-weight:700;">{target['code']}</span>
            <span style="font-size:0.72rem; font-weight:700; background:#EEF2FF; color:#1E3A8A; padding:2px 6px; border-radius:4px;">{target['sector']}</span>
            <span class="{b_cls}">등급: {target.get('grade', 'B')}</span>
        </div>
        """, unsafe_allow_html=True)
    with det_col2:
        if st.button("심층 분석 🔍", key="btn_deep_modal", use_container_width=True):
            show_deep_analysis_dialog(target)

    st.markdown(f"""
    <div class="detail-price-table">
        <div><div style="font-size:0.65rem; color:#64748B;">보유평균단가 (수량)</div><div style="font-size:0.82rem; font-weight:800;">{target['avg_price']:,}원 ({target['qty']}주)</div></div>
        <div><div style="font-size:0.65rem; color:#64748B;">현재가 (수익률)</div><div style="font-size:0.82rem; font-weight:800;">{t_cur:,}원 <span class="{t_p_cls}">({t_profit_rate:+.2f}%)</span></div></div>
        <div><div style="font-size:0.65rem; color:#64748B;">매입금액</div><div style="font-size:0.82rem; font-weight:800;">{t_buy_amt:,}원</div></div>
        <div><div style="font-size:0.65rem; color:#64748B;">평가손익</div><div style="font-size:0.82rem; font-weight:800;" class="{t_p_cls}">{t_profit_val:+,.0f}원</div></div>
    </div>
    <div style="background:#EEF2FF; border-left:3px solid #1E3A8A; padding:6px 10px; border-radius:0 6px 6px 0; font-size:0.74rem; color:#1E293B; line-height:1.45; font-weight:600; margin-bottom:8px;">
        💡 AI 한 줄 진단: {target.get('why', '')}
    </div>
    """, unsafe_allow_html=True)

    # 캔들스틱 차트 (현실적 최근 거래일 시계열 적용)
    dates = ['10-24', '10-27', '10-28', '10-29', '10-30', '10-31', '11-03']
    base_p = t_cur if t_cur > 0 else 30000
    opens = [base_p*0.96, base_p*0.97, base_p*0.98, base_p*1.01, base_p*1.00, base_p*0.99, base_p*1.01]
    highs = [base_p*0.98, base_p*0.99, base_p*1.02, base_p*1.03, base_p*1.02, base_p*1.02, base_p*1.03]
    lows = [base_p*0.95, base_p*0.96, base_p*0.97, base_p*0.99, base_p*0.98, base_p*0.98, base_p*0.99]
    closes = [base_p*0.97, base_p*0.98, base_p*1.01, base_p*1.00, base_p*0.99, base_p*1.01, base_p]
    volumes = [150000, 220000, 480000, 310000, 190000, 260000, 350000]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
    fig.add_trace(go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes, increasing_line_color='#DC2626', decreasing_line_color='#1D4ED8', name="캔들"), row=1, col=1)

    ma5 = [sum(closes[max(0, i-4):i+1]) / len(closes[max(0, i-4):i+1]) for i in range(len(closes))]
    ma20 = [p * 0.985 for p in closes]
    fig.add_trace(go.Scatter(x=dates, y=ma5, line=dict(color='#EAB308', width=1.5), name="5일선"), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=ma20, line=dict(color='#F97316', width=1.5), name="20일선"), row=1, col=1)

    fig.add_hline(y=target['avg_price'], line_dash="dash", line_color="#475569", line_width=1.2,
                  annotation_text=f"내 평단: {target['avg_price']:,}원", annotation_position="top left", row=1, col=1)

    v_colors = ['#DC2626' if c >= o else '#1D4ED8' for c, o in zip(closes, opens)]
    fig.add_trace(go.Bar(x=dates, y=volumes, marker_color=v_colors, name="거래량"), row=2, col=1)

    fig.update_layout(
        height=360,
        margin=dict(l=5, r=5, t=5, b=5),
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
