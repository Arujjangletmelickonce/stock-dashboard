import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------------------------
# ⚙️ 1. 기본 설정 및 카테고리 분류 함수
# ------------------------------------------------
st.set_page_config(page_title="2026 자산 사이클 대시보드", page_icon="📊", layout="wide")

# 자산 이름(티커)을 보고 대분류를 짝지어주는 함수
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

@st.cache_data
def load_data():
    df = pd.read_csv('2026forcast.csv', index_col=0)
    # 데이터프레임에 'Category(대분류)' 파생 변수 추가
    df['Category'] = df.index.map(get_category)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("📂 '2026forcast.csv' 파일을 찾을 수 없습니다.")
    st.stop()

# 날짜 데이터 처리 (Category 열 제외하고 날짜만 추출)
available_dates = [col for col in df.columns if col != 'Category']
today_str = datetime.now().strftime('%Y-%m-%d')
future_dates = [d for d in available_dates if d >= today_str]
default_date_str = future_dates[0] if future_dates else available_dates[-1]
default_date_obj = datetime.strptime(default_date_str, '%Y-%m-%d').date()

st.title("📊 2026 자산 사이클 대시보드")
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
# 탭 1: 날짜별 + 대분류 필터 모아보기
# ==========================================
with tab1:
    st.subheader("💡 특정 날짜의 상태별 종목 현황")
    
    col_date, col_cat = st.columns(2)
    with col_date:
        selected_date_obj = st.date_input("조회할 개장일을 선택하세요", default_date_obj, key="tab1_date")
        selected_date = selected_date_obj.strftime('%Y-%m-%d')
    with col_cat:
        # 카테고리 필터 추가 (전체 보기 포함)
        categories = ['전체 보기'] + list(df['Category'].unique())
        selected_cat1 = st.selectbox("대분류를 선택하세요", categories)
    
    if selected_date not in available_dates:
        st.warning(f"{selected_date}은(는) 개장일 데이터가 없습니다.")
    else:
        # 선택한 카테고리에 맞춰 데이터 필터링
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
# 탭 2: 대분류 -> 소분류 2단계 선택 방식
# ==========================================
with tab2:
    st.subheader("🗓️ 특정 종목의 향후 2주 흐름")
    
    col_main, col_sub = st.columns(2)
    with col_main:
        # 1단계: 대분류 선택
        selected_main_cat = st.selectbox("1단계: 대분류 선택", df['Category'].unique())
    with col_sub:
        # 2단계: 대분류에 속한 종목들만 모아서 소분류 선택
        sub_tickers = df[df['Category'] == selected_main_cat].index.tolist()
        selected_ticker = st.selectbox("2단계: 종목 선택", sub_tickers)
        
    start_date_obj2 = st.date_input("시작일을 선택하세요", default_date_obj, key="tab2_date")
    start_date2 = start_date_obj2.strftime('%Y-%m-%d')
    
    if start_date2 in available_dates:
        start_idx = available_dates.index(start_date2)
        end_idx = min(start_idx + 10, len(available_dates)) # 향후 10일치
        target_dates = available_dates[start_idx:end_idx]
        
        ticker_data = df.loc[selected_ticker, target_dates]
        trend_df = pd.DataFrame({"날짜": target_dates, "상태": ticker_data.values})
        
        st.dataframe(trend_df.style.map(highlight_status, subset=['상태']), use_container_width=True, hide_index=True)
    else:
        st.warning("선택하신 날짜의 데이터가 없습니다.")

# ==========================================
# 탭 3: 전체 종목 (카테고리별로 정렬하여 보기)
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
        
        # 카테고리 필터링 적용
        if selected_cat3 != '전체 보기':
            view_df = df[df['Category'] == selected_cat3].copy()
        else:
            view_df = df.copy()
            # 전체 보기일 경우, 카테고리별로 묶어서 정렬
            view_df = view_df.sort_values(by=['Category'])
            
        # 표에 보여줄 열만 선택 ('Category' 열 포함하여 보여주면 좋음)
        columns_to_show = ['Category'] + target_dates
        all_trend_df = view_df[columns_to_show]
        
        st.dataframe(all_trend_df.style.map(highlight_status), use_container_width=True)
        st.caption("💡 표 안에서 스크롤하거나 우측 상단의 '전체화면' 아이콘을 누르면 크게 볼 수 있습니다.")
    else:
        st.warning("선택하신 날짜의 데이터가 없습니다.")