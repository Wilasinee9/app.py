import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# 1. ตั้งค่าพื้นฐานเว็บแอปแบบ Wide Screen
st.set_page_config(
    page_title="AlphaTrader Pro - US Stock Technical Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ปรับแต่งดีไซน์ดาร์กธีมระดับพรีเมียมด้วย CSS (HTML UI Injection)
st.markdown("""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    </head>
    <style>
        /* รีเซ็ตดีไซน์สีพื้นหลังหน้าจอหลัก และปรับฟอนต์ของแอป */
        html, body, [class*="css"], .stApp {
            background-color: #090d16 !important;
            color: #f1f5f9 !important;
            font-family: 'Inter', 'Prompt', sans-serif !important;
        }
        
        /* ซ่อนแผงคอนโทรลหัวกระดาษดั้งเดิมของ Streamlit */
        header[data-testid="stHeader"] {
            background-color: rgba(17, 22, 34, 0.8) !important;
            backdrop-filter: blur(12px) !important;
            border-bottom: 1px solid #1f2635 !important;
        }
        
        /* ตกแต่งแถบควบคุมด้านข้าง (Sidebar) ให้เหมือนสไตล์ HTML */
        section[data-testid="stSidebar"] {
            background-color: #111622 !important;
            border-right: 1px solid #1f2635 !important;
        }
        
        /* ปรับดีไซน์ช่องกรอกข้อความ (Inputs) */
        div[data-baseweb="input"] {
            background-color: #1b2336 !important;
            border: 1px solid #1f2635 !important;
            border-radius: 12px !important;
        }
        input {
            color: #ffffff !important;
        }
        
        /* ปรับดีไซน์กล่องเลือก (Selectbox) */
        div[data-baseweb="select"] {
            background-color: #1b2336 !important;
            border: 1px solid #1f2635 !important;
            border-radius: 12px !important;
        }
        
        /* ตกแต่งปุ่มหลัก (ปุ่มค้นหา/บันทึก) */
        .stButton>button {
            background-color: #10b981 !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out !important;
            width: 100% !important;
            padding: 8px 16px !important;
        }
        .stButton>button:hover {
            background-color: #059669 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4) !important;
        }
        
        /* ปรับดีไซน์ปุ่มรายการโปรดในแถบข้างให้เหมือนลิสต์การ์ดของ HTML */
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #1b2336 !important;
            border: 1px solid #1f2635 !important;
            border-radius: 10px !important;
            text-align: left !important;
            color: #ffffff !important;
            margin-bottom: 4px !important;
            font-weight: 500 !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            border-color: #3b4b6c !important;
            background-color: #232d42 !important;
            box-shadow: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. จัดการ State ของหน้าเว็บและ Watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'META']
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = 'AAPL'

# 4. ออกแบบเมนูข้าง (Sidebar) ให้เรียบหรูดูเท่เหมือน HTML
with st.sidebar:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="font-size: 14px; font-weight: 600; color: #94a3b8; margin: 0; font-family: 'Prompt';">
                🔍 ค้นหาและวิเคราะห์หุ้น
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # ช่องใส่สัญลักษณ์หุ้น
    search_input = st.text_input("ใส่รหัสย่อหุ้น เช่น AAPL, TSLA, NVDA:", value="", placeholder="ระบุอักษรย่อยักษ์ใหญ่", key="stock_input")
    
    col_search_add, col_search_del = st.columns(2)
    with col_search_add:
        if st.button("➕ เพิ่มในโปรด", key="add_btn"):
            if search_input:
                new_ticker = search_input.upper().strip()
                if new_ticker not in st.session_state.watchlist:
                    st.session_state.watchlist.append(new_ticker)
                st.session_state.active_ticker = new_ticker
                st.rerun()
    with col_search_del:
        if st.button("❌ ลบออก", key="del_btn"):
            if search_input:
                remove_ticker = search_input.upper().strip()
                if remove_ticker in st.session_state.watchlist:
                    st.session_state.watchlist.remove(remove_ticker)
                st.rerun()
                
    st.markdown("<br><hr style='border-color: #1f2635;'><br>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size: 14px; font-weight: 600; color: #94a3b8; margin-bottom: 12px; font-family: \"Prompt\";'>⭐ รายการโปรด (Watchlist)</h4>", unsafe_allow_html=True)
    
    # สร้างเมนูคลิกเลือกหุ้นจาก Watchlist โดยทำเป็นปุ่มการ์ดสตรีมลิตแบบพรีเมียม
    for symbol in st.session_state.watchlist:
        if st.button(f"✨ {symbol}", key=f"select_{symbol}"):
            st.session_state.active_ticker = symbol
            st.rerun()

    st.markdown("<br><hr style='border-color: #1f2635;'>", unsafe_allow_html=True)
    period = st.selectbox(
        "ช่วงเวลาวิเคราะห์ข้อมูลย้อนหลัง:",
        options=["3mo", "6mo", "1y", "2y"],
        index=2
    )

# 5. ดึงข้อมูลพิกัดราคาจริง และดำเนินการคำนวณสูตรทางเทคนิค
active_ticker = st.session_state.active_ticker

# หัวโลโก้และแถบควบคุมพรีเมียมที่ยึดโครงมาจาก HTML
st.markdown("""
    <div style="
        border-bottom: 1px solid #1f2635;
        background-color: rgba(17, 22, 34, 0.8);
        backdrop-filter: blur(12px);
        padding: 16px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 16px;
        margin-bottom: 24px;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%); padding: 10px; border-radius: 12px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);">
                <span style="color: white; font-size: 20px; font-weight: bold;">📈</span>
            </div>
            <div>
                <h1 style="font-size: 20px; font-weight: 800; color: white; margin: 0; font-family: 'Prompt', sans-serif;">
                    ALPHATRADER <span style="font-size: 10px; background-color: rgba(16, 185, 129, 0.2); color: #10b981; font-weight: 600; padding: 2px 8px; border-radius: 9999px; margin-left: 4px;">PRO V2</span>
                </h1>
                <p style="font-size: 12px; color: #94a3b8; margin: 0; font-family: 'Prompt', sans-serif;">ระบบวิเคราะห์จุดรับ-ต้าน และตีกราฟส่งสัญญาณอัตโนมัติ (Python Server Engine)</p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; background-color: #1b2336; padding: 6px 12px; border-radius: 8px; border: 1px solid #1f2635;">
            <span style="height: 8px; width: 8px; border-radius: 50%; background-color: #10b981; display: inline-block; box-shadow: 0 0 8px #10b981;"></span>
            <span style="font-size: 11px; color: #94a3b8; font-family: 'Prompt';">Live Market Engine Active</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if active_ticker:
    try:
        stock_api = yf.Ticker(active_ticker)
        df = stock_api.history(period="2y")
        
        if df.empty:
            st.error(f"ไม่พบข้อมูลสัญลักษณ์หุ้น '{active_ticker}' กรุณาเปลี่ยนชื่อสัญลักษณ์หุ้นและลองใหม่อีกครั้ง")
        else:
            # รายละเอียดชื่อบริษัทและประเภท
            company_name = stock_api.info.get('longName', f"{active_ticker} Inc.")
            
            # ตัดข้อมูลตามช่วงเวลาที่ผู้ใช้อยากดู
            if period == "3mo": df_view = df.tail(63)
            elif period == "6mo": df_view = df.tail(126)
            elif period == "1y": df_view = df.tail(252)
            else: df_view = df
            
            # คำนวณอินดิเคเตอร์ทางเทคนิค
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, np.nan)
            df['RSI'] = 100 - (100 / (1 + rs))
            df['RSI'] = df['RSI'].fillna(50)
            
            # คำนวณขีดแนวรับ-แนวต้านหลัก
            resistance = df_view['High'].max()
            support = df_view['Low'].min()
            
            # ดึงสถิติล่าสุด
            last_close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            price_change = last_close - prev_close
            pct_change = (price_change / prev_close) * 100
            
            current_rsi = df['RSI'].iloc[-1]
            current_ema20 = df['EMA20'].iloc[-1]
            current_ema50 = df['EMA50'].iloc[-1]
            
            # ระบบจัดอันดับคำแนะนำสิทธิพิเศษทางเทคนิค
            score = 0
            alert_reasons = []
            
            dist_to_support = (last_close - support) / support
            dist_to_resistance = (resistance - last_close) / last_close
            
            if dist_to_support < 0.02:
                score += 3
                alert_reasons.append(f"ราคาเริ่มชะลอตัวและรักษาระดับเหนือแนวรับหลัก ${support:.2f} (ใกล้เคียงมาก ห่างแค่ {dist_to_support*100:.1f}%) เป็นจังหวะทยอยสะสมที่ปลอดภัย")
            elif dist_to_resistance < 0.02:
                score -= 3
                alert_reasons.append(f"ราคากำลังทดสอบแนวต้านหลัก ${resistance:.2f} (ห่างเพียง {dist_to_resistance*100:.1f}%) แนะนำลดพอร์ตเพื่อรอจังหวะย่อซื้อใหม่")
            else:
                alert_reasons.append(f"ราคายังเคลื่อนไหวในกรอบสะสมระหว่างแนวรับ ${support:.2f} และแนวต้าน ${resistance:.2f}")
                
            if last_close > current_ema20 > current_ema50:
                score += 1.5
                alert_reasons.append("โครงสร้างหลักเป็นขาขึ้นชัดเจน (Bullish Pattern) เส้น EMA20 ตัดอยู่เหนือ EMA50 สนับสนุนโมเมนตัมบวก")
            elif last_close < current_ema20 < current_ema50:
                score -= 1.5
                alert_reasons.append("โครงสร้างหลักเป็นขาลง (Bearish Pattern) หลีกเลี่ยงจนกว่าราคาจะสร้างฐานเหนือเส้น EMA 20 ได้อย่างมั่นคง")
                
            if current_rsi < 30:
                score += 2.5
                alert_reasons.append(f"ดัชนี RSI ({current_rsi:.1f}) อยู่ในเขตขายมากเกินไป (Oversold) มีโอกาสสูงที่จะเกิดการรีบาวด์ระยะสั้น")
            elif current_rsi > 70:
                score -= 2.5
                alert_reasons.append(f"ดัชนี RSI ({current_rsi:.1f}) อยู่ในเขตซื้อมากเกินไป (Overbought) มีแรงไล่ราคาที่หนาแน่น เสี่ยงต่อการโดนทุบสลับตัว")
            else:
                alert_reasons.append(f"ดัชนีโมเมนตัม RSI อยู่ในโซนกลางที่ระดับ {current_rsi:.1f} (Neutral) การซื้อขายมีความเสี่ยงปานกลาง")

            # ประเมินเกณฑ์สรุปแบบ HTML Badge
            if score >= 2.5:
                verdict_status = "STRONG BUY (สัญญาณซื้อแข็งแกร่ง)"
                verdict_color = "#10b981"
                verdict_bg = "rgba(16, 185, 129, 0.1)"
                verdict_border = "rgba(16, 185, 129, 0.3)"
                verdict_icon = "🟢"
                advise_card_bg = "rgba(16, 185, 129, 0.05)"
                advise_card_border = "rgba(16, 185, 129, 0.15)"
                advise_icon_color = "#10b981"
                advise_icon_bg = "rgba(16, 185, 129, 0.2)"
            elif score >= 1:
                verdict_status = "BUY (เข้าซื้อสะสม)"
                verdict_color = "#0d9488"
                verdict_bg = "rgba(13, 148, 136, 0.1)"
                verdict_border = "rgba(13, 148, 136, 0.3)"
                verdict_icon = "➕"
                advise_card_bg = "rgba(13, 148, 136, 0.05)"
                advise_card_border = "rgba(13, 148, 136, 0.15)"
                advise_icon_color = "#0d9488"
                advise_icon_bg = "rgba(13, 148, 136, 0.2)"
            elif score <= -2.5:
                verdict_status = "STRONG SELL (ควรระวังแรงทุบ/ขายออก)"
                verdict_color = "#f43f5e"
                verdict_bg = "rgba(244, 63, 94, 0.1)"
                verdict_border = "rgba(244, 63, 94, 0.3)"
                verdict_icon = "🔴"
                advise_card_bg = "rgba(244, 63, 94, 0.05)"
                advise_card_border = "rgba(244, 63, 94, 0.15)"
                advise_icon_color = "#f43f5e"
                advise_icon_bg = "rgba(244, 63, 94, 0.2)"
            elif score <= -1:
                verdict_status = "SELL (แบ่งทยอยขายทำกำไร)"
                verdict_color = "#f97316"
                verdict_bg = "rgba(249, 115, 22, 0.1)"
                verdict_border = "rgba(249, 115, 22, 0.3)"
                verdict_icon = "⚠️"
                advise_card_bg = "rgba(249, 115, 22, 0.05)"
                advise_card_border = "rgba(249, 115, 22, 0.15)"
                advise_icon_color = "#f97316"
                advise_icon_bg = "rgba(249, 115, 22, 0.2)"
            else:
                verdict_status = "HOLD (ถือครองดูทิศทาง)"
                verdict_color = "#eab308"
                verdict_bg = "rgba(234, 179, 8, 0.1)"
                verdict_border = "rgba(234, 179, 8, 0.3)"
                verdict_icon = "⏳"
                advise_card_bg = "rgba(234, 179, 8, 0.05)"
                advise_card_border = "rgba(234, 179, 8, 0.15)"
                advise_icon_color = "#eab308"
                advise_icon_bg = "rgba(234, 179, 8, 0.2)"

            # วาดแผงหน้าจอ Active Stock แบบ HTML 
            st.markdown(f"""
                <div style="
                    background: linear-gradient(to right, #111622, #171e2e);
                    border: 1px solid #1f2635;
                    padding: 24px;
                    border-radius: 16px;
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    justify-content: space-between;
                    position: relative;
                    overflow: hidden;
                    margin-bottom: 24px;
                ">
                    <div style="position: absolute; right: 20px; top: -30px; opacity: 0.05; font-size: 120px; font-weight: 900; color: #ffffff; user-select: none; pointer-events: none;">
                        {active_ticker}
                    </div>
                    <div style="display: flex; align-items: center; gap: 16px; position: relative; z-index: 1;">
                        <div style="height: 64px; width: 64px; background-color: #1b2336; border: 1px solid #2b3752; border-radius: 16px; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 22px; font-weight: 900; color: white; letter-spacing: -0.05em;">{active_ticker}</span>
                        </div>
                        <div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <h2 style="font-size: 22px; font-weight: 700; color: white; margin: 0; font-family: 'Prompt';">{company_name}</h2>
                                <span style="font-size: 10px; background-color: #1e293b; color: #cbd5e1; padding: 2px 6px; border-radius: 4px; font-weight: 600;">NASDAQ</span>
                            </div>
                            <p style="font-size: 13px; color: #94a3b8; margin: 4px 0 0 0; font-family: 'Prompt';">วิเคราะห์ระดับแนวรับ-แนวต้านหลัก และจุดซื้อขายทางจิตวิทยา</p>
                        </div>
                    </div>
                    <div style="
                        background-color: {verdict_bg};
                        border: 1px solid {verdict_border};
                        padding: 12px 20px;
                        border-radius: 16px;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        position: relative;
                        z-index: 1;
                    ">
                        <div style="font-size: 24px; color: {verdict_color};">{verdict_icon}</div>
                        <div>
                            <span style="font-size: 9px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; display: block; font-weight: bold; font-family: 'Prompt';">สัญญาณเทคนิคัลหลัก</span>
                            <span style="font-size: 16px; font-weight: 900; color: {verdict_color}; font-family: 'Prompt';">{verdict_status}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # คัดสรรตัวเลขและพื้นสีของการเปลี่ยนราคาส่วนต่าง
            price_change_color = "#10b981" if price_change >= 0 else "#f43f5e"
            price_change_bg = "rgba(16, 185, 129, 0.1)" if price_change >= 0 else "rgba(244, 63, 94, 0.1)"
            
            # ระบุโซนสเตตัส RSI
            if current_rsi < 30:
                rsi_status, rsi_status_color, rsi_status_bg = "Oversold", "#10b981", "rgba(16, 185, 129, 0.15)"
            elif current_rsi > 70:
                rsi_status, rsi_status_color, rsi_status_bg = "Overbought", "#f43f5e", "rgba(244, 63, 94, 0.15)"
            else:
                rsi_status, rsi_status_color, rsi_status_bg = "Neutral", "#a855f7", "rgba(168, 85, 247, 0.15)"

            # วาดกล่องข้อมูล 4 ดัชนีสำคัญ (Metrics Row) แบบ HTML คัสตอม
            st.markdown(f"""
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 16px;
                    margin-bottom: 24px;
                ">
                    <!-- Price card -->
                    <div style="background-color: #111622; border: 1px solid #1f2635; padding: 16px; border-radius: 16px; font-family: 'Prompt';">
                        <span style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 4px;">ราคาล่าสุด</span>
                        <div style="display: flex; align-items: baseline; gap: 8px;">
                            <span style="font-size: 24px; font-weight: 800; color: white;">${last_close:.2f}</span>
                            <span style="font-size: 12px; font-weight: 600; color: {price_change_color}; background-color: {price_change_bg}; padding: 2px 6px; border-radius: 6px;">{pct_change:+.2f}%</span>
                        </div>
                    </div>
                    <!-- Support card -->
                    <div style="background-color: #111622; border: 1px solid #1f2635; padding: 16px; border-radius: 16px; font-family: 'Prompt';">
                        <span style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 4px;">🛡️ แนวรับสำคัญ (Support)</span>
                        <div>
                            <span style="font-size: 24px; font-weight: 800; color: #10b981;">${support:.2f}</span>
                        </div>
                    </div>
                    <!-- Resistance card -->
                    <div style="background-color: #111622; border: 1px solid #1f2635; padding: 16px; border-radius: 16px; font-family: 'Prompt';">
                        <span style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 4px;">🎯 แนวต้านสำคัญ (Resistance)</span>
                        <div>
                            <span style="font-size: 24px; font-weight: 800; color: #f43f5e;">${resistance:.2f}</span>
                        </div>
                    </div>
                    <!-- RSI card -->
                    <div style="background-color: #111622; border: 1px solid #1f2635; padding: 16px; border-radius: 16px; display: flex; flex-direction: column; justify-content: space-between; font-family: 'Prompt';">
                        <span style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 4px;">📊 ดัชนี RSI (14)</span>
                        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                            <span style="font-size: 24px; font-weight: 800; color: #a855f7;">{current_rsi:.1f}</span>
                            <span style="font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 6px; background-color: {rsi_status_bg}; color: {rsi_status_color};">{rsi_status}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # กล่องความเห็น AI ผู้ช่วยอัจฉริยะ (AI Technical Advisor Panel)
            advice_list_html = "".join([f"<li style='margin-bottom: 6px;'>• {reason}</li>" for reason in alert_reasons])
            st.markdown(f"""
                <div style="
                    background-color: {advise_card_bg};
                    border: 1px solid {advise_card_border};
                    padding: 20px;
                    border-radius: 16px;
                    display: flex;
                    align-items: start;
                    gap: 14px;
                    margin-bottom: 24px;
                ">
                    <div style="background-color: {advise_icon_bg}; padding: 8px; border-radius: 12px; color: {advise_icon_color}; font-size: 20px; display: flex; align-items: center; justify-content: center;">
                        🧠
                    </div>
                    <div>
                        <h4 style="font-weight: 700; color: {advise_icon_color}; font-size: 14px; margin: 0 0 6px 0; font-family: 'Prompt', sans-serif;">ความเห็นผู้ช่วยอัจฉริยะ (AI Technical Advisor)</h4>
                        <ul style="font-size: 12px; color: #cbd5e1; line-height: 1.6; list-style-type: none; padding-left: 0; margin: 0; font-family: 'Prompt', sans-serif;">
                            {advice_list_html}
                        </ul>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # --- โซนวาดกราฟเทคนิคสไตล์ดาร์กธีมพรีเมียม (Plotly Engine) ---
            st.markdown("<h3 style='font-size: 16px; font-weight: 700; color: white; margin-bottom: 12px; font-family: \"Prompt\";'>📈 กราฟเทคนิคเชิงลึกและจุดซื้อขาย</h3>", unsafe_allow_html=True)
            
            df_chart = df.loc[df_view.index[0]:df_view.index[-1]].copy()
            
            # ระบุสัญลักษณ์จุด BUY/SELL
            df_chart['Buy_Marker'] = np.nan
            df_chart['Sell_Marker'] = np.nan
            df_chart.loc[df_chart['RSI'] < 33, 'Buy_Marker'] = df_chart['Low'] * 0.985
            df_chart.loc[df_chart['RSI'] > 67, 'Sell_Marker'] = df_chart['High'] * 1.015

            # แบ่งพิกัด 2 กราฟซ้อนกัน
            fig = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.08, 
                row_heights=[0.75, 0.25]
            )

            # 1. กราฟด้านบน: Candlesticks
            fig.add_trace(go.Candlestick(
                x=df_chart.index,
                open=df_chart['Open'],
                high=df_chart['High'],
                low=df_chart['Low'],
                close=df_chart['Close'],
                name="ราคาดิบ (Candles)",
                increasing_line_color='#10b981', 
                decreasing_line_color='#f43f5e',
                increasing_fillcolor='#10b981',
                decreasing_fillcolor='#f43f5e'
            ), row=1, col=1)

            # เส้น EMA20 และ EMA50
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['EMA20'],
                line=dict(color='#60a5fa', width=1.8),
                name='EMA 20 (เทรนด์เร็ว)'
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['EMA50'],
                line=dict(color='#f43f5e', width=1.8),
                name='EMA 50 (เทรนด์กลาง)'
            ), row=1, col=1)

            # เส้นขีดแนวรับ-แนวต้าน
            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], 
                y=[resistance, resistance],
                mode="lines",
                line=dict(color="#f43f5e", width=1.5, dash="dash"),
                name="แนวต้านสำคัญ (Resistance)"
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], 
                y=[support, support],
                mode="lines",
                line=dict(color="#10b981", width=1.5, dash="dash"),
                name="แนวรับสถิติหลัก (Support)"
            ), row=1, col=1)

            # จุดหมุดสัญญาณการเทรดจริงบนกราฟ
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Buy_Marker'],
                mode='markers',
                marker=dict(symbol='triangle-up', size=12, color='#10b981', line=dict(width=1, color='white')),
                name='สัญญาณซื้อ (BUY)'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Sell_Marker'],
                mode='markers',
                marker=dict(symbol='triangle-down', size=12, color='#f43f5e', line=dict(width=1, color='white')),
                name='สัญญาณขาย (SELL)'
            ), row=1, col=1)

            # 2. กราฟด้านล่าง: RSI Panel
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['RSI'],
                line=dict(color='#a855f7', width=2),
                name='RSI(14)'
            ), row=2, col=1)

            # ปรับแต่งรายละเอียดหน้าตากราฟให้พรีเมียมสีดำเข้ม
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                paper_bgcolor='#090d16',
                plot_bgcolor='#090d16',
                font=dict(color='#94a3b8', family='Inter, Prompt', size=10),
                height=640,
                margin=dict(l=40, r=40, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)')
            )
            
            # เส้นพิกัดกรอบสีจาง และสีเขีดแบ่งระดับ RSI
            fig.update_xaxes(showgrid=True, gridcolor='#171e2e', linecolor='#1f2635')
            fig.update_yaxes(title_text="ระดับราคา ($)", showgrid=True, gridcolor='#171e2e', linecolor='#1f2635', row=1, col=1)
            fig.update_yaxes(title_text="RSI Value", range=[10, 90], showgrid=True, gridcolor='#171e2e', linecolor='#1f2635', row=2, col=1)
            
            fig.add_shape(type="line", x0=df_chart.index[0], x1=df_chart.index[-1], y0=70, y1=70, line=dict(color="#f43f5e", width=1, dash="dot"), row=2, col=1)
            fig.add_shape(type="line", x0=df_chart.index[0], x1=df_chart.index[-1], y0=30, y1=30, line=dict(color="#10b981", width=1, dash="dot"), row=2, col=1)

            st.plotly_chart(fig, use_container_width=True)

            # ตารางตัวเลขสถิติแบบละเอียดซ่อนอยู่ (Expander)
            with st.expander("📝 เปิดดูตารางวิเคราะห์สถิติตัวเลขย้อนหลังโดยละเอียด"):
                df_show = df_chart[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'EMA20']].sort_index(ascending=False)
                st.dataframe(df_show, use_container_width=True)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลหรือคำนวณราคาหุ้น: {e}")
