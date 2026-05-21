import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ตั้งค่าหน้าเว็บแอปพลิเคชันแบบ Wide Layout คลีนๆ สไตล์ห้องเทรดมืออาชีพ
st.set_page_config(
    page_title="AlphaTrader Premium - Multi-Timeframe Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🚨 ตกแต่ง UI ด้วย CSS สด ป้องกันการเกิด Syntax Error ด้วยการไม่ใช้ f-string 🚨
st.markdown("""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    </head>
    <style>
        /* จัดโครงสร้างสีพื้นหลังและฟอนต์หลักของแอป */
        html, body, [class*="css"], .stApp {
            background-color: #0b0f19 !important;
            color: #f8fafc !important;
            font-family: 'Inter', 'Prompt', sans-serif !important;
        }
        
        /* ปรับดีไซน์ของ Sidebar ให้มีความโมเดิร์น โทนสีลึกมีมิติ */
        section[data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #1f2937 !important;
        }
        
        /* แก้ไขช่องค้นหาตามคำขอ: พื้นหลังสีขาว ตัวอักษรขณะพิมพ์เป็นสีดำเข้มชัดเจน */
        div[data-testid="stTextInput"] input {
            color: #000000 !important; /* ตัวอักษรสีดำขณะพิมพ์ */
            font-weight: 600 !important;
            background-color: #ffffff !important;
            border: 2px solid #10b981 !important;
            border-radius: 8px !important;
        }
        
        /* ตกแต่งกล่องเลือกตัวเลือก (Selectbox) */
        div[data-baseweb="select"] {
            background-color: #1f2937 !important;
            border: 1px solid #374151 !important;
            border-radius: 10px !important;
        }
        
        /* ตกแต่งปุ่มหลักให้สวยงาม */
        .stButton>button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.1) !important;
        }
        .stButton>button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3) !important;
        }
        
        /* ปุ่มสไตล์อันตราย / ปุ่มลบรายการโปรด */
        .btn-danger button {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
            box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1) !important;
        }
        
        /* สไตล์พิเศษสำหรับปุ่มเลือกหุ้นลัดในแถบรายการโปรด */
        section[data-testid="stSidebar"] .stButton > button {
            background: #1f2937 !important;
            border: 1px solid #2d3748 !important;
            border-radius: 8px !important;
            text-align: left !important;
            color: #e5e7eb !important;
            margin-bottom: 6px !important;
            font-weight: 500 !important;
            padding: 8px 12px !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #374151 !important;
            border-color: #4b5563 !important;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# จัดการ State หุ้นและรายการโปรด (Watchlist) ให้จำค่าและใช้งานง่าย
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'META']
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = 'AAPL'

# เมนูข้าง (Sidebar) จัดกลุ่มฟังก์ชันเรียบง่าย สบายตา
with st.sidebar:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <span style="font-size: 24px;">🎯</span>
            <h2 style="font-size: 18px; font-weight: 700; color: #ffffff; display: inline-block; margin: 0 0 0 8px; vertical-align: middle;">
                AlphaTrader Pro
            </h2>
            <p style="font-size: 11px; color: #9ca3af; margin: 4px 0 0 0;">เครื่องมือเลือกหุ้นและวิเคราะห์แนวรับต้านทุกไทม์เฟรม</p>
        </div>
        <hr style="border-color: #1f2937; margin-bottom: 20px;">
    """, unsafe_allow_html=True)
    
    # ช่องค้นหาตัวย่อหุ้น (ตัวอักษรสีดำ พิมพ์ง่ายสบายตา)
    st.markdown("<label style='font-size: 13px; font-weight: 500; color: #9ca3af;'>🔍 ค้นหาชื่อหุ้นสหรัฐฯ (ตัวอักษรดำพื้นขาว)</label>", unsafe_allow_html=True)
    search_input = st.text_input("", value="", placeholder="เช่น AAPL, TSLA, NVDA", label_visibility="collapsed", key="stock_input")
    
    target_ticker = st.session_state.active_ticker
    if search_input:
        target_ticker = search_input.upper().strip()
        st.session_state.active_ticker = target_ticker

    # 📌 ปุ่มจัดการรายการโปรดแบบชัดเจน 2 ปุ่ม (เพิ่ม/ลบ)
    st.markdown("<div style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
    col_add, col_del = st.columns(2)
    with col_add:
        if st.button("➕ เพิ่มโปรด", use_container_width=True):
            if target_ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(target_ticker)
                st.toast(f"เพิ่ม {target_ticker} เข้าในรายการโปรดแล้ว! ⭐")
                st.rerun()
    with col_del:
        # ใช้ container ครอบเพื่อให้ CSS ตกแต่งเป็นสีแดงสไตล์ปุ่มอันตราย
        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
        if st.button("❌ ลบออก", use_container_width=True):
            if target_ticker in st.session_state.watchlist:
                st.session_state.watchlist.remove(target_ticker)
                st.toast(f"ลบ {target_ticker} ออกจากรายการโปรดแล้ว")
                st.session_state.active_ticker = 'AAPL' if not st.session_state.watchlist else st.session_state.watchlist[0]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='font-size: 13px; font-weight: 500; color: #9ca3af; margin-bottom: 8px;'>⭐️ รายการโปรดของคุณ</p>", unsafe_allow_html=True)
    
    # ปุ่มด่วนสำหรับเลือกหุ้นในรายการโปรด (กดทีเดียวสลับหน้าหุ้นทันที)
    for symbol in st.session_state.watchlist:
        btn_label = f"✨ {symbol} (กำลังเปิด)" if symbol == st.session_state.active_ticker else f"📁 {symbol}"
        if st.button(btn_label, key=f"sel_{symbol}", use_container_width=True):
            st.session_state.active_ticker = symbol
            st.rerun()

    st.markdown("<hr style='border-color: #1f2937; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # 📌 ส่วนเลือกไทม์เฟรมวิเคราะห์ราคา (Timeframe Selector) ครอบคลุมทุกความต้องการ
    st.markdown("<label style='font-size: 13px; font-weight: 500; color: #9ca3af;'>🕒 เลือกไทม์เฟรมวิเคราะห์ราคา (Timeframe)</label>", unsafe_allow_html=True)
    timeframe_choice = st.selectbox(
        "",
        options=[
            "15 นาที (15m)",
            "1 ชั่วโมง (1h)",
            "1 วัน (Daily)",
            "1 สัปดาห์ (Weekly)"
        ],
        index=2,
        label_visibility="collapsed"
    )

# กำหนดค่า Period และ Interval ให้สัมพันธ์กับไทม์เฟรมที่ผู้ใช้เลือกจริง
if timeframe_choice == "15 นาที (15m)":
    api_period = "5d"
    api_interval = "15m"
elif timeframe_choice == "1 ชั่วโมง (1h)":
    api_period = "1mo"
    api_interval = "60m"
elif timeframe_choice == "1 วัน (Daily)":
    api_period = "1y"
    api_interval = "1d"
else: # 1 สัปดาห์ (Weekly)
    api_period = "2y"
    api_interval = "1wk"

active_ticker = st.session_state.active_ticker

# หัวเว็บบาร์สไตล์พรีเมียมคลีน
st.markdown(f"""
    <div style="
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 12px;
        margin-bottom: 20px;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); padding: 8px 12px; border-radius: 8px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);">
                <span style="color: white; font-size: 18px; font-weight: bold;">📊</span>
            </div>
            <div>
                <h1 style="font-size: 18px; font-weight: 700; color: white; margin: 0; font-family: 'Prompt', sans-serif;">
                    AlphaTrader US Market Analyzer
                </h1>
                <p style="font-size: 11px; color: #9ca3af; margin: 0; font-family: 'Prompt', sans-serif;">วิเคราะห์ทิศทางและตีกราฟอัตโนมัติ | ไทม์เฟรมปัจจุบัน: {timeframe_choice}</p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 6px; background-color: rgba(16, 185, 129, 0.1); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.2);">
            <span style="height: 6px; width: 6px; border-radius: 50%; background-color: #10b981; display: inline-block;"></span>
            <span style="font-size: 10px; color: #10b981; font-weight: 600; font-family: 'Prompt';">เรียลไทม์เอนจินเปิดใช้งาน</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if active_ticker:
    try:
        # ดึงข้อมูลตามไทม์เฟรมที่ผู้ใช้ระบุย้อนหลังจริง
        stock_api = yf.Ticker(active_ticker)
        df = stock_api.history(period=api_period, interval=api_interval)
        
        if df.empty:
            st.error(f"⚠️ ไม่พบข้อมูลสัญลักษณ์หุ้น '{active_ticker}' บนระบบในช่วงเวลาหรือไทม์เฟรมที่เลือก กรุณาลองใหม่อีกครั้ง")
        else:
            company_name = stock_api.info.get('longName', f"{active_ticker} Inc.")
            
            # เคลียร์ค่าแถวข้อมูลที่มีค่าว่างให้พร้อมต่อการคำนวณสูตรเทคนิคัล
            df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
            
            # คำนวณอินดิเคเตอร์ทางเทคนิค (EMA20 & EMA50) สำหรับหาเทรนด์หลัก
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            
            # คำนวณสูตรดัชนีโมเมนตัม RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, np.nan)
            df['RSI'] = 100 - (100 / (1 + rs))
            df['RSI'] = df['RSI'].fillna(50)
            
            # ตรวจสอบจุดต่ำสุดและจุดสูงสุดในรอบข้อมูลปัจจุบันเพื่อใช้เป็นแนวรับ-แนวต้านหลัก
            resistance = df['High'].max()
            support = df['Low'].min()
            
            # ดึงราคาพิกัดล่าสุดเปรียบเทียบหาเปอร์เซ็นต์เปลี่ยนแปลง
            last_close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2] if len(df) > 1 else last_close
            price_change = last_close - prev_close
            pct_change = (price_change / prev_close) * 100 if prev_close != 0 else 0
            
            current_rsi = df['RSI'].iloc[-1]
            current_ema20 = df['EMA20'].iloc[-1]
            current_ema50 = df['EMA50'].iloc[-1]
            
            # ประเมินเกณฑ์เพื่อให้คะแนนจุดเข้าซื้อและจุดขายตามพฤติกรรมราคา
            score = 0
            alert_reasons = []
            
            dist_to_support = (last_close - support) / support if support != 0 else 0
            dist_to_resistance = (resistance - last_close) / last_close if last_close != 0 else 0
            
            if dist_to_support < 0.025:
                score += 3
                alert_reasons.append(f"ราคาลดลงมาใกล้แนวรับสำคัญที่ **${support:.2f}** (ห่างเพียง {dist_to_support*100:.1f}%) เริ่มยืนสร้างฐานได้มั่นคง ถือเป็นโอกาสเข้าสะสมที่ดี")
            elif dist_to_resistance < 0.025:
                score -= 3
                alert_reasons.append(f"ราคากำลังขึ้นไปชนแนวต้านเก่าที่ค่อนข้างหนาแน่นที่ **${resistance:.2f}** (ห่างเพียง {dist_to_resistance*100:.1f}%) ให้ระวังมีแรงขายล็อกกำไรระยะสั้น")
            else:
                alert_reasons.append(f"ราคาแกว่งตัวอยู่ในโซนปกติ ระหว่างฐานแนวรับ ${support:.2f} ถึงกรอบแนวต้านด้านบนที่ ${resistance:.2f}")
                
            if last_close > current_ema20 > current_ema50:
                score += 1.5
                alert_reasons.append("ราคายืนเหนือเส้นเฉลี่ยสะสมหลัก EMA20 และ EMA50 บ่งบอกทิศทางหลักเป็นขาขึ้นแข็งแกร่ง (Bullish Trend)")
            elif last_close < current_ema20 < current_ema50:
                score -= 1.5
                alert_reasons.append("ราคาหลุดต่ำกว่าเส้นเฉลี่ยสะสมหลักลงมา ทิศทางหลักอยู่ในช่วงชะลอตัวฝั่งขาลง (Bearish Trend) ควรรอยืนฐานได้ก่อน")
                
            if current_rsi < 30:
                score += 2.5
                alert_reasons.append(f"ดัชนีโมเมนตัม RSI บ่งบอกสภาวะแรงเทขายหนักเกินไป (Oversold ที่ {current_rsi:.1f}) มีลุ้นเกิดรอบรีบาวด์ดีดกลับเร็วๆ นี้")
            elif current_rsi > 70:
                score -= 2.5
                alert_reasons.append(f"ดัชนีโมเมนตัม RSI บ่งบอกสภาวะแรงซื้อหนาแน่นเกินไป (Overbought ที่ {current_rsi:.1f}) เสี่ยงโดนเททุบสลับรอบทำกำไร")

            # สรุปเกณฑ์ตัดสินใจสำหรับแผงคำแนะนำการลงทุนด่วน
            if score >= 2.0:
                verdict_status = "แนะนำ: ซื้อสะสม (BUY)"
                verdict_color = "#10b981"
                verdict_bg = "rgba(16, 185, 129, 0.08)"
                verdict_border = "#10b981"
                verdict_icon = "🟢"
            elif score <= -2.0:
                verdict_status = "แนะนำ: ลดพอร์ต/ขายทำกำไร (SELL)"
                verdict_color = "#ef4444"
                verdict_bg = "rgba(239, 68, 68, 0.08)"
                verdict_border = "#ef4444"
                verdict_icon = "🔴"
            else:
                verdict_status = "แนะนำ: ถือครองดูรอบราคา (HOLD)"
                verdict_color = "#f59e0b"
                verdict_bg = "rgba(245, 158, 11, 0.08)"
                verdict_border = "#f59e0b"
                verdict_icon = "⏳"

            # สร้างส่วนสรุปผลคำแนะนำระดับสายตา (Highlight Banner) ใหญ่ ชัดเจนที่สุด
            st.markdown(f"""
                <div style="
                    background: {verdict_bg};
                    border: 1px solid {verdict_border};
                    padding: 24px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 20px;
                ">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <span style="font-size: 32px;">{verdict_icon}</span>
                        <div>
                            <span style="font-size: 11px; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; font-weight: bold; display: block;">
                                ความคิดเห็นจากสูตรเทคนิคัลอัตโนมัติ (ไทม์เฟรม {timeframe_choice})
                            </span>
                            <h2 style="font-size: 20px; font-weight: 800; color: {verdict_color}; margin: 4px 0 0 0; font-family: 'Prompt';">
                                {verdict_status}
                            </h2>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 11px; color: #9ca3af; display: block;">วิเคราะห์สำหรับหุ้น</span>
                        <span style="font-size: 18px; font-weight: 700; color: #ffffff;">{active_ticker} ({company_name})</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # ตกแต่งสีสันกล่องรายงานตัวเลขสำคัญ
            price_change_color = "#10b981" if price_change >= 0 else "#ef4444"
            price_change_bg = "rgba(16, 185, 129, 0.1)" if price_change >= 0 else "rgba(239, 68, 68, 0.1)"
            
            # โซนสถานะความเสี่ยง RSI
            if current_rsi < 30:
                rsi_badge, rsi_badge_color, rsi_badge_bg = "โอกาสซื้อ (Oversold)", "#10b981", "rgba(16, 185, 129, 0.1)"
            elif current_rsi > 70:
                rsi_badge, rsi_badge_color, rsi_badge_bg = "ระวังขาย (Overbought)", "#ef4444", "rgba(239, 68, 68, 0.1)"
            else:
                rsi_badge, rsi_badge_color, rsi_badge_bg = "ปกติ (Neutral)", "#a855f7", "rgba(168, 85, 247, 0.1)"

            # การ์ดรายงานตัวเลขสำคัญ (Dashboard Cards Grid) ลอยเด่น ชัดเจน สไตล์โมเดิร์น
            st.markdown(f"""
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                    margin-bottom: 24px;
                ">
                    <!-- Price Card -->
                    <div style="background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 12px; font-family: 'Prompt';">
                        <span style="font-size: 11px; color: #9ca3af; display: block; margin-bottom: 4px;">ราคาซื้อขายล่าสุด</span>
                        <div style="display: flex; align-items: baseline; gap: 8px;">
                            <span style="font-size: 24px; font-weight: 800; color: white;">${last_close:.2f}</span>
                            <span style="font-size: 11px; font-weight: 600; color: {price_change_color}; background-color: {price_change_bg}; padding: 2px 6px; border-radius: 4px;">{pct_change:+.2f}%</span>
                        </div>
                    </div>
                    <!-- Support Card -->
                    <div style="background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 12px; font-family: 'Prompt';">
                        <span style="font-size: 11px; color: #9ca3af; display: block; margin-bottom: 4px;">🛡️ ขีดแนวรับสำคัญ</span>
                        <div>
                            <span style="font-size: 24px; font-weight: 800; color: #10b981;">${support:.2f}</span>
                        </div>
                    </div>
                    <!-- Resistance Card -->
                    <div style="background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 12px; font-family: 'Prompt';">
                        <span style="font-size: 11px; color: #9ca3af; display: block; margin-bottom: 4px;">🎯 ขีดแนวต้านสำคัญ</span>
                        <div>
                            <span style="font-size: 24px; font-weight: 800; color: #ef4444;">${resistance:.2f}</span>
                        </div>
                    </div>
                    <!-- RSI Card -->
                    <div style="background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 12px; display: flex; flex-direction: column; justify-content: space-between; font-family: 'Prompt';">
                        <span style="font-size: 11px; color: #9ca3af; display: block; margin-bottom: 4px;">📊 พลังแรงซื้อขาย RSI(14)</span>
                        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                            <span style="font-size: 24px; font-weight: 800; color: #a855f7;">{current_rsi:.1f}</span>
                            <span style="font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 6px; background-color: {rsi_badge_bg}; color: {rsi_badge_color};">{rsi_badge}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # กล่องสรุปวิเคราะห์ข้อมูลย่อยจากสมองกล AI เข้าใจง่ายที่สุด
            advice_list_html = "".join([f"<li style='margin-bottom: 8px; list-style-type: none; padding-left: 14px; position: relative;'><span style='position: absolute; left: 0; color: {verdict_color};'>•</span> {reason}</li>" for reason in alert_reasons])
            st.markdown(f"""
                <div style="
                    background-color: #111827;
                    border: 1px solid #1f2937;
                    padding: 20px;
                    border-radius: 12px;
                    margin-bottom: 24px;
                ">
                    <h4 style="font-weight: 700; color: #ffffff; font-size: 13px; margin: 0 0 10px 0; font-family: 'Prompt', sans-serif;">
                        💡 สรุปพฤติกรรมเทคนิคอลเพื่อประกอบการตัดสินใจ ({timeframe_choice})
                    </h4>
                    <ul style="font-size: 12px; color: #cbd5e1; line-height: 1.6; padding-left: 0; margin: 0; font-family: 'Prompt', sans-serif;">
                        {advice_list_html}
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            # โซนวาดกราฟเทคนิคัลระดับโปรที่ซูม-ลากดูราคาได้ (Plotly Interactive Chart)
            st.markdown("<h3 style='font-size: 14px; font-weight: 700; color: white; margin-bottom: 12px; font-family: \"Prompt\";'>📉 กราฟราคาสดแท่งเทียน & ดัชนีโมเมนตัม</h3>", unsafe_allow_html=True)
            
            # คัดลอกตารางข้อมูลสำหรับนำไปเขียนกราฟ
            df_chart = df.copy()
            
            # กำหนดจุดปักหมุดสัญญาณ BUY และ SELL บนชาร์ตแท่งเทียนให้ดูง่าย
            df_chart['Buy_Marker'] = np.nan
            df_chart['Sell_Marker'] = np.nan
            df_chart.loc[df_chart['RSI'] < 33, 'Buy_Marker'] = df_chart['Low'] * 0.985
            df_chart.loc[df_chart['RSI'] > 67, 'Sell_Marker'] = df_chart['High'] * 1.015

            # สร้าง Subplots สำหรับแยก 2 แผงกราฟ (บน: ราคากลุ่มแท่งเทียน, ล่าง: แถบดัชนี RSI)
            fig = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.08, 
                row_heights=[0.72, 0.28]
            )

            # กราฟด้านบน: แท่งเทียน (Candlesticks) โทนสีเขียวแดงคมชัดลึก
            fig.add_trace(go.Candlestick(
                x=df_chart.index,
                open=df_chart['Open'],
                high=df_chart['High'],
                low=df_chart['Low'],
                close=df_chart['Close'],
                name="ราคา",
                increasing_line_color='#10b981', 
                decreasing_line_color='#ef4444',
                increasing_fillcolor='#10b981',
                decreasing_fillcolor='#ef4444'
            ), row=1, col=1)

            # เพิ่มเส้นเฉลี่ยความเร็วแนวโน้มระยะสั้น EMA20
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['EMA20'],
                line=dict(color='#3b82f6', width=1.8),
                name='แนวโน้มระยะสั้น (EMA 20)'
            ), row=1, col=1)
            
            # เพิ่มเส้นเฉลี่ยความเร็วแนวโน้มระยะกลาง EMA50
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['EMA50'],
                line=dict(color='#f43f5e', width=1.8),
                name='แนวโน้มระยะกลาง (EMA 50)'
            ), row=1, col=1)

            # ตีเส้นประแนวต้านและแนวรับของพฤติกรรมรอบราคาปัจจุบัน
            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], 
                y=[resistance, resistance],
                mode="lines",
                line=dict(color="#ef4444", width=1.5, dash="dash"),
                name="เส้นสังเกตการณ์: แนวต้าน"
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], 
                y=[support, support],
                mode="lines",
                line=dict(color="#10b981", width=1.5, dash="dash"),
                name="เส้นสังเกตการณ์: แนวรับ"
            ), row=1, col=1)

            # ใส่สัญลักษณ์ลูกศรปักหมุดชี้ช่องสัญญานซื้อสะสม (BUY) และสัญญานสกัดขาย (SELL) ชัดเจนสวยงาม
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Buy_Marker'],
                mode='markers',
                marker=dict(symbol='triangle-up', size=13, color='#10b981', line=dict(width=1.2, color='white')),
                name='จุดลุ้นเข้าสะสม (BUY)'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Sell_Marker'],
                mode='markers',
                marker=dict(symbol='triangle-down', size=13, color='#ef4444', line=dict(width=1.2, color='white')),
                name='จุดพึงระวังแรงขาย (SELL)'
            ), row=1, col=1)

            # กราฟด้านล่าง: แผงโมเมนตัมวัดปริมาณการซื้อขายมากเกินไป/น้อยเกินไป (RSI Panel)
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['RSI'],
                line=dict(color='#a855f7', width=2),
                name='ระดับโมเมนตัม RSI'
            ), row=2, col=1)

            # ปรับแต่งสภาพแวดล้อมรวมถึงสีกราฟทั้งหมดให้ออกแนวโมเดิร์นดาร์กสเปซกลมกลืนกับหน้าเว็บ
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                paper_bgcolor='#0b0f19',
                plot_bgcolor='#0b0f19',
                font=dict(color='#9ca3af', family='Inter, Prompt', size=10),
                height=580,
                margin=dict(l=40, r=40, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)')
            )
            
            # ตกแต่งเส้นพิกัดตารางแผนผัง
            fig.update_xaxes(showgrid=True, gridcolor='#1f2937', linecolor='#374151')
            fig.update_yaxes(title_text="ระดับราคา ($)", showgrid=True, gridcolor='#1f2937', linecolor='#374151', row=1, col=1)
            fig.update_yaxes(title_text="ระดับ RSI", range=[10, 90], showgrid=True, gridcolor='#1f2937', linecolor='#374151', row=2, col=1)
            
            # มาร์กเกอร์เส้นมาตรฐานขีด 70 (Overbought) และขีด 30 (Oversold)
            fig.add_shape(type="line", x0=df_chart.index[0], x1=df_chart.index[-1], y0=70, y1=70, line=dict(color="#ef4444", width=1, dash="dot"), row=2, col=1)
            fig.add_shape(type="line", x0=df_chart.index[0], x1=df_chart.index[-1], y0=30, y1=30, line=dict(color="#10b981", width=1, dash="dot"), row=2, col=1)

            st.plotly_chart(fig, use_container_width=True)

            # แผงตารางขยายดูรายงานราคาย้อนหลังรายแถวข้อมูลจริง
            with st.expander("📝 เปิดดูตารางวิเคราะห์สถิติตัวเลขย้อนหลังเพิ่มเติม"):
                df_show = df_chart[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'EMA20']].sort_index(ascending=False)
                st.dataframe(df_show, use_container_width=True)

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูลหรือจัดระดับวิเคราะห์: {e}")
