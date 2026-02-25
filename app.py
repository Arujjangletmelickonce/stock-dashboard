import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ------------------------------------------------
# ⚙️ 1. 페이지 설정 및 보안 강화
# ------------------------------------------------
st.set_page_config(page_title="2026년 운명의 수정구슬", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDataFrame {width: 100%;}
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------
# 📥 2. 데이터 로딩, 분류 및 ETF 매핑
# ------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    try:
        sheet_url = st.secrets["gs_url"]
        df = pd.read_csv(sheet_url, index_col=0)
    except Exception as e:
        st.error(f"❌ 데이터를 불러올 수 없습니다. Secrets 설정을 확인하세요: {e}")
        st.stop()
    
    def get_category(ticker):
        markets = ['Australia', 'Brazil', 'Canada', 'China', 'Dow Jones Islamic Market Titans', 'Dow Jones Transports', 'Dow Jones Utilities', 'France', 'Germany', 'Great Britain', 'Hong Kong', 'India', 'Israel', 'Italy', 'Japan', 'Korea', 'Nasdaq', 'Russia', 'S&P 500 E-minis']
        bonds = ['10 Year Bond Yield 1994-', 'Fed Funds 1990-', '10 Year Treasury Notes', '30 Year Treasury Bonds']
        currencies = ['Australian Dollar', 'British Pound', 'Canadian Dollar', 'US Dollar Index', 'Euro Currency', 'Japanese Yen', 'Mexican Peso', 'New Zealand Dollar', 'Swiss Franc']
        crypto_etf = ['Comparison of Ethereum and Binance to GBTC', 'GBTC', 'URA', 'QQQ', 'USRT', 'FNGU']
        commodities = ['Copper', 'Gold', 'Palladium', 'Platinum', 'Silver', 'Cocoa', 'Coffee', 'Cotton', 'Lumber', 'Orange Juice', 'Sugar', 'Crude Oil Long-Term Cycle', 'Crude Oil', 'Heating Oil', 'Natural Gas', 'RBOB Unleaded', 'Feeder Cattle', 'Live Cattle', 'Lean Hogs', 'Corn', 'Oats', 'Soybeans', 'Soybean Meal', 'Soybean Oil', 'Wheat', 'Dow Jones Commodity Index', 'Goldman Sachs Commodity Index']
        
        if ticker in markets: return '🌎 국가 및 지수'
        elif ticker in bonds: return '🏦 금리 및 채권'
        elif ticker in currencies: return '💱 환율'
        elif ticker in crypto_etf: return '🪙 암호화폐 및 ETF'
        elif ticker in commodities: return '🛢️ 원자재'
        else: return '📈 개별 주식'

    df['Category'] = df.index.map(get_category)
    return df

df = load_data()

ETF_MAPPING = {
    'Australia': 'EWA', 'Brazil': 'EWZ', 'Canada': 'EWC', 'China': 'FXI',
    'France': 'EWQ', 'Germany': 'EWG', 'Great Britain': 'EWU', 'Hong Kong': 'EWH',
    'India': 'INDA', 'Israel': 'EIS', 'Italy': 'EWI', 'Japan': 'EWJ',
    'Korea': 'EWY', 'Nasdaq': 'QQQ', 'S&P 500 E-minis': 'SPY',
    'Dow Jones Transports': 'IYT', 'Dow Jones Utilities': 'XLU',
    '10 Year Treasury Notes': 'IEF', '30 Year Treasury Bonds': 'TLT',
    'Gold': 'GLD', 'Silver': 'SLV', 'Copper': 'CPER',
    'Crude Oil': 'USO', 'Natural Gas': 'UNG', 'Heating Oil': 'UHN',
    'Corn': 'CORN', 'Soybeans': 'SOYB', 'Wheat': 'WEAT',
    'Goldman Sachs Commodity Index': 'GSG', 'Dow Jones Commodity Index': 'DJP',
    'GBTC': 'GBTC', 'URA': 'URA', 'QQQ': 'QQQ', 'USRT': 'USRT', 'FNGU': 'FNGU'
}

available_dates = [col for col in df.columns if col != 'Category']
today_str = datetime.now().strftime('%Y-%m-%d')
future_dates = [d for d in available_dates if d >= today_str]
default_date_str = future_dates[0] if future_dates else available_dates[-1]
default_date_obj = datetime.strptime(default_date_str, '%Y-%m-%d').date()

def get_valid_date(selected_obj):
    sel_str = selected_obj.strftime('%Y-%m-%d')
    if sel_str in available_dates:
        return sel_str, False
    
    date_objs = [datetime.strptime(d, '%Y-%m-%d').date() for d in available_dates]
    past_dates = [d for d in date_objs if d <= selected_obj]
    if past_dates:
        closest_date = max(past_dates).strftime('%Y-%m-%d')
    else:
        closest_date = min(date_objs).strftime('%Y-%m-%d')
    return closest_date, True

# ------------------------------------------------
# 📊 [핵심] 차트 & 인사이트 생성 공통 함수
# ------------------------------------------------
def create_chart_and_insights(s_ticker, yf_ticker, display_name, sel_date_str, period_choice):
    if period_choice == "1주일": 
        yf_period, future_days = "5d", 5
    elif period_choice == "1개월": 
        yf_period, future_days = "1mo", 10
    else: 
        yf_period, future_days = "3mo", 30

    try:
        stock_data = yf.Ticker(yf_ticker)
        hist = stock_data.history(period=yf_period)
        
        if hist.empty:
            return None, "데이터 없음"
            
        hist.index = hist.index.tz_localize(None)
        
        # 1. 현재가 및 등락률 계산
        last_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else last_price
        change = last_price - prev_price
        change_pct = (change / prev_price) * 100
        
        # 2. [기능 1] 백테스트 적중률 계산
        correct_preds, total_preds = 0, 0
        for i in range(1, len(hist)):
            prev_date = hist.index[i-1].strftime('%Y-%m-%d')
            if prev_date in available_dates:
                pred = df.loc[s_ticker, prev_date]
                actual_ret = hist['Close'].iloc[i] - hist['Close'].iloc[i-1]
                
                if pred in ['단기상승', '스윗스팟'] and actual_ret > 0:
                    correct_preds += 1
                elif pred == '단기하락' and actual_ret <= 0:
                    correct_preds += 1
                total_preds += 1
                
        accuracy = (correct_preds / total_preds * 100) if total_preds > 0 else 0

        # 3. [기능 4] 모멘텀 뱃지 계산
        curr_idx = available_dates.index(sel_date_str)
        curr_status = df.loc[s_ticker, sel_date_str]
        forward_streak = 0
        
        for d in available_dates[curr_idx:]:
            if df.loc[s_ticker, d] == curr_status:
                forward_streak += 1
            else:
                break
                
        if curr_status == '스윗스팟': momentum_msg = f"🎯 **{curr_status}** (앞으로 {forward_streak}일간 유지 예정)"
        elif curr_status == '단기상승': momentum_msg = f"🔥 **{curr_status}** 흐름 (앞으로 {forward_streak}일간 유지 예정)"
        else: momentum_msg = f"❄️ **{curr_status}** 주의 (앞으로 {forward_streak}일간 유지 예정)"

        # 4. 차트 그리기
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(hist.index, hist['Close'], color='#1f77b4', linewidth=2, marker='o', markersize=4)
        
        last_actual_date = hist.index[-1]
        ax.axvline(x=last_actual_date, color='gray', linestyle='--', linewidth=1.5, alpha=0.8)
        
        y_max = ax.get_ylim()[1]
        ax.text(last_actual_date + timedelta(days=1), y_max, 'Future ▶', color='gray', fontsize=11, fontweight='bold', va='top')
        
        start_date = hist.index[0].date()
        end_date = last_actual_date.date() + timedelta(days=future_days)
        num_days = (end_date - start_date).days + 1
        
        last_bg_color = None
        for i in range(num_days):
            current_date_obj = start_date + timedelta(days=i)
            date_str = current_date_obj.strftime('%Y-%m-%d')
            
            if date_str in df.columns:
                status = df.loc[s_ticker, date_str]
                if status == '단기상승': last_bg_color = '#d4edda'
                elif status == '단기하락': last_bg_color = '#f8d7da'
                elif status == '스윗스팟': last_bg_color = '#fff3cd'
                else: last_bg_color = None
                    
            if last_bg_color:
                plot_date = datetime.combine(current_date_obj, datetime.min.time())
                start_x = plot_date - timedelta(days=0.5)
                end_x = plot_date + timedelta(days=0.5)
                ax.axvspan(start_x, end_x, color=last_bg_color, alpha=0.6, lw=0)
        
        ax.set_xlim(hist.index[0] - timedelta(days=1), last_actual_date + timedelta(days=future_days + 1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.xticks(rotation=45)
        ax.set_ylabel("Price (USD)")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        
        return {
            "fig": fig,
            "last_price": last_price,
            "change": change,
            "change_pct": change_pct,
            "accuracy": accuracy,
            "momentum_msg": momentum_msg
        }
        
    except Exception as e:
        return None, str(e)

# ------------------------------------------------
# 🎨 4. 메인 화면 구성 및 탭 분리
# ------------------------------------------------
st.markdown("<h1 style='font-size: clamp(28px, 7vw, 40px); text-align: center;'>🔮 2026년 운명의 수정구슬</h1>", unsafe_allow_html=True)
st.write("---")

def highlight_status(val):
    if val == '스윗스팟': return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == '단기상승': return 'background-color: #d4edda; color: #155724;'
    elif val == '단기하락': return 'background-color: #f8d7da; color: #721c24;'
    return ''

# [기능 5] 탭 4개로 확장
tab1, tab2, tab3, tab4 = st.tabs(["📅 날짜별 모아보기", "🔍 종목 상세 분석", "🌐 전체 현황", "⚖️ 두 종목 비교"])

# --- 탭 1: 날짜별 모아보기 ---
with tab1:
    st.subheader("💡 오늘의 상태별 종목")
    col_d, col_c = st.columns(2)
    with col_d:
        raw_date1 = st.date_input("날짜 선택", default_date_obj, key="t1_d")
        sel_date1, is_changed1 = get_valid_date(raw_date1)
        if is_changed1: st.caption(f"ℹ️ 휴장일 보정: {sel_date1} 기준")
            
    with col_c:
        cats = ['전체 보기'] + list(df['Category'].unique())
        sel_cat = st.selectbox("카테고리 선택", cats, key="t1_c")
    
    f_df = df[df['Category'] == sel_cat] if sel_cat != '전체 보기' else df
    d_data = f_df[sel_date1]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success(f"🎯 스윗스팟")
        for t in d_data[d_data == '스윗스팟'].index: st.write(f"- {t}")
    with c2:
        st.success(f"📈 단기상승")
        for t in d_data[d_data == '단기상승'].index: st.write(f"- {t}")
    with c3:
        st.error(f"📉 단기하락")
        for t in d_data[d_data == '단기하락'].index: st.write(f"- {t}")

# --- 탭 3: 전체 종목 현황 ---
with tab3:
    st.subheader("🌐 카테고리별 전체 현황")
    d3_col, c3_col = st.columns(2)
    with d3_col:
        raw_date3 = st.date_input("시작일", default_date_obj, key="t3_date")
        sel_date3, is_changed3 = get_valid_date(raw_date3)
        if is_changed3: st.caption(f"ℹ️ 휴장일 보정: {sel_date3} 기준")
    with c3_col:
        sel_cat3 = st.selectbox("카테고리", cats, key="t3_cat")
    
    idx3 = available_dates.index(sel_date3)
    t_dates3 = available_dates[idx3:idx3+7]
    v_df = df[df['Category'] == sel_cat3].copy() if sel_cat3 != '전체 보기' else df.copy().sort_values('Category')
    st.dataframe(v_df[['Category'] + t_dates3].style.map(highlight_status), use_container_width=True)

# --- 탭 2: 종목 상세 분석 (인사이트 통합) ---
with tab2:
    st.subheader("🗓️ 종목 상세 분석 및 예측")
    m_col, s_col = st.columns(2)
    with m_col:
        m_cat = st.selectbox("대분류", df['Category'].unique(), key="t2_m")
    with s_col:
        s_ticker = st.selectbox("소분류", df[df['Category'] == m_cat].index, key="t2_s")
    
    raw_date2 = st.date_input("기준일", default_date_obj, key="t2_date")
    sel_date2, is_changed2 = get_valid_date(raw_date2)
    if is_changed2: st.caption(f"ℹ️ 휴장일 보정: {sel_date2} 기준")
        
    idx = available_dates.index(sel_date2)
    t_dates = available_dates[idx:idx+10]
    res = pd.DataFrame({"날짜": t_dates, "상태": df.loc[s_ticker, t_dates].values})
    st.dataframe(res.style.map(highlight_status, subset=['상태']), use_container_width=True, hide_index=True)

    yf_ticker = "BRK-B" if "BRK-B" in s_ticker else s_ticker if m_cat == '📈 개별 주식' else ETF_MAPPING.get(s_ticker)
        
    if yf_ticker:
        st.write("---")
        display_name = f"{s_ticker} ({yf_ticker})" if m_cat != '📈 개별 주식' else s_ticker
        
        period_choice = st.radio("조회 기간:", ["1주일", "1개월", "3개월"], index=2, horizontal=True, key="t2_radio")
        
        # 차트 및 인사이트 데이터 생성
        chart_data = create_chart_and_insights(s_ticker, yf_ticker, display_name, sel_date2, period_choice)
        
        if isinstance(chart_data, dict):
            # 상단 인사이트 뱃지 표시
            st.info(f"💡 {chart_data['momentum_msg']}")
            
            col_metric, col_acc = st.columns(2)
            with col_metric:
                st.metric(label=f"{display_name} 현재가", value=f"${chart_data['last_price']:,.2f}", delta=f"{chart_data['change']:,.2f} ({chart_data['change_pct']:.2f}%)")
            with col_acc:
                st.metric(label=f"과거 {period_choice} 예측 적중률", value=f"{chart_data['accuracy']:.1f}%")

            st.pyplot(chart_data['fig'])
        else:
            st.warning("차트 데이터를 불러올 수 없습니다.")
    else:
        st.info("지원되는 ETF 티커가 없어 차트를 제공하지 않습니다.")

# --- 탭 4: 두 종목 비교 (신규 기능) ---
with tab4:
    st.subheader("⚖️ 두 종목 흐름 한눈에 비교하기")
    
    comp_date_raw = st.date_input("기준일 선택", default_date_obj, key="t4_date")
    comp_date, _ = get_valid_date(comp_date_raw)
    comp_period = st.radio("비교 기간:", ["1개월", "3개월"], index=1, horizontal=True, key="t4_radio")
    
    colA, colB = st.columns(2)
    
    # [왼쪽 종목 선택]
    with colA:
        st.markdown("### 🟦 종목 A")
        cat_A = st.selectbox("분류 A", df['Category'].unique(), key="t4_cat_A")
        tick_A = st.selectbox("종목 A", df[df['Category'] == cat_A].index, key="t4_tick_A")
        yf_A = "BRK-B" if "BRK-B" in tick_A else tick_A if cat_A == '📈 개별 주식' else ETF_MAPPING.get(tick_A)
        
        if yf_A:
            data_A = create_chart_and_insights(tick_A, yf_A, tick_A, comp_date, comp_period)
            if isinstance(data_A, dict):
                st.success(data_A['momentum_msg'])
                st.pyplot(data_A['fig'])
            else:
                st.warning("데이터 없음")
        else:
            st.info("차트 미지원 항목")

    # [오른쪽 종목 선택]
    with colB:
        st.markdown("### 🟧 종목 B")
        cat_B = st.selectbox("분류 B", df['Category'].unique(), key="t4_cat_B")
        tick_B = st.selectbox("종목 B", df[df['Category'] == cat_B].index, key="t4_tick_B")
        yf_B = "BRK-B" if "BRK-B" in tick_B else tick_B if cat_B == '📈 개별 주식' else ETF_MAPPING.get(tick_B)
        
        if yf_B:
            data_B = create_chart_and_insights(tick_B, yf_B, tick_B, comp_date, comp_period)
            if isinstance(data_B, dict):
                st.success(data_B['momentum_msg'])
                st.pyplot(data_B['fig'])
            else:
                st.warning("데이터 없음")
        else:
            st.info("차트 미지원 항목")
