import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# 1. ตั้งค่าโครงสร้างเว็บแอปพลิเคชันแบบ Wide Layout คลีนๆ
st.set_page_config(
    page_title="AlphaTrader Premium - Easy Technical Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ปรับแต่ง UI ด้วยดีไซน์หรูหรา ใช้งานง่าย สบายตา สไตล์โมเดิร์นดาร์กธีม
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
        
        /* ตกแต่งกล่องกรอกข้อความ (Input fields) */
        div[data-baseweb="input"] {
            background-color: #1f2937 !important;
            border: 1px solid #374151 !important;
            border-radius: 10px !important;
        }
        input {
            color: #ffffff !important;
            font-weight: 500 !important;
        }
        
        /* ตกแต่งกล่องเลือกตัวเลือก (Selectbox) */
        div[data-baseweb="select"] {
            background-color: #1f2937 !important;
            border: 1px solid #374151 !important;
            border-radius: 10px !important;
        }
        
        /* ตกแต่งปุ่มหลักให้สวยงาม กดง่าย มีปฏิกิริยาโต้ตอบ (Hover Effect) */
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

# 3. จัดการ State หุ้นและรายการโปรด (Watchlist) ให้จำค่าและใช้งานง่าย
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'META']
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = 'AAPL'

# 4. เมนูข้าง (Sidebar) จัดกลุ่มฟังก์ชันเรียบง่าย สบายตา ไม่รกตา
with st.sidebar:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <span style="font-size: 24px;">🎯</span>
            <h2 style="font-size: 18px; font-weight: 700; color: #ffffff; display: inline-block; margin: 0 0 0 8px; vertical-align: middle;">
                AlphaTrader Lite
            </h2>
            <p style="font-size: 11px; color: #9ca3af; margin: 4px 0 0 0;">เครื่องมือเลือกหุ้นและวิเคราะห์แนวรับต้าน</p>
        </div>
        <hr style="border-color: #1f2937; margin-bottom: 20px;">
    """, unsafe_allow_html=True)
    
    # ช่องค้นหาตัวย่อหุ้น
    st.markdown("<label style='font-size: 13px; font-weight: 500; color: #9ca3af;'>🔍 ค้นหาชื่อหุ้นสหรัฐฯ</label>", unsafe_allow_html=True)
    search_input = st.text_input("", value="", placeholder="เช่น AAPL, TSLA, NVDA", label_visibility="collapsed", key="stock_input")
    
    # ปุ่มควบคุมอัจฉริยะแบบปุ่มเดียว (Smart Button)
    if search_input:
        target_ticker = search_input.upper().strip()
        # ตรวจสอบว่าหุ้นตัวนี้อยู่ในรายการโปรดแล้วหรือยัง
        if target_ticker in st.session_state.watchlist:
            if st.button(f"❌ ลบ {target_ticker} ออกจากโปรด", use_container_width=True):
                st.session_state.watchlist.remove(target_ticker)
                st.session_state.active_ticker = 'AAPL' if not st.session_state.watchlist else st.session_state.watchlist[0]
                st.rerun()
        else:
            if st.button(f"➕ เพิ่ม {target_ticker} เข้าในโปรด", use_container_width=True):
                st.session_state.watchlist.append(target_ticker)
                st.session_state.active_ticker = target_ticker
                st.rerun()

    st.markdown("<br><p style='font-size: 13px; font-weight: 500; color: #9ca3af; margin-bottom: 8px;'>⭐️ รายการโปรดของคุณ</p>", unsafe_allow_html=True)
    
    # ปุ่มด่วนสำหรับเลือกหุ้นในรายการโปรด (กดทีเดียวสลับหน้าหุ้นทันที)
    for symbol in st.session_state.watchlist:
        # เน้นหุ้นที่กำลังถูกวิเคราะห์ให้เด่นชัดขึ้น
        btn_label = f"✨ {symbol} (กำลังเปิด)" if symbol == st.session_state.active_ticker else f"📁 {symbol}"
        if st.button(btn_label, key=f"sel_{symbol}", use_container_width=True):
            st.session_state.active_ticker = symbol
            st.rerun()

    st.markdown("<hr style='border-color: #1f2937; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # ตัวเลือกช่วงเวลาข้อมูล
    period = st.selectbox(
        "ช่วงเวลาวิเคราะห์ข้อมูลย้อนหลัง:",
        options=["3mo", "6mo", "1y", "2y"],
        index=2
    )

# 5. ดึงข้อมูลพิกัดราคาปัจจุบันและแนวรับแนวต้านจริง
active_ticker = st.session_state.active_ticker

# หัวเว็บบาร์สไตล์พรีเมียมคลีน
st.markdown("""
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
                <p style="font-size: 11px; color: #9ca3af; margin: 0; font-family: 'Prompt', sans-serif;">ระบบตีกราฟและประเมินสัญญาณเทคนิคัลเข้าใจง่ายที่สุด</p>
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
        # ใช้ดึงประวัติราคา 2 ปีเพื่อความนิ่งของดัชนีชี้วัด EMA
        stock_api = yf.Ticker(active_ticker)
        df = stock_api.history(period="2y")
        
        if df.empty:
            st.error(f"⚠️ ไม่พบข้อมูลสัญลักษณ์หุ้น '{active_ticker}' บนระบบ กรุณาลองใหม่อีกครั้ง")
        else:
            company_name = stock_api.info.get('longName', f"{active_ticker} Inc.")
            
            # ตัดข้อมูลตามช่วงเวลาที่ผู้ใช้เลือกดู
            if period == "3mo": df_view = df.tail(63)
            elif period == "6mo": df_view = df.tail(126)
            elif period == "1y": df_view = df.tail(252)
            else: df_view = df
            
            # คำนวณอินดิเคเตอร์ทางเทคนิค
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            
            # สูตรดัชนีโมเมนตัม RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, np.nan)
            df['RSI'] = 100 - (100 / (1 + rs))
            df['RSI'] = df['RSI'].fillna(50)
            
            # ตรวจสอบจุดต่ำสุดและจุดสูงสุดเพื่อตีเป็นแนวรับ-แนวต้าน
            resistance = df_view['High'].max()
            support = df_view['Low'].min()
            
            # ดึงราคาปัจจุบัน
            last_close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            price_change = last_close - prev_close
            pct_change = (price_change / prev_close) * 100
            
            current_rsi = df['RSI'].iloc[-1]
            current_ema20 = df['EMA20'].iloc[-1]
            current_ema50 = df['EMA50'].iloc[-1]
            
            # ประเมินเกณฑ์เพื่อให้คะแนนจุดเข้าซื้อและจุดขาย
            score = 0
            alert_reasons = []
            
            dist_to_support = (last_close - support) / support
            dist_to_resistance = (resistance - last_close) / last_close
            
            if dist_to_support < 0.025:
                score += 3
                alert_reasons.append(f"ราคาเข้าใกล้ขีดแนวรับสำคัญที่ **${support:.2f}** (ห่างเพียง {dist_to_support*100:.1f}%) ราคาเริ่มยืนสร้างฐานมั่นคง เป็นโอกาสทยอยสะสมหุ้น")
            elif dist_to_resistance < 0.025:
                score -= 3
                alert_reasons.append(f"ราคากำลังพุ่งขึ้นไปติดเพดานแนวต้านเก่าที่ **${resistance:.2f}** (ห่างเพียง {dist_to_resistance*100:.1f}%) ระวังมีแรงขายสกัดรอบสั้น")
            else:
                alert_reasons.append(f"ราคาเคลื่อนไหวแกว่งตัวในกรอบปกติ ระหว่างขีดแนวรับ ${support:.2f} ถึงสถิติแนวต้าน ${resistance:.2f}")
                
            if last_close > current_ema20 > current_ema50:
                score += 1.5
                alert_reasons.append("ราคายืนเหนือเส้นเฉลี่ยหลัก EMA20 และ EMA50 บ่งบอกทิศทางหลักเป็นขาขึ้นแข็งแกร่ง (Bullish Momentum)")
            elif last_close < current_ema20 < current_ema50:
                score -= 1.5
                alert_reasons.append("ราคาหลุดเส้นเฉลี่ยสะสมลงมา ทิศทางหลักอยู่ในช่วงชะลอตัวฝั่งขาลง (Bearish Momentum) ควรรอก่อน")
                
            if current_rsi < 30:
                score += 2.5
                alert_reasons.append(f"ดัชนีโมเมนตัม RSI ต่ำกว่า 30 (อยู่ที่ {current_rsi:.1f}) บ่งบอกสภาวะแรงขายหนักเกินไป (Oversold) มีลุ้นเกิดการดีดตัวระยะสั้น")
            elif current_rsi > 70:
                score -= 2.5
                alert_reasons.append(f"ดัชนีโมเมนตัม RSI สูงเกิน 70 (อยู่ที่ {current_rsi:.1f}) บ่งบอกสภาวะแรงซื้อล้นเกินไป (Overbought) มีความเสี่ยงต่อการโดนทุบสลับรอบ")

            # ประเมินสรุปเป็นคำแนะนำแบบเข้าใจง่ายที่สุด (Simple Actions)
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

            # 6. สร้างส่วนสรุปผลคำแนะนำระดับสายตา (Highlight Banner) ใหญ่ ชัดเจน ใช้งานง่ายที่สุด
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
                                ความคิดเห็นจากสูตรเทคนิคัลอัตโนมัติ
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

            # ตกแต่งแถบสีราคาเคลื่อนไหว
            price_change_color = "#10b981" if price_change >= 0 else "#ef4444"
            price_change_bg = "rgba(16, 185, 129, 0.1)" if price_change >= 0 else "rgba(239, 68, 68, 0.1)"
            
            # โซนสถานะความเสี่ยง RSI
            if current_rsi < 30:
                rsi_badge, rsi_badge_color, rsi_badge_bg = "โอกาสซื้อ (Oversold)", "#10b981", "rgba(16, 185, 129, 0.1)"
            elif current_rsi > 70:
                rsi_badge, rsi_badge_color, rsi_badge_bg = "ระวังขาย (Overbought)", "#ef4444", "rgba(239, 68, 68, 0.1)"
            else:
                rsi_badge, rsi_badge_color, rsi_badge_bg = "ปกติ (Neutral)", "#a855f7", "rgba(168, 85, 247, 0.1)"

            # 7. การ์ดรายงานตัวเลขสำคัญ (Dashboard Cards Grid) ลอย เด่น ชัดเจน
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
                        <span style="font-size: 11px; color: #9ca3af; display: block; margin-bottom: 4px;">🛡️ ขีดแนวรับ (ราคาต่ำสุดรอบนี้)</span>
                        <div>
                            <span style="font-size: 24px; font-weight: 800; color: #10b981;">${support:.2f}</span>
                        </div>
                    </div>
                    <!-- Resistance Card -->
                    <div style="background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 12px; font-family: 'Prompt';">
                        <span style="font-size: 11px; color: #9ca3af; display: block; margin-bottom: 4px;">🎯 ขีดแนวต้าน (ราคาขึ้นสูงสุดรอบนี้)</span>
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

            # 8. กล่องสรุปวิเคราะห์ข้อมูลย่อยจากสมองกล AI เข้าใจง่าย
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
                        💡 สรุปข้อวิเคราะห์หลักเพื่อช่วยตัดสินใจ (สรุปสั้น)
                    </h4>
                    <ul style="font-size: 12px; color: #cbd5e1; line-height: 1.6; padding-left: 0; margin: 0; font-family: 'Prompt', sans-serif;">
                        {advice_list_html}
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            # 9. โซนวาดกราฟเทคนิคัลระดับโปรที่ซูม-ลาก ดูง่าย (Plotly Engine)
            st.markdown("<h3 style='font-size: 14px; font-weight: 700; color: white; margin-bottom: 12px; font-family: \"Prompt\";'>📉 กราฟเทคนิคแบบสลับดูราคาและแรงซื้อขาย</h3>", unsafe_allow_html=True)
            
            df_chart = df.loc[df_view.index[0]:df_view.index[-1]].copy()
            
            # กำหนดจุดปักหมุด BUY หรือ SELL ลงบนตัวกราฟตามค่าโมเมนตัมที่เหมาะสม
            df_chart['Buy_Marker'] = np.nan
            df_chart['Sell_Marker'] = np.nan
            df_chart.loc[df_chart['RSI'] < 33, 'Buy_Marker'] = df_chart['Low'] * 0.985
            df_chart.loc[df_chart['RSI'] > 67, 'Sell_Marker'] = df_chart['High'] * 1.015

            # แบ่งพิกัด 2 กราฟ: กราฟแท่งเทียนราคา (บน) + กราฟ RSI (ล่าง)
            fig = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.08, 
                row_heights=[0.75, 0.25]
            )

            # กราฟด้านบน: แท่งเทียน (Candlesticks) สีคลีนชัดเจน
            fig.add_trace(go.Candlestick(
                x=df_chart.index,
                open=df_chart['Open'],
                high=df_chart['High'],
                low=df_chart['Low'],
                close=df_chart['Close'],
                name="ราคาซื้อขาย",
                increasing_line_color='#10b981', 
                decreasing_line_color='#ef4444',
                increasing_fillcolor='#10b981',
                decreasing_fillcolor='#ef4444'
            ), row=1, col=1)

            # เพิ่มเส้นค่าเฉลี่ยแนวโน้ม EMA20 (เส้นเร็ว)
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['EMA20'],
                line=dict(color='#3b82f6', width=1.8),
                name='แนวโน้มเร็ว (EMA 20)'
            ), row=1, col=1)
            
            # เพิ่มเส้นค่าเฉลี่ยแนวโน้ม EMA50 (เส้นปานกลาง)
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['EMA50'],
                line=dict(color='#ef4444', width=1.8),
                name='แนวโน้มกลาง (EMA 50)'
            ), row=1, col=1)

            # ตีเส้นปะตึกแนวรับ-แนวต้าน
            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], 
                y=[resistance, resistance],
                mode="lines",
                line=dict(color="#ef4444", width=1.5, dash="dash"),
                name="เส้นระวัง: แนวต้าน"
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], 
                y=[support, support],
                mode="lines",
                line=dict(color="#10b981", width=1.5, dash="dash"),
                name="เส้นลุ้นเด้ง: แนวรับ"
            ), row=1, col=1)

            # ใส่สัญลักษณ์ลูกศรจุดโอกาสซื้อ (BUY) และสัญลักษณ์จังหวะขาย (SELL) ชัดเจนสวยงาม
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Buy_Marker'],
                mode='markers',
                marker=dict(symbol='triangle-up', size=12, color='#10b981', line=dict(width=1, color='white')),
                name='โอกาสเข้าซื้อ (BUY)'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Sell_Marker'],
                mode='markers',
                marker=dict(symbol='triangle-down', size=12, color='#ef4444', line=dict(width=1, color='white')),
                name='สัญญาระวังแรงขาย (SELL)'
            ), row=1, col=1)

            # กราฟด้านล่าง: RSI Panel เพื่อดูปริมาณพลังซื้อ-ขายส่วนเกิน
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['RSI'],
                line=dict(color='#a855f7', width=2),
                name='ปริมาณแรงซื้อขาย RSI'
            ), row=2, col=1)

            # ปรับรูปแบบตารางและดีไซน์สีหลังกราฟให้ออกดาร์กโหมดหรูหรา
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                paper_bgcolor='#0b0f19',
                plot_bgcolor='#0b0f19',
                font=dict(color='#9ca3af', family='Inter, Prompt', size=10),
                height=550,
                margin=dict(l=40, r=40, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)')
            )
            
            # ตกแต่งพิกัดเส้นตาราง
            fig.update_xaxes(showgrid=True, gridcolor='#1f2937', linecolor='#374151')
            fig.update_yaxes(title_text="ระดับราคา ($)", showgrid=True, gridcolor='#1f2937', linecolor='#374151', row=1, col=1)
            fig.update_yaxes(title_text="พลังโมเมนตัม", range=[10, 90], showgrid=True, gridcolor='#1f2937', linecolor='#374151', row=2, col=1)
            
            # ลากเส้นมาตรฐานขีด 70 (อันตรายขาย) และเส้นขีด 30 (ปลอดภัยลุ้นเก็บสะสม) ของ RSI
            fig.add_shape(type="line", x0=df_chart.index[0], x1=df_chart.index[-1], y0=70, y1=70, line=dict(color="#ef4444", width=1, dash="dot"), row=2, col=1)
            fig.add_shape(type="line", x0=df_chart.index[0], x1=df_chart.index[-1], y0=30, y1=30, line=dict(color="#10b981", width=1, dash="dot"), row=2, col=1)

            st.plotly_chart(fig, use_container_width=True)

            # 10. ซ่อนตารางข้อมูลละเอียดเพื่อให้หน้าจอดูสบายตาขึ้น (จะดูเมื่อไหร่ค่อยกดขยาย)
            with st.expander("📝 เปิดดูตารางวิเคราะห์สถิติตัวเลขย้อนหลังเพิ่มเติม"):
                df_show = df_chart[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'EMA20']].sort_index(ascending=False)
                st.dataframe(df_show, use_container_width=True)

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูลหรือการจัดระดับราคา: {e}")
