import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------------------------
# ⚙️ 1. 기본 설정 및 카테고리 분류 함수
# ------------------------------------------------
# 타이틀과 이모지를 수정구슬(🔮)로 변경했습니다.
st.set_page_config(page_title="2026년 운명의 수정구슬", page_icon="🔮", layout="wide")

def get_category(ticker):
    markets = ['Australia', 'Brazil', 'Canada', 'China', 'Dow Jones Islamic Market Titans', 'Dow Jones Transports', 'Dow Jones Utilities', 'France', 'Germany', 'Great Britain', 'Hong Kong', 'India', 'Israel', 'Italy', 'Japan', 'Korea', 'Nasdaq', 'Russia', 'S&P 500 E-minis']
    bonds = ['10 Year Bond Yield 1994-', 'Fed Funds 1990-', '10 Year Treasury Notes', '30 Year Treasury Bonds']
    currencies = ['Australian Dollar', 'British Pound', 'Canadian Dollar', 'US Dollar Index', 'Euro Currency', 'Japanese Yen', 'Mexican Peso', 'New Zealand Dollar', 'Swiss Franc']
    crypto_etf = ['GBTC', 'URA', 'QQQ', 'USRT', 'FNGU']
    commodities = ['Copper', 'Gold', 'Palladium', 'Platinum', 'Silver', 'Cocoa', 'Coffee', 'Cotton', 'Lumber', 'Orange Juice', 'Sugar', 'Crude Oil Long-Term Cycle', 'Crude Oil', 'Heating Oil', 'Natural Gas', 'RBOB Unleaded', 'Feeder Cattle', 'Live Cattle', 'Lean Hogs', 'Corn', 'Oats', 'Soybeans', 'Soybean Meal', 'Soybean Oil', 'Wheat', 'Dow Jones Commodity Index', 'Goldman Sachs Commodity Index']
    
    if ticker in markets: return '🌎 국가 및 지수'
    elif ticker in bonds: return '🏦 금리 및 채권'
    elif ticker in currencies: return '💱 환율'
    elif ticker in crypto_etf: return '🪙 암호화폐 및 ETF'
    elif ticker in commodities: return '🛢️ 원자재'
    else: return '📈 개별 주식'

@st.cache_data
def load_data():
    df = pd.read_csv('2026forcast.csv', index_col=0)
    df['Category'] = df.index.map(get_category)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("📂 '2026forcast.csv' 파일을 찾을 수 없습니다.")
    st.stop()

available_dates = [col for col in df.columns if col != 'Category']
today_str = datetime.now().strftime('%Y-%m-%d')
future_dates = [d for d in available_dates if d >= today_str]
default_date_str = future_dates[0] if future_dates else available_dates[-1]
default_date_obj = datetime.strptime(default_date_str, '%Y-%m-%d').date()

# 메인 타이틀 변경
st.markdown("<h1 style='font-size: clamp(28px, 7vw, 40px);'>🔮 2026년 운명의 수정구슬</h1>", unsafe_allow_html=True)
st.write("---")

def highlight_status(val):
    if val == '스윗스팟':
        return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == '단기상승':
        return 'background-color: #f8d7da; color: #721c24;'
    elif val == '단기하락':
        return 'background-color: #cce5ff; color: #004085;'
    return ''

# ------------------------------------------------
# 🗂️ 2. 화면 탭 구성
# ------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📅 날짜별 모아보기", "🔍 종목별 흐름보기", "🌐 전체 종목 한눈에 보기"])

# ==========================================
# 탭 1: 날짜별 모아보기
# ==========================================
with tab1:
    st.subheader("💡 특정 날짜의 상태별 종목 현황")
    
    col_date, col_cat = st.columns(2)
    with col_date:
        selected_date_obj = st.date_input("조회할 개장일을 선택하세요", default_date_obj, key="tab1_date")
        selected_date = selected_date_obj.strftime('%Y-%m-%d')
    with col_cat:
        categories = ['전체 보기'] + list(df['Category'].unique())
        selected_cat1 = st.selectbox("대분류를 선택하세요", categories)
    
    if selected_date not in available_dates:
        st.warning(f"{selected_date}은(는) 개장일 데이터가 없습니다.")
    else:
        if selected_cat1 != '전체 보기':
            filtered_df = df[df['Category'] == selected_cat1]
        else:
            filtered_df = df
            
        day_data = filtered_df[selected_date]
        
        sweet_spots = day_data[day_data == '스윗스팟'].index.tolist()
        uptrends = day_data[day_data == '단기상승'].index.tolist()
        downtrends = day_data[day_data == '단기하락'].index.tolist()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success(f"🎯 스윗스팟 ({len(sweet_spots)})")
            for ticker in sweet_spots: st.write(f"- **{ticker}**")
        with col2:
            st.error(f"📈 단기상승 ({len(uptrends)})")
            for ticker in uptrends: st.write(f"- {ticker}")
        with col3:
            st.info(f"📉 단기하락 ({len(downtrends)})")
            for ticker in downtrends: st.write(f"- {ticker}")

# ==========================================
# 탭 2: 종목별 흐름보기
# ==========================================
with tab2:
    st.subheader("🗓️ 특정 종목의 향후 2주 흐름")
    
    col_main, col_sub = st.columns(2)
    with col_main:
        selected_main_cat = st.selectbox("1단계: 대분류 선택", df['Category'].unique())
    with col_sub:
        sub_tickers = df[df['Category'] == selected_main_cat].index.tolist()
        selected_ticker = st.selectbox("2단계: 종목 선택", sub_tickers)
        
    start_date_obj2 = st.date_input("시작일을 선택하세요", default_date_obj, key="tab2_date")
    start_date2 = start_date_obj2.strftime('%Y-%m-%d')
    
    if start_date2 in available_dates:
        start_idx = available_dates.index(start_date2)
        end_idx = min(start_idx + 10, len(available_dates))
        target_dates = available_dates[start_idx:end_idx]
        
        ticker_data = df.loc[selected_ticker, target_dates]
        trend_df = pd.DataFrame({"날짜": target_dates, "상태": ticker_data.values})
        
        st.dataframe(trend_df.style.map(highlight_status, subset=['상태']), use_container_width=True, hide_index=True)
    else:
        st.warning("선택하신 날짜의 데이터가 없습니다.")

# ==========================================
# 탭 3: 전체 종목 한눈에 보기
# ==========================================
with tab3:
    st.subheader("🌐 전체 종목 향후 7일치 흐름 한눈에 보기")
    
    col_date3, col_cat3 = st.columns(2)
    with col_date3:
        start_date_obj3 = st.date_input("시작일을 선택하세요", default_date_obj, key="tab3_date")
        start_date3 = start_date_obj3.strftime('%Y-%m-%d')
    with col_cat3:
        selected_cat3 = st.selectbox("조회할 대분류를 선택하세요", categories, key="tab3_cat")
    
    if start_date3 in available_dates:
        start_idx = available_dates.index(start_date3)
        end_idx = min(start_idx + 7, len(available_dates))
        target_dates = available_dates[start_idx:end_idx]
        
        if selected_cat3 != '전체 보기':
            view_df = df[df['Category'] == selected_cat3].copy()
        else:
            view_df = df.copy()
            view_df = view_df.sort_values(by=['Category'])
            
        columns_to_show = ['Category'] + target_dates
        all_trend_df = view_df[columns_to_show]
        
        st.dataframe(all_trend_df.style.map(highlight_status), use_container_width=True)
        st.caption("💡 표 안에서 스크롤하거나 우측 상단의 '전체화면' 아이콘을 누르면 크게 볼 수 있습니다.")
    else:
        st.warning("선택하신 날짜의 데이터가 없습니다.")



