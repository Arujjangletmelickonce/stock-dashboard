import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# ------------------------------------------------
# ⚙️ 1. 페이지 설정 및 보안 (메뉴 숨기기)
# ------------------------------------------------
st.set_page_config(page_title="2026년 운명의 수정구슬", page_icon="🔮", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none !important;}
    </style>
    """, unsafe_allow_html=True)



# ------------------------------------------------
# 📥 3. 데이터 로드 및 휴장일 계산
# ------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    try:
        sheet_url = st.secrets["gs_url"]
        df = pd.read_csv(sheet_url, index_col=0)
    except:
        st.error("❌ 구글 시트 연결을 확인하세요.")
        st.stop()
    
    # 카테고리 분류 함수
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

# --- 🗓️ 달력 제어 로직 ---
# 데이터에 있는 날짜들만 리스트로 추출
available_dates_str = [col for col in df.columns if col != 'Category']
available_dates_obj = [datetime.strptime(d, '%Y-%m-%d').date() for d in available_dates_str]

# 2026년 전체 범위 설정
min_date = available_dates_obj[0]
max_date = available_dates_obj[-1]

# 비활성화할 날짜 계산 (전체 범위 중 데이터가 없는 날 = 주말 및 휴장일)
all_days = [min_date + timedelta(days=x) for x in range((max_date - min_date).days + 1)]
disabled_days = [d for d in all_days if d not in available_dates_obj]

# 오늘 기준 가장 가까운 개장일 설정
today = date.today()
default_date = today if today in available_dates_obj else min_date

# ------------------------------------------------
# 🎨 4. 메인 화면 및 탭 구성
# ------------------------------------------------
st.markdown("<h1 style='font-size: clamp(28px, 7vw, 40px); text-align: center;'>🔮 2026년 운명의 수정구슬</h1>", unsafe_allow_html=True)
st.write("---")

def highlight_status(val):
    if val == '스윗스팟': return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == '단기상승': return 'background-color: #f8d7da; color: #721c24;'
    elif val == '단기하락': return 'background-color: #cce5ff; color: #004085;'
    return ''

tab1, tab2, tab3 = st.tabs(["📅 날짜별 모아보기", "🔍 종목별 흐름보기", "🌐 전체 종목 현황"])

# --- 탭 1: 날짜별 ---
with tab1:
    st.subheader("💡 오늘의 상태별 종목")
    c_d, c_c = st.columns(2)
    with c_d:
        # ★ 핵심 기능: disabled_dates를 통해 주말/휴장일 선택 방지 ★
        sel_date = st.date_input("날짜 선택 (주말/휴장일 제외)", 
                                  value=default_date,
                                  min_value=min_date,
                                  max_value=max_date,
                                  disabled_dates=disabled_days,
                                  key="t1_date").strftime('%Y-%m-%d')
    with c_c:
        cats = ['전체 보기'] + list(df['Category'].unique())
        sel_cat = st.selectbox("카테고리 선택", cats)
    
    f_df = df[df['Category'] == sel_cat] if sel_cat != '전체 보기' else df
    d_data = f_df[sel_date]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("🎯 스윗스팟")
        for t in d_data[d_data == '스윗스팟'].index: st.write(f"- **{t}**")
    with col2:
        st.error("📈 단기상승")
        for t in d_data[d_data == '단기상승'].index: st.write(f"- {t}")
    with col3:
        st.info("📉 단기하락")
        for t in d_data[d_data == '단기하락'].index: st.write(f"- {t}")

# --- 탭 2: 종목별 ---
with tab2:
    st.subheader("🗓️ 종목별 향후 10일 흐름")
    m_col, s_col = st.columns(2)
    with m_col:
        m_cat = st.selectbox("대분류", df['Category'].unique(), key="t2_m")
    with s_col:
        s_ticker = st.selectbox("소분류", df[df['Category'] == m_cat].index, key="t2_s")
    
    st_date = st.date_input("시작일 선택", 
                             value=default_date,
                             min_value=min_date,
                             max_value=max_date,
                             disabled_dates=disabled_days,
                             key="t2_date").strftime('%Y-%m-%d')
    
    idx = available_dates_str.index(st_date)
    t_dates = available_dates_str[idx:idx+10]
    res = pd.DataFrame({"날짜": t_dates, "상태": df.loc[s_ticker, t_dates].values})
    st.dataframe(res.style.map(highlight_status, subset=['상태']), use_container_width=True, hide_index=True)

# --- 탭 3: 전체 현황 ---
with tab3:
    st.subheader("🌐 카테고리별 전체 현황")
    d3_col, c3_col = st.columns(2)
    with d3_col:
        st_date3 = st.date_input("시작일 선택", 
                                  value=default_date,
                                  min_value=min_date,
                                  max_value=max_date,
                                  disabled_dates=disabled_days,
                                  key="t3_date").strftime('%Y-%m-%d')
    with c3_col:
        sel_cat3 = st.selectbox("카테고리 선택", cats, key="t3_cat")
    
    idx3 = available_dates_str.index(st_date3)
    t_dates3 = available_dates_str[idx3:idx3+7]
    v_df = df[df['Category'] == sel_cat3].copy() if sel_cat3 != '전체 보기' else df.copy().sort_values('Category')
    st.dataframe(v_df[['Category'] + t_dates3].style.map(highlight_status), use_container_width=True)

