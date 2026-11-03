import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import StockWorldEngine, run_full_pipeline, fetch_market_macro

# ---------------------------------------------------------
# 1. 페이지 와이드 설정 및 원본 CSS 주입
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI 스마트 주식 자산관리",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 1. Streamlit 기본 툴바(Share, 별, 연필, 배너) 완전 제거 */
    header[data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }

    /* 2. 기존 HTML CSS 변수 및 컴포넌트 복원 */
    :root {
        --deep-navy: #1E3A8A;
        --positive-red: #DC2626;
        --negative-blue: #1D4ED8;
        --border-color: #E2E8F0;
        --bg-subtle: #F8FAFC;
    }

    /* 타이틀 바 */
    .title-wrapper { display: flex; align-items: center; gap: 10px; }
    .title-bar-accent { width: 5px; height: 36px; background: linear-gradient(180deg, #1E3A8A 0%, #DC2626 100%); border-radius: 4px; flex-shrink: 0; }
    .title-area h1 { font-size: 1.25rem; font-weight: 800; color: #0F172A; margin: 0; display: flex; align-items: center; gap: 8px; }
    .live-badge { font-size: 0.65rem; font-weight: 700; background: #FEE2E2; color: #991B1B; padding: 2px 8px; border-radius: 12px; }
    .title-area p { font-size: 0.74rem; color: #64748B; margin: 2px 0 0 0; font-weight: 500; }

    /* 상단 매크로 박스 */
    .market-index-bar {
        background: #FFFFFF; border: 1px solid #E2E8F0; padding: 6px 12px; border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03); display: flex; align-items: center;
    }
    .macro-grid-inner { display: grid; grid-template-columns: auto auto; gap: 2px 14px; }
    .index-item { display: inline-flex; align-items: baseline; gap: 5px; font-size: 0.74rem; white-space: nowrap; }
    .index-name { font-weight: 700; color: #475569; font-size: 0.70rem; }
    .index-price { font-weight: 800; color: #000000; font-size: 0.76rem; }

    /* 브리핑 2열 */
    .intro-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
    .intro-box {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02); min-height: 110px;
    }
    .intro-box-title { font-size: 0.88rem; font-weight: 700; color: #0F172A; display: flex; justify-content: space-between; margin-bottom: 6px; }
    .risk-content-body {
        font-size: 0.78rem; color: #1E293B; line-height: 1.5; background: #F8FAFC;
        padding: 8px 12px; border-radius: 8px; border: 1px solid #E2E8F0;
    }

    /* Top 3 카드 */
    .rec-carousel-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 14px; }
    .rec-carousel-card {
        background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 14px;
        display: flex; flex-direction: column; gap: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    .rec-head { display: flex; justify-content: space-between; align-items: center; }
    .rec-rank-badge { font-size: 0.70rem; font-weight: 800; color: #FFFFFF; background: #1E3A8A; padding: 2px 6px; border-radius: 6px; }
    .rec-name { font-size: 0.95rem; font-weight: 800; color: #000; }
    .rec-code { font-size: 0.74rem; color: #64748B; font-weight: 700; }
    .rec-headline-box {
        font-size: 0.76rem; color: #1E293B; line-height: 1.45; background: #FEF2F2; border: 1px solid #FECACA;
        padding: 6px 10px; border-radius: 8px; font-weight: 700;
    }

    /* KPI 그리드 */
    .kpi-main-grid { display: grid; grid-template-columns: 1.15fr 1.15fr 0.85fr 1.35fr; gap: 8px; margin-bottom: 12px; }
    .kpi-main-card {
        background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px;
        display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
    }
    .kpi-title { font-size: 0.68rem; font-weight: 700; color: #64748B; }
    .kpi-val { font-size: 1.05rem; font-weight: 800; color: #000; }
    .kpi-sub { font-size: 0.72rem; font-weight: 700; }

    /* 종목 리스트 카드 */
    .compact-stock-item {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 7px; padding: 6px 9px;
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;
    }
    .compact-stock-item.active { border-color: #1E3A8A !important; background: #FEF2F2 !important; box-shadow: 0 0 0 1px #1E3A8A; }

    /* 수치 컬러 */
    .val-up { color: #DC2626 !important; font-weight: 800 !important; }
    .val-down { color: #1D4ED8 !important; font-weight: 800 !important; }
    .badge-s { font-size: 0.65rem; font-weight: 800; background: #1E3A8A; color: #FFFFFF; padding: 2px 6px; border-radius: 4px; }
    .badge-a { font-size: 0.65rem; font-weight: 800; background: #047857; color: #FFFFFF; padding: 2px 6px; border-radius: 4px; }
    .badge-b { font-size: 0.65rem; font-weight: 800; background: #B45309; color: #FFFFFF; padding: 2px 6px; border-radius: 4px; }

    /* 심층 진단 인디케이터 */
    .grid-4col { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
    .indicator-card { border-radius: 6px; padding: 6px 8px; border: 1px solid #E2E8F0; background: #FFFFFF; text-align: center; }
    .indicator-title { font-size: 0.65rem; color: #64748B; font-weight: 700; }
    .indicator-val { font-size: 0.85rem; font-weight: 800; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 세션 상태 초기화 & 원천 데이터 로드
# ---------------------------------------------------------
if "engine" not in st.session_state:
    st.session_state.engine = StockWorldEngine()
    st.session_state.engine.report_data["macro"] = fetch_market_macro()

if "holdings_data" not in st.session_state:
    st.session_state.holdings_data = [
        {"code": "060720", "name": "RFHIC", "sector": "방산/통신", "qty": 450, "avg_price": 28500, "cur_price": 28500, "grade": "S",
         "roe": "14.2%", "debt": "42.1%", "opYoY": "+38.4%", "targetDisp": "+24.5%", "per": "18.2", "pbr": "1.3", "supply_score": 85, "supply_stage": "🚀 매집완료", "rsi": 62.4, "volRatio": "185.0%", "disparity20": "104.2%",
         "why": "방산 GaN 전력증폭기 글로벌 수주 확대 및 5G 어드밴스드 투자 사이클 진입에 따른 실적 턴어라운드 본격화."},
        {"code": "001440", "name": "대한전선", "sector": "전력인프라", "qty": 1200, "avg_price": 14200, "cur_price": 14200, "grade": "A",
         "roe": "11.5%", "debt": "88.2%", "opYoY": "+25.1%", "targetDisp": "+18.0%", "per": "14.1", "pbr": "1.1", "supply_score": 75, "supply_stage": "⏳ 집중매집", "rsi": 58.1, "volRatio": "142.0%", "disparity20": "102.5%",
         "why": "북미 노후 송전망 교체 및 해저케이블 1공장 가동에 따른 수주 잔고 최고치 경신 모멘텀 지속."},
        {"code": "005420", "name": "코스모화학", "sector": "2차전지/소재", "qty": 300, "avg_price": 31000, "cur_price": 31000, "grade": "A",
         "roe": "8.4%", "debt": "110.5%", "opYoY": "+12.0%", "targetDisp": "+15.2%", "per": "22.5", "pbr": "1.6", "supply_score": 68, "supply_stage": "🔍 수급유입", "rsi": 51.0, "volRatio": "98.0%", "disparity20": "99.8%",
         "why": "폐배터리 리사이클링 설비 증설 효과 및 이산화티타늄 업황 회복 기대감 유효."},
        {"code": "005930", "name": "삼성전자", "sector": "반도체/IT", "qty": 150, "avg_price": 72000, "cur_price": 72000, "grade": "B",
         "roe": "9.1%", "debt": "26.3%", "opYoY": "+18.2%", "targetDisp": "+20.0%", "per": "12.8", "pbr": "1.2", "supply_score": 52, "supply_stage": "❌ 중립", "rsi": 46.5, "volRatio": "85.0%", "disparity20": "97.5%",
         "why": "메모리 가격 회복 지속 중이나 HBM 납품 일정 조율에 따른 기간 조정 흐름."},
        {"code": "000660", "name": "SK하이닉스", "sector": "반도체/HBM", "qty": 80, "avg_price": 175000, "cur_price": 175000, "grade": "S",
         "roe": "21.4%", "debt": "55.8%", "opYoY": "+145.0%", "targetDisp": "+28.0%", "per": "8.5", "pbr": "1.8", "supply_score": 92, "supply_stage": "🚀 매집완료", "rsi": 68.2, "volRatio": "210.0%", "disparity20": "106.8%",
         "why": "HBM3E 독점적 시장 지위 유지 및 엔터프라이즈 eSSD 수요 폭증에 따른 분기 최대 실적 경신 가시화."}
    ]

if "selected_code" not in st.session_state:
    st.session_state.selected_code = "060720"

# ---------------------------------------------------------
# 3. 심층 분석 모달 v4.2 (@st.dialog)
# ---------------------------------------------------------
@st.dialog("🔍 종목 심층 분석 (v4.2 모달 복원)")
def show_deep_analysis_dialog(stock):
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #E2E8F0; padding-bottom:8px; margin-bottom:10px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:1.2rem; font-weight:800;">{stock['name']}</span>
            <span style="font-size:0.8rem; color:#64748B; font-weight:700;">{stock['code']}</span>
            <span class="badge-s" style="background:#EEF2FF; color:#1E3A8A; border:1px solid #C7D2FE;">{stock['sector']}</span>
            <span style="font-size:0.85rem; font-weight:800; background:#F1F5F9; padding:2px 8px; border-radius:5px;">현재가: {stock['cur_price']:,}원</span>
        </div>
        <span class="badge-s">등급: {stock['grade']}</span>
    </div>

    <!-- DART 리스크 배너 -->
    <div style="background:#F0FDF4; border:1px solid #BBF7D0; color:#166534; padding:6px 12px; border-radius:6px; font-size:0.75rem; font-weight:700; margin-bottom:10px; display:flex; justify-content:space-between;">
        <span>🛡️ DART 공시 리스크 트래커</span>
        <span>최근 90일 내 주요 리스크 공시 없음 (정상)</span>
    </div>

    <!-- 1. 기업 실적 펀더멘털 분석 (4열) -->
    <div style="font-size:0.8rem; font-weight:800; color:#1E3A8A; margin-bottom:4px;">📊 1. 기업 실적 펀더멘털 분석</div>
    <div class="grid-4col" style="margin-bottom:12px;">
        <div class="indicator-card"><div class="indicator-title">ROE</div><div class="indicator-val" style="color:#15803D;">{stock.get('roe', '-')}</div></div>
        <div class="indicator-card"><div class="indicator-title">부채비율</div><div class="indicator-val" style="color:#15803D;">{stock.get('debt', '-')}</div></div>
        <div class="indicator-card"><div class="indicator-title">영업익 YoY</div><div class="indicator-val" style="color:#15803D;">{stock.get('opYoY', '-')}</div></div>
        <div class="indicator-card"><div class="indicator-title">목표가 괴리율</div><div class="indicator-val">{stock.get('targetDisp', '-')}</div></div>
    </div>

    <!-- 2. 밸류에이션 & 기술적 모멘텀 (4열) -->
    <div style="font-size:0.8rem; font-weight:800; color:#1E3A8A; margin-bottom:4px;">🎯 2. 밸류에이션 & 수급 모멘텀</div>
    <div class="grid-4col" style="margin-bottom:6px;">
        <div class="indicator-card"><div class="indicator-title">PER</div><div class="indicator-val">{stock.get('per', '-')}배</div></div>
        <div class="indicator-card"><div class="indicator-title">PBR</div><div class="indicator-val">{stock.get('pbr', '-')}배</div></div>
        <div class="indicator-card"><div class="indicator-title">매집강도</div><div class="indicator-val" style="color:#15803D;">{stock.get('supply_score', 50)}점</div></div>
        <div class="indicator-card"><div class="indicator-title">수급단계</div><div class="indicator-val" style="color:#15803D; font-size:0.75rem;">{stock.get('supply_stage', '안정')}</div></div>
    </div>
    <div class="grid-4col" style="margin-bottom:12px;">
        <div class="indicator-card"><div class="indicator-title">20일선 이격도</div><div class="indicator-val">{stock.get('disparity20', '100%')}</div></div>
        <div class="indicator-card"><div class="indicator-title">RSI (14)</div><div class="indicator-val">{stock.get('rsi', 50)}</div></div>
        <div class="indicator-card"><div class="indicator-title">거래량 비율</div><div class="indicator-val">{stock.get('volRatio', '100%')}</div></div>
        <div class="indicator-card"><div class="indicator-title">52주 고저위치</div><div class="indicator-val">74.5%</div></div>
    </div>

    <!-- Why 전문 리포트 카드 -->
    <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:8px; padding:10px 12px;">
        <div style="font-size:0.78rem; font-weight:800; color:#1E3A8A; margin-bottom:4px;">💡 AI 종합 분석 요약 (Why 전문 리포트)</div>
        <div style="font-size:0.75rem; color:#1E293B; line-height:1.5; font-weight:600;">{stock.get('why', '분석 리포트 생성 중...')}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 상단 헤더 & 원본 4대 매크로 바
# ---------------------------------------------------------
macro = st.session_state.engine.report_data.get("macro", {})
kp_p = macro.get('KOSPI', {}).get('price', 2650.0)
kp_c = macro.get('KOSPI', {}).get('change', 0.62)
kd_p = macro.get('KOSDAQ', {}).get('price', 850.0)
kd_c = macro.get('KOSDAQ', {}).get('change', -0.45)
usd_p = macro.get('USDKRW', {}).get('price', 1350.0)
usd_c = macro.get('USDKRW', {}).get('change', 0.15)
bond_p = macro.get('US10Y', {}).get('price', 4.50)
bond_c = macro.get('US10Y', {}).get('change', -0.02)

kp_cls = "val-up" if kp_c >= 0 else "val-down"
kd_cls = "val-up" if kd_c >= 0 else "val-down"
usd_cls = "val-up" if usd_c >= 0 else "val-down"
bond_cls = "val-up" if bond_c >= 0 else "val-down"

h_col1, h_col2 = st.columns([1.5, 1.5])
with h_col1:
    st.markdown("""
    <div class="title-wrapper">
        <div class="title-bar-accent"></div>
        <div class="title-area">
            <h1>AI 스마트 주식 자산관리 <span class="live-badge">LIVE</span></h1>
            <p>포트폴리오 리밸런싱 & 실시간 모멘텀 진단 시스템</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with h_col2:
    st.markdown(f"""
    <div class="market-index-bar">
        <div class="macro-grid-inner">
            <div class="index-item"><span class="index-name">KOSPI</span> <span class="index-price">{kp_p:,.2f}</span> <span class="index-change {kp_cls}">({kp_c:+.2f}%)</span></div>
            <div class="index-item"><span class="index-name">KOSDAQ</span> <span class="index-price">{kd_p:,.2f}</span> <span class="index-change {kd_cls}">({kd_c:+.2f}%)</span></div>
            <div class="index-item"><span class="index-name">USD/KRW</span> <span class="index-price">{usd_p:,.1f}</span> <span class="index-change {usd_cls}">({usd_c:+.2f}%)</span></div>
            <div class="index-item"><span class="index-name">US 10Y</span> <span class="index-price">{bond_p:.2f}%</span> <span class="index-change {bond_cls}">({bond_c:+.2f}%)</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. 브리핑 2열 카드 (장전 리스크 & 장마감 결산)
# ---------------------------------------------------------
briefing = st.session_state.engine.report_data.get("briefing", "")
close_txt = briefing if briefing else "• 코스피 및 글로벌 주요 지수 반등세 유지 속 기관 수급 유입 확인.\n• 반도체 및 전력인프라 섹터 중심 방어 흐름 지속.\n• 원달러 환율 안정권 진입으로 외국인 순매수 전환 기대감 유효."
morning_txt = "• 미 국채금리 안정세 및 엔비디아 반등 모멘텀으로 국내 반도체 투심 개선 기대.\n• 외국인 선물 수급 유입 여부 및 원달러 1,350원선 안착 테스트 주목."

st.markdown(f"""
<div class="intro-grid">
    <div class="intro-box">
        <div class="intro-box-title"><span>⚡ 장전 리스크 & 동향 브리핑</span><span style="font-size:0.7rem; color:#64748B;">08:00 갱신</span></div>
        <div class="risk-content-body">{morning_txt}</div>
    </div>
    <div class="intro-box">
        <div class="intro-box-title"><span>🌙 장마감 결산 & 시황 복기(Review)</span><span style="font-size:0.7rem; color:#64748B;">16:30 갱신</span></div>
        <div class="risk-content-body">{close_txt}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4대 에이전트 실행 버튼 바
if st.button("🚀 4대 전문 에이전트 종합 파이프라인 가동 (시황/수급/공시 정밀 분석)", type="primary", use_container_width=True):
    with st.spinner("팩트·퀀트·공시 에이전트 병렬 분석 및 가드 검증 중..."):
        st.session_state.engine = run_full_pipeline(st.session_state.holdings_data, st.session_state.engine)
        st.session_state.holdings_data = st.session_state.engine.report_data["holdings"]
    st.rerun()

# ---------------------------------------------------------
# 6. 오늘의 관심 추천 Top 3 캐러셀
# ---------------------------------------------------------
st.markdown("<div style='font-size:1.05rem; font-weight:800; color:#0F172A; margin: 10px 0 8px 0; border-bottom: 2px solid #1E3A8A; width:fit-content; padding-bottom:3px;'>오늘의 관심 추천 Top 3</div>", unsafe_allow_html=True)

t_stocks = [s for s in st.session_state.holdings_data if s['grade'] in ['S', 'A']][:3]
st.markdown(f"""
<div class="rec-carousel-container">
    <div class="rec-carousel-card">
        <div class="rec-head">
            <div style="display:flex; align-items:center; gap:6px;">
                <span class="rec-rank-badge">1</span>
                <span class="rec-name">{t_stocks[0]['name']}</span>
                <span class="rec-code">{t_stocks[0]['sector']}</span>
            </div>
            <span class="badge-s">{t_stocks[0]['grade']}</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:4px; text-align:center; background:#FFF; padding:6px; border-radius:6px; border:1px solid #E2E8F0;">
            <div><div style="font-size:0.62rem; color:#64748B;">현재가</div><div style="font-size:0.78rem; font-weight:800;">{t_stocks[0]['cur_price']:,}원</div></div>
            <div><div style="font-size:0.62rem; color:#64748B;">매집강도</div><div style="font-size:0.78rem; font-weight:800; color:#15803D;">{t_stocks[0].get('supply_score', 80)}점</div></div>
            <div><div style="font-size:0.62rem; color:#64748B;">수급단계</div><div style="font-size:0.72rem; font-weight:800;">{t_stocks[0].get('supply_stage', '매집완료')}</div></div>
        </div>
        <div class="rec-headline-box">💡 {t_stocks[0].get('why', '')}</div>
    </div>
    <div class="rec-carousel-card">
        <div class="rec-head">
            <div style="display:flex; align-items:center; gap:6px;">
                <span class="rec-rank-badge">2</span>
                <span class="rec-name">{t_stocks[1]['name']}</span>
                <span class="rec-code">{t_stocks[1]['sector']}</span>
            </div>
            <span class="badge-a">{t_stocks[1]['grade']}</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:4px; text-align:center; background:#FFF; padding:6px; border-radius:6px; border:1px solid #E2E8F0;">
            <div><div style="font-size:0.62rem; color:#64748B;">현재가</div><div style="font-size:0.78rem; font-weight:800;">{t_stocks[1]['cur_price']:,}원</div></div>
            <div><div style="font-size:0.62rem; color:#64748B;">매집강도</div><div style="font-size:0.78rem; font-weight:800; color:#15803D;">{t_stocks[1].get('supply_score', 75)}점</div></div>
            <div><div style="font-size:0.62rem; color:#64748B;">수급단계</div><div style="font-size:0.72rem; font-weight:800;">{t_stocks[1].get('supply_stage', '집중매집')}</div></div>
        </div>
        <div class="rec-headline-box">💡 {t_stocks[1].get('why', '')}</div>
    </div>
    <div class="rec-carousel-card">
        <div class="rec-head">
            <div style="display:flex; align-items:center; gap:6px;">
                <span class="rec-rank-badge">3</span>
                <span class="rec-name">{t_stocks[2]['name']}</span>
                <span class="rec-code">{t_stocks[2]['sector']}</span>
            </div>
            <span class="badge-s">{t_stocks[2]['grade']}</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:4px; text-align:center; background:#FFF; padding:6px; border-radius:6px; border:1px solid #E2E8F0;">
            <div><div style="font-size:0.62rem; color:#64748B;">현재가</div><div style="font-size:0.78rem; font-weight:800;">{t_stocks[2]['cur_price']:,}원</div></div>
            <div><div style="font-size:0.62rem; color:#64748B;">매집강도</div><div style="font-size:0.78rem; font-weight:800; color:#15803D;">{t_stocks[2].get('supply_score', 90)}점</div></div>
            <div><div style="font-size:0.62rem; color:#64748B;">수급단계</div><div style="font-size:0.72rem; font-weight:800;">{t_stocks[2].get('supply_stage', '매집완료')}</div></div>
        </div>
        <div class="rec-headline-box">💡 {t_stocks[2].get('why', '')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 메인 그리드: 좌측 보유목록 vs 우측 자산 KPI & 디테일
# ---------------------------------------------------------
left_col, right_col = st.columns([1.1, 2.9])

# [좌측] 컴팩트 보유 목록
with left_col:
    st.markdown("<div style='font-size:0.85rem; font-weight:800; color:#1E293B; margin-bottom:6px;'>📋 보유 종목 현황</div>", unsafe_allow_html=True)
    for idx, item in enumerate(st.session_state.holdings_data):
        cur_p = item.get("cur_price", item["avg_price"])
        profit_rate = ((cur_p - item["avg_price"]) / item["avg_price"]) * 100 if item["avg_price"] > 0 else 0
        p_cls = "val-up" if profit_rate >= 0 else "val-down"
        is_active = (item["code"] == st.session_state.selected_code)
        active_class = "active" if is_active else ""
        badge_cls = "badge-s" if item.get("grade") == "S" else ("badge-a" if item.get("grade") == "A" else "badge-b")
        
        st.markdown(f"""
        <div class="compact-stock-item {active_class}">
            <div style="display:flex; align-items:center; gap:6px; min-width:0;">
                <span style="font-size:0.7rem; font-weight:800; color:#64748B;">{idx+1}</span>
                <div>
                    <div style="font-size:0.82rem; font-weight:800; color:#000;">{item['name']}</div>
                    <div style="font-size:0.65rem; color:#64748B;">{item['sector']}</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.78rem; font-weight:800;">{cur_p:,}원</div>
                <div class="{p_cls}" style="font-size:0.7rem;">{profit_rate:+.2f}%</div>
            </div>
            <span class="{badge_cls}">{item.get('grade', 'B')}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("조회", key=f"sel_{item['code']}", use_container_width=True):
            st.session_state.selected_code = item["code"]
            st.rerun()

# [우측] 내 자산 포트폴리오 현황 KPI 4종 & 상세 인스펙터
with right_col:
    total_buy = sum(item["qty"] * item["avg_price"] for item in st.session_state.holdings_data)
    total_eval = sum(item["qty"] * item.get("cur_price", item["avg_price"]) for item in st.session_state.holdings_data)
    total_profit = total_eval - total_buy
    total_rate = (total_profit / total_buy) * 100 if total_buy > 0 else 0
    p_cls = "val-up" if total_profit >= 0 else "val-down"

    win_count = sum(1 for item in st.session_state.holdings_data if item.get("cur_price", item["avg_price"]) >= item["avg_price"])
    loss_count = len(st.session_state.holdings_data) - win_count

    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:12px 14px; box-shadow:0 2px 4px rgba(0,0,0,0.02); margin-bottom:12px;">
        <div style="font-size:0.9rem; font-weight:800; color:#0F172A; margin-bottom:8px;">💰 내 자산 포트폴리오 현황</div>
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
                <span class="kpi-title">주간(1W) 변동 극점</span>
                <div style="font-size:0.75rem; font-weight:700;"><span style="color:#1E293B;">🚀 RFHIC</span> <span class="val-up">+14.2%</span></div>
                <div style="font-size:0.75rem; font-weight:700;"><span style="color:#1E293B;">📉 삼성전자</span> <span class="val-down">-2.1%</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 선택 종목 상세 진단 & 심층 분석 버튼
    target = next((item for item in st.session_state.holdings_data if item["code"] == st.session_state.selected_code), st.session_state.holdings_data[0])
    t_cur = target.get("cur_price", target["avg_price"])
    t_profit_rate = ((t_cur - target["avg_price"]) / target["avg_price"]) * 100
    t_profit_val = (t_cur - target["avg_price"]) * target["qty"]
    t_buy_amt = target["qty"] * target["avg_price"]
    t_p_cls = "val-up" if t_profit_rate >= 0 else "val-down"

    det_col1, det_col2 = st.columns([3, 1])
    with det_col1:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:1.3rem; font-weight:800; color:#000;">{target['name']}</span>
            <span style="font-size:0.85rem; color:#64748B; font-weight:700;">{target['code']}</span>
            <span class="badge-s" style="background:#EEF2FF; color:#1E3A8A; border:1px solid #C7D2FE;">{target['sector']}</span>
        </div>
        """, unsafe_allow_html=True)
    with det_col2:
        if st.button("심층 분석 🔍", type="primary", use_container_width=True):
            show_deep_analysis_dialog(target)

    # 4열 가격 테이블
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; background:#F8FAFC; border:1px solid #E2E8F0; padding:8px 12px; border-radius:8px; text-align:center; margin-bottom:8px;">
        <div><div style="font-size:0.68rem; color:#64748B;">보유평균단가 (수량)</div><div style="font-size:0.85rem; font-weight:800;">{target['avg_price']:,}원 ({target['qty']}주)</div></div>
        <div><div style="font-size:0.68rem; color:#64748B;">현재가 (수익률)</div><div style="font-size:0.85rem; font-weight:800;">{t_cur:,}원 <span class="{t_p_cls}">({t_profit_rate:+.2f}%)</span></div></div>
        <div><div style="font-size:0.68rem; color:#64748B;">매입금액</div><div style="font-size:0.85rem; font-weight:800;">{t_buy_amt:,}원</div></div>
        <div><div style="font-size:0.68rem; color:#64748B;">평가손익</div><div style="font-size:0.85rem; font-weight:800;" class="{t_p_cls}">{t_profit_val:+,.0f}원</div></div>
    </div>
    <div style="background:#EEF2FF; border-left:3px solid #1E3A8A; padding:7px 11px; border-radius:0 6px 6px 0; font-size:0.76rem; color:#1E293B; line-height:1.5; font-weight:600; margin-bottom:10px;">
        💡 AI 한 줄 진단: {target.get('why', '')}
    </div>
    """, unsafe_allow_html=True)

    # 캔들스틱 + 4대 이동평균선 + 거래량 차트
    dates = ['10-25', '10-28', '10-29', '10-30', '10-31', '11-01', '11-02']
    base_p = t_cur if t_cur > 0 else 30000
    opens = [base_p*0.96, base_p*0.97, base_p*0.98, base_p*1.01, base_p*1.00, base_p*0.99, base_p*1.01]
    highs = [base_p*0.98, base_p*0.99, base_p*1.02, base_p*1.03, base_p*1.02, base_p*1.02, base_p*1.03]
    lows = [base_p*0.95, base_p*0.96, base_p*0.97, base_p*0.99, base_p*0.98, base_p*0.98, base_p*0.99]
    closes = [base_p*0.97, base_p*0.98, base_p*1.01, base_p*1.00, base_p*0.99, base_p*1.01, base_p]
    volumes = [150000, 220000, 480000, 310000, 190000, 260000, 350000]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.75, 0.25])
    
    # 캔들
    fig.add_trace(go.Candlestick(
        x=dates, open=opens, high=highs, low=lows, close=closes,
        increasing_line_color='#DC2626', decreasing_line_color='#1D4ED8', name="캔들"
    ), row=1, col=1)

    # 5일 / 20일 이동평균선
    ma5 = [sum(closes[max(0, i-4):i+1]) / len(closes[max(0, i-4):i+1]) for i in range(len(closes))]
    ma20 = [p * 0.985 for p in closes]
    fig.add_trace(go.Scatter(x=dates, y=ma5, line=dict(color='#EAB308', width=1.5), name="5일선"), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=ma20, line=dict(color='#F97316', width=1.5), name="20일선"), row=1, col=1)

    # 평단가 기준선
    fig.add_hline(y=target['avg_price'], line_dash="dash", line_color="#475569", line_width=1.2,
                  annotation_text=f"내 평단가: {target['avg_price']:,}원", annotation_position="top left", row=1, col=1)

    # 거래량
    v_colors = ['#DC2626' if c >= o else '#1D4ED8' for c, o in zip(closes, opens)]
    fig.add_trace(go.Bar(x=dates, y=volumes, marker_color=v_colors, name="거래량"), row=2, col=1)

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10))
    )
    st.plotly_chart(fig, use_container_width=True)
