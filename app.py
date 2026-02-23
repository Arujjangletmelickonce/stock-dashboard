import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# ------------------------------------------------
# ⚙️ 1. 페이지 설정 및 UI 정리 (메뉴 숨기기)
# ------------------------------------------------
st.set_page_config(page_title="2026년 운명의 수정구슬", page_icon="🔮", layout="wide")

# 우측 상단 메뉴와 하단 툴바 등을 숨겨 깔끔한 화면을 유지합니다.
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none !important;}
    /* 모바일에서 표가 잘 보이도록 너비 조정 */
    .stDataFrame {width: 100%;}
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------
# 📥 2. 데이터 로드 및 날짜 제어 로직
# ------------------------------------------------
@st.cache_data(ttl=600)  # 10분마다 구글 시트에서 최신 데이터를 가져옵니다.
def load_data():
    try:
        # Streamlit Cloud의 Secrets에 등록된 gs_url을 사용합니다.
        sheet_url = st.secrets["gs_url"]
        df = pd.read_csv(sheet_url, index_col=0)
    except Exception as e:
        st.error(f"❌ 데이터를 불러올 수 없습니다. 구글 시트 연결을 확인하세요: {e}")
        st.stop()
    
    # 종목별 카테고리 분류 함수
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

# --- 🗓️ 날짜 계산 (주말 및 휴장일 비활성화용) ---
available_dates_str = [col for col in df.columns if col != 'Category']
available_dates_obj = [datetime.strptime(d, '%Y-%m-%d').date() for d in available_dates_str]

min_date = available_dates_obj[0]
max_date = available_dates_obj[-1]

# 전체 범위 중 데이터가 없는 날(주말/휴장일)을 찾아 비활성화 리스트 생성
all_days = [min_date + timedelta(days=x) for x in range((max_date - min_date).days + 1)]
disabled_days = [d for d in all_days if d not in available_dates_obj]

# 오늘 날짜를 기본값으로 하되, 데이터가 없으면 첫 번째 날짜 선택
today = date.today()
default_date = today if today in available_dates_obj else available_dates_obj[0]

# ------------------------------------------------
# 🎨 3. 메인 화면 구성
# ------------------------------------------------
# 반응형 타이틀
st.markdown("<h1 style='font-size: clamp(28px, 7vw, 40px); text-align: center;'>🔮 2026년 운명의 수정구슬</h1>", unsafe_allow_html=True)
st.write("---")

# 상태별 색상 강조 함수
def highlight_status(val):
    if val == '스윗스팟': return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == '단기상승': return 'background-color: #f8d7da; color: #721c24;'
    elif val == '단기하락': return 'background-color: #cce5ff; color: #004085;'
    return ''

# 세 개의 탭 구성
tab1, tab2, tab3 = st.tabs(["📅 날짜별 모아보기", "🔍 종목별 흐름보기", "🌐 전체 종목 현황"])

# --- 탭 1: 날짜별 모아보기 ---
with tab1:
    st.subheader("💡 오늘의 상태별 종목 현황")
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        # 데이터가 있는 날만 선택 가능하게 설정
        sel_date = st.date_input("조회할 날짜를 선택하세요", 
                                  value=default_date,
                                  min_value=min_date,
                                  max_value=max_date,
                                  disabled_dates=disabled_days,
                                  key="t1_date").strftime('%Y-%m-%d')
    with col1_2:
        categories = ['전체 보기'] + list(df['Category'].unique())
        sel_cat = st.selectbox("조회할 카테고리를 선택하세요", categories, key="t1_cat")
    
    f_df = df[df['Category'] == sel_cat] if sel_cat != '전체 보기' else df
    day_data = f_df[sel_date]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("🎯 스윗스팟")
        for t in day_data[day_data == '스윗스팟'].index: st.write(f"- **{t}**")
    with c2:
        st.error("📈 단기상승")
        for t in day_data[day_data == '단기상승'].index: st.write(f"- {t}")
    with c3:
        st.info("📉 단기하락")
        for t in day_data[day_data == '단기하락'].index: st.write(f"- {t}")

# --- 탭 2: 종목별 흐름보기 ---
with tab2:
    st.subheader("🗓️ 특정 종목의 향후 10일 흐름")
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        sel_m_cat = st.selectbox("1단계: 대분류 선택", df['Category'].unique(), key="t2_main")
    with col2_2:
        sub_tickers = df[df['Category'] == sel_m_cat].index.tolist()
        sel_ticker = st.selectbox("2단계: 종목 선택", sub_tickers, key="t2_sub")
    
    st_date2 = st.date_input("시작일 선택", 
                              value=default_date,
                              min_value=min_date,
                              max_value=max_date,
                              disabled_dates=disabled_days,
                              key="t2_start").strftime('%Y-%m-%d')
    
    # 선택한 날짜부터 향후 10개 거래일 데이터 추출
    curr_idx = available_dates_str.index(st_date2)
    end_idx = min(curr_idx + 10, len(available_dates_str))
    target_dates = available_dates_str[curr_idx:end_idx]
    
    ticker_data = df.loc[sel_ticker, target_dates]
    res_df = pd.DataFrame({"날짜": target_dates, "상태": ticker_data.values})
    st.dataframe(res_df.style.map(highlight_status, subset=['상태']), use_container_width=True, hide_index=True)

# --- 탭 3: 전체 종목 현황 ---
with tab3:
    st.subheader("🌐 전체 종목 향후 7일치 흐름")
    col3_1, col3_2 = st.columns(2)
    with col3_1:
        st_date3 = st.date_input("시작일 선택", 
                                  value=default_date,
                                  min_value=min_date,
                                  max_value=max_date,
                                  disabled_dates=disabled_days,
                                  key="t3_start").strftime('%Y-%m-%d')
    with col3_2:
        sel_cat3 = st.selectbox("카테고리 필터", categories, key="t3_cat")
    
    curr_idx3 = available_dates_str.index(st_date3)
    end_idx3 = min(curr_idx3 + 7, len(available_dates_str))
    target_dates3 = available_dates_str[curr_idx3:end_idx3]
    
    v_df = df[df['Category'] == sel_cat3].copy() if sel_cat3 != '전체 보기' else df.copy().sort_values('Category')
    # 카테고리 열을 포함하여 표 표시
    st.dataframe(v_df[['Category'] + target_dates3].style.map(highlight_status), use_container_width=True)
