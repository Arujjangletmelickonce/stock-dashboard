import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------------------------
# ⚙️ 1. 페이지 설정 및 보안 강화 (메뉴 숨기기)
# ------------------------------------------------
st.set_page_config(page_title="2026년 운명의 수정구슬", page_icon="🔮", layout="wide")

# 우측 상단 메뉴, 푸터, 헤더를 숨겨서 일반 사용자가 소스 코드나 깃허브로 접근하는 것을 방지합니다.
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* 모바일에서 테이블이 잘 보이지 않을 경우 대비한 스타일 */
    .stDataFrame {width: 100%;}
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------
# 🔒 2. 보안: 비밀번호 잠금 기능
# ------------------------------------------------
def check_password():
    def password_entered():
        # 🔑 원하는 비밀번호로 수정하세요 (예: "2026")
        if st.session_state["password"] == "1234":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔒 접근 제한 구역</h2>", unsafe_allow_html=True)
        st.text_input("🔑 비밀번호를 입력하세요:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center;'>🔒 접근 제한 구역</h2>", unsafe_allow_html=True)
        st.text_input("🔑 비밀번호를 입력하세요:", type="password", on_change=password_entered, key="password")
        st.error("🚫 비밀번호가 틀렸습니다. 다시 시도해 주세요.")
        return False
    return True

# 비밀번호 통과 못하면 중단
if not check_password():
    st.stop()

# ------------------------------------------------
# 📥 3. 데이터 로딩 및 분류 시스템
# ------------------------------------------------
@st.cache_data(ttl=600)  # 10분마다 구글 시트에서 새 데이터를 가져옴
def load_data():
    try:
        # Streamlit Cloud의 Settings -> Secrets에 등록한 주소를 가져옵니다.
        sheet_url = st.secrets["gs_url"]
        df = pd.read_csv(sheet_url, index_col=0)
    except Exception as e:
        st.error(f"❌ 데이터를 불러올 수 없습니다. Secrets 설정을 확인하세요: {e}")
        st.stop()
    
    # 카테고리 분류 로직
    def get_category(ticker):
        markets = ['Australia', 'Brazil', 'Canada', 'China', 'Dow Jones Islamic Market Titans', 'Dow Jones Transports', 'Dow Jones Utilities', 'France', 'Germany', 'Great Britain', 'Hong Kong', 'India', 'Israel', 'Italy', 'Japan', 'Korea', 'Nasdaq', 'Russia', 'S&P 500 E-minis']
        bonds = ['10 Year Bond Yield 1994-', 'Fed Funds 1990-', '10 Year Treasury Notes', '30 Year Treasury Bonds']
        currencies = ['Australian Dollar', 'British Pound', 'Canadian Dollar', 'US Dollar Index', 'Euro Currency', 'Japanese Yen', 'Mexican Peso', 'New Zealand Dollar', 'Swiss Franc']
        crypto_etf = ['GBTC', 'QQQ', 'USRT', 'FNGU']
        commodities = ['Copper', 'Gold', 'Palladium', 'Platinum', 'Silver', 'URA', 'Cocoa', 'Coffee', 'Cotton', 'Lumber', 'Orange Juice', 'Sugar', 'Crude Oil Long-Term Cycle', 'Crude Oil', 'Heating Oil', 'Natural Gas', 'RBOB Unleaded', 'Feeder Cattle', 'Live Cattle', 'Lean Hogs', 'Corn', 'Oats', 'Soybeans', 'Soybean Meal', 'Soybean Oil', 'Wheat', 'Dow Jones Commodity Index', 'Goldman Sachs Commodity Index']
        
        if ticker in markets: return '🌎 국가 및 지수'
        elif ticker in bonds: return '🏦 금리 및 채권'
        elif ticker in currencies: return '💱 환율'
        elif ticker in crypto_etf: return '🪙 암호화폐 및 ETF'
        elif ticker in commodities: return '🛢️ 원자재'
        else: return '📈 개별 주식'

    df['Category'] = df.index.map(get_category)
    return df

df = load_data()

# 날짜 추출 (Category 열 제외)
available_dates = [col for col in df.columns if col != 'Category']
today_str = datetime.now().strftime('%Y-%m-%d')
future_dates = [d for d in available_dates if d >= today_str]
default_date_str = future_dates[0] if future_dates else available_dates[-1]
default_date_obj = datetime.strptime(default_date_str, '%Y-%m-%d').date()

# ------------------------------------------------
# 🎨 4. 메인 화면 구성
# ------------------------------------------------
# 반응형 타이틀
st.markdown("<h1 style='font-size: clamp(28px, 7vw, 40px); text-align: center;'>🔮 2026년 운명의 수정구슬</h1>", unsafe_allow_html=True)
st.write("---")

def highlight_status(val):
    if val == '스윗스팟':
        return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == '단기상승':
        return 'background-color: #f8d7da; color: #721c24;'
    elif val == '단기하락':
        return 'background-color: #cce5ff; color: #004085;'
    return ''

tab1, tab2, tab3 = st.tabs(["📅 날짜별 모아보기", "🔍 종목별 흐름보기", "🌐 전체 종목 현황"])

# --- 탭 1: 날짜별 모아보기 ---
with tab1:
    st.subheader("💡 오늘의 상태별 종목")
    col_d, col_c = st.columns(2)
    with col_d:
        sel_date = st.date_input("날짜 선택", default_date_obj, key="t1_d").strftime('%Y-%m-%d')
    with col_c:
        cats = ['전체 보기'] + list(df['Category'].unique())
        sel_cat = st.selectbox("카테고리 선택", cats, key="t1_c")
    
    if sel_date in available_dates:
        f_df = df[df['Category'] == sel_cat] if sel_cat != '전체 보기' else df
        d_data = f_df[sel_date]
        
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
    else:
        st.warning("데이터가 없는 날짜입니다.")

# --- 탭 2: 종목별 흐름보기 ---
with tab2:
    st.subheader("🗓️ 종목별 향후 10일 흐름")
    m_col, s_col = st.columns(2)
    with m_col:
        m_cat = st.selectbox("대분류", df['Category'].unique(), key="t2_m")
    with s_col:
        s_ticker = st.selectbox("소분류", df[df['Category'] == m_cat].index, key="t2_s")
    
    st_date = st.date_input("시작일", default_date_obj, key="t2_date").strftime('%Y-%m-%d')
    if st_date in available_dates:
        idx = available_dates.index(st_date)
        t_dates = available_dates[idx:idx+10]
        res = pd.DataFrame({"날짜": t_dates, "상태": df.loc[s_ticker, t_dates].values})
        st.dataframe(res.style.map(highlight_status, subset=['상태']), use_container_width=True, hide_index=True)

# --- 탭 3: 전체 종목 현황 ---
with tab3:
    st.subheader("🌐 카테고리별 전체 현황")
    d3_col, c3_col = st.columns(2)
    with d3_col:
        st_date3 = st.date_input("시작일", default_date_obj, key="t3_date").strftime('%Y-%m-%d')
    with c3_col:
        sel_cat3 = st.selectbox("카테고리", cats, key="t3_cat")
    
    if st_date3 in available_dates:
        idx3 = available_dates.index(st_date3)
        t_dates3 = available_dates[idx3:idx3+7]
        v_df = df[df['Category'] == sel_cat3].copy() if sel_cat3 != '전체 보기' else df.copy().sort_values('Category')
        st.dataframe(v_df[['Category'] + t_dates3].style.map(highlight_status), use_container_width=True)
