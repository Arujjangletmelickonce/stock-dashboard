import streamlit as st
import pandas as pd
from datetime import datetime
import yfinance as yf

# ------------------------------------------------
# ⚙️ 1. 페이지 설정 및 보안 강화 (메뉴 숨기기)
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
# 📥 2. 데이터 로딩 및 분류 시스템
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

available_dates = [col for col in df.columns if col != 'Category']
today_str = datetime.now().strftime('%Y-%m-%d')
future_dates = [d for d in available_dates if d >= today_str]
default_date_str = future_dates[0] if future_dates else available_dates[-1]
default_date_obj = datetime.strptime(default_date_str, '%Y-%m-%d').date()

# 💡 [핵심 기능] 주말/휴장일을 누르면 가장 가까운 개장일로 자동 스냅(보정)하는 함수
def get_valid_date(selected_obj):
    sel_str = selected_obj.strftime('%Y-%m-%d')
    if sel_str in available_dates:
        return sel_str, False # 변경 없음
    
    # 데이터가 없는 날(주말/휴장일)을 골랐다면, 가장 가까운 과거 개장일을 찾음
    date_objs = [datetime.strptime(d, '%Y-%m-%d').date() for d in available_dates]
    past_dates = [d for d in date_objs if d <= selected_obj]
    if past_dates:
        closest_date = max(past_dates).strftime('%Y-%m-%d')
    else:
        closest_date = min(date_objs).strftime('%Y-%m-%d')
    return closest_date, True # 날짜가 보정되었음을 알림

# ------------------------------------------------
# 🎨 3. 메인 화면 구성
# ------------------------------------------------
st.markdown("<h1 style='font-size: clamp(28px, 7vw, 40px); text-align: center;'>🔮 2026년 운명의 수정구슬</h1>", unsafe_allow_html=True)
st.write("---")

def highlight_status(val):
    if val == '스윗스팟': return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == '단기상승': return 'background-color: #f8d7da; color: #721c24;'
    elif val == '단기하락': return 'background-color: #cce5ff; color: #004085;'
    return ''

tab1, tab2, tab3 = st.tabs(["📅 날짜별 모아보기", "🔍 종목별 흐름보기", "🌐 전체 종목 현황"])

# --- 탭 1: 날짜별 모아보기 ---
with tab1:
    st.subheader("💡 오늘의 상태별 종목")
    col_d, col_c = st.columns(2)
    with col_d:
        raw_date1 = st.date_input("날짜 선택", default_date_obj, key="t1_d")
        sel_date1, is_changed1 = get_valid_date(raw_date1)
        if is_changed1:
            st.caption(f"ℹ️ 선택하신 날은 휴장일입니다. 가장 가까운 개장일({sel_date1})을 보여줍니다.")
            
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
        st.error(f"📈 단기상승")
        for t in d_data[d_data == '단기상승'].index: st.write(f"- {t}")
    with c3:
        st.info(f"📉 단기하락")
        for t in d_data[d_data == '단기하락'].index: st.write(f"- {t}")

# --- 탭 2: 종목별 흐름보기 (+차트) ---
with tab2:
    st.subheader("🗓️ 종목별 향후 10일 흐름")
    m_col, s_col = st.columns(2)
    with m_col:
        m_cat = st.selectbox("대분류", df['Category'].unique(), key="t2_m")
    with s_col:
        s_ticker = st.selectbox("소분류", df[df['Category'] == m_cat].index, key="t2_s")
    
    raw_date2 = st.date_input("시작일", default_date_obj, key="t2_date")
    sel_date2, is_changed2 = get_valid_date(raw_date2)
    if is_changed2:
        st.caption(f"ℹ️ 선택하신 날은 휴장일입니다. 가장 가까운 개장일({sel_date2})부터 시작합니다.")
        
    idx = available_dates.index(sel_date2)
    t_dates = available_dates[idx:idx+10]
    res = pd.DataFrame({"날짜": t_dates, "상태": df.loc[s_ticker, t_dates].values})
    st.dataframe(res.style.map(highlight_status, subset=['상태']), use_container_width=True, hide_index=True)

    # 💡 [새로운 기능] 개별 주식일 경우 하단에 실시간 주가 및 차트 표시
    if m_cat == '📈 개별 주식':
        st.write("---")
        st.subheader(f"📊 {s_ticker} 현재 주가 및 최근 3개월 차트")
        
        # 야후 파이낸스 인식을 위해 티커 이름 정리 (예: Berkshire Hathaway (BRK-B) -> BRK-B)
        yf_ticker = "BRK-B" if "BRK-B" in s_ticker else s_ticker
        
        try:
            # 야후 파이낸스에서 최근 3개월 데이터 불러오기
            stock_data = yf.Ticker(yf_ticker)
            hist = stock_data.history(period="3mo")
            
            if not hist.empty:
                last_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else last_price
                change = last_price - prev_price
                change_pct = (change / prev_price) * 100
                
                # 주가 표시
                st.metric(label=f"{s_ticker} 현재가 (USD)", 
                          value=f"${last_price:,.2f}", 
                          delta=f"{change:,.2f} ({change_pct:.2f}%)")
                
                # 차트 그리기
                st.line_chart(hist['Close'], use_container_width=True)
            else:
                st.info("해당 종목의 차트 데이터를 불러올 수 없습니다.")
        except Exception as e:
            st.error("차트를 불러오는 중 오류가 발생했습니다.")

# --- 탭 3: 전체 종목 현황 ---
with tab3:
    st.subheader("🌐 카테고리별 전체 현황")
    d3_col, c3_col = st.columns(2)
    with d3_col:
        raw_date3 = st.date_input("시작일", default_date_obj, key="t3_date")
        sel_date3, is_changed3 = get_valid_date(raw_date3)
        if is_changed3:
            st.caption(f"ℹ️ 휴장일 대신 {sel_date3} 데이터를 보여줍니다.")
    with c3_col:
        sel_cat3 = st.selectbox("카테고리", cats, key="t3_cat")
    
    idx3 = available_dates.index(sel_date3)
    t_dates3 = available_dates[idx3:idx3+7]
    v_df = df[df['Category'] == sel_cat3].copy() if sel_cat3 != '전체 보기' else df.copy().sort_values('Category')
    st.dataframe(v_df[['Category'] + t_dates3].style.map(highlight_status), use_container_width=True)
