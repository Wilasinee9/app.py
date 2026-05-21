import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ตั้งค่าหน้าเว็บให้เป็นแบบ Wide screen และใส่หัวข้อแอปพลิเคชัน
st.set_page_config(
    page_title="AlphaTrader Pro - US Stock Analysis Hub",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# เพิ่มสไตล์ CSS ในตัวเพื่อควบคุมดีไซน์ หน้าตาปุ่ม การจัดหน้า และกล่องคำแนะนำให้สวยงามระดับพรีเมียม
st.markdown("""
    <style>
    /* ปรับแต่งหน้าตาพื้นหลังและฟอนต์เบื้องต้น */
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
    }
    
    /* ปรับแต่งความโค้งมนของกล่องข้อความและโมดูลต่างๆ */
    .stApp {
        background-color: #0b0e14;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #94a3b8;
    }
    
    /* ตกแต่งปุ่มเมนูทางซ้ายมือ */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    
    /* กรอบสไตล์ Dashboard หรูหรา */
    .metric-card {
        background: #121620;
        border: 1px solid #1e2530;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ระบบจัดเก็บรายชื่อหุ้นโปรด (Watchlist) ลงใน Session State เพื่อให้ข้อมูลคงอยู่ระหว่างเปลี่ยนหน้าหรือค้นหา
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'META']

# แผงควบคุมด้านข้าง (Sidebar Dynamic Panel)
with st.sidebar:
    st.markdown("<h2 style='color:#10b981; margin-bottom:0;'>🦅 ALPHATRADER PRO</h2>", unsafe_allow_html=True)
    st.caption("ระบบวิเคราะห์ทางเทคนิคหุ้นสหรัฐฯ อัตโนมัติ")
    st.markdown("---")
    
    # ส่วนของ Watchlist รายการโปรด
    st.subheader("⭐ รายการโปรดของคุณ")
    
    # ตัวเลือกดึงหุ้นจากรายการโปรดมาแสดงทันที
    selected_watchlist = st.selectbox(
        "เลือกหุ้นจากรายการโปรด:", 
        ["--- เลือกหุ้นโปรด ---"] + st.session_state.watchlist,
        index=0
    )
    
    # ส่วนของการค้นหาหุ้นใหม่แบบอิสระ
    st.subheader("🔍 ค้นหาและวิเคราะห์")
    search_ticker = st.text_input(
        "ใส่ชื่อย่อหุ้นสหรัฐฯ:", 
        value="AAPL" if selected_watchlist == "--- เลือกหุ้นโปรด ---" else selected_watchlist
    )
    ticker = search_ticker.upper().strip()
    
    # ปุ่มกดเพิ่ม/ลบ หุ้นจากรายการโปรด
    col_add, col_del = st.columns(2)
    with col_add:
        if st.button("➕ เพิ่มในโปรด", use_container_width=True):
            if ticker and ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                st.toast(f"เพิ่ม {ticker} ลงรายการโปรดแล้ว!", icon="✅")
                st.rerun()
    with col_del:
        if st.button("❌ ลบจากโปรด", use_container_width=True):
            if ticker in st.session_state.watchlist:
                st.session_state.watchlist.remove(ticker)
                st.toast(f"ลบ {ticker} ออกจากรายการโปรดแล้ว", icon="🗑️")
                st.rerun()
                
    st.markdown("---")
    # ตัวเลือกปรับ Timeframe
    period = st.selectbox(
        "กรอบเวลาราคาหุ้นย้อนหลัง:", 
        options=["3mo", "6mo", "1y", "2y"], 
        index=2,
        help="ใช้ช่วงข้อมูลที่เลือกเพื่อคำนวณแนวรับ-แนวต้านและโมเมนตัมเทรนด์หลัก"
    )

# ตรวจสอบว่าผู้ใช้เลือกหุ้นและจะดึงข้อมูลมาแสดงผล
if ticker:
    try:
        # ดึงข้อมูลจาก Yahoo Finance API
        stock_api = yf.Ticker(ticker)
        # ดึงข้อมูลราคาย้อนหลังมาเผื่อสำหรับการคำนวณอินดิเคเตอร์
        df = stock_api.history(period="2y")
        
        if df.empty:
            st.error(f"🔍 ไม่พบข้อมูลหุ้นสัญลักษณ์ '{ticker}' กรุณาตรวจสอบตัวย่อหุ้นสหรัฐฯ และลองใหม่อีกครั้ง")
        else:
            # ดึงชื่อบริษัทเต็ม
            stock_info = stock_api.info
            company_name = stock_info.get('longName', f"{ticker} Corporation")
            market_cap = stock_info.get('marketCap', 0)
            
            # ตัดข้อมูลตามช่วงเวลาที่ผู้ใช้เลือกดูจริง
            if period == "3mo":
                df_view = df.tail(63)
            elif period == "6mo":
                df_view = df.tail(126)
            elif period == "1y":
                df_view = df.tail(252)
            else:
                df_view = df

            # 1. คำนวณเส้นค่าเฉลี่ยเคลื่อนที่เพื่อจับแนวโน้มแนวรับแบบไดนามิก
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            
            # 2. คำนวณดัชนีโมเมนตัมกำลังการซื้อขาย (RSI - 14 วัน)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, np.nan)
            df['RSI'] = 100 - (100 / (1 + rs))
            df['RSI'] = df['RSI'].fillna(50) # กรณีข้อมูลแกว่งตัวแคบมากให้เป็นค่ากลาง
            
            # 3. คำนวณแนวรับ-แนวต้านทางจิตวิทยาจากช่วง High-Low ย้อนหลังที่ผู้ใช้เลือก
            resistance = df_view['High'].max()
            support = df_view['Low'].min()
            
            # ค่าข้อมูลล่าสุด
            last_close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            price_change = last_close - prev_close
            pct_change = (price_change / prev_close) * 100
            
            current_rsi = df['RSI'].iloc[-1]
            current_ema20 = df['EMA20'].iloc[-1]
            current_ema50 = df['EMA50'].iloc[-1]

            # ออกแบบคะแนนประเมิน (Technical Scoring System) ว่าคุ้มค่าต่อการ ซื้อ หรือ ขาย
            score = 0
            analysis_reasons = []
            
            # เงื่อนไขระยะห่างแนวรับแนวต้าน (เทียบความห่างเป็นเปอร์เซ็นต์)
            distance_to_support_pct = (last_close - support) / support
            distance_to_resistance_pct = (resistance - last_close) / last_close
            
            if distance_to_support_pct < 0.02:
                score += 3
                analysis_reasons.append(f"🛡️ ราคาปรับตัวลงมาใกล้แนวรับหลักที่ **${support:.2f}** (ห่างเพียง {distance_to_support_pct*100:.1f}%) ซึ่งเป็นจุดปลอดภัยทางเทคนิคัลที่มีแรงรับซื้อกลับค่อนข้างหนาแน่น")
            elif distance_to_resistance_pct < 0.02:
                score -= 3
                analysis_reasons.append(f"🎯 ราคาพุ่งชนหรือใกล้แนวต้านสำคัญที่ **${resistance:.2f}** (ห่างเพียง {distance_to_resistance_pct*100:.1f}%) ระวังแรงขายทำกำไรฉับพลัน")
            else:
                analysis_reasons.append(f"⚖️ ปัจจุบันราคาวิ่งอยู่ในโซนปลอดภัย โดยเคลื่อนไหวอยู่ในกรอบระหว่างแนวรับ ${support:.2f} ถึงแนวต้าน ${resistance:.2f}")

            # สัญญาณแนวโน้มเทรนด์จากเส้น EMA 20 และ EMA 50
            if last_close > current_ema20 > current_ema50:
                score += 1.5
                analysis_reasons.append("📈 โครงสร้างราคาอยู่ในเทรนด์ขาขึ้นแข็งแกร่ง (Bullish Wave) ราคาปิดยืนเหนือเส้นค่าเฉลี่ย EMA 20 และ 50 วัน")
            elif last_close < current_ema20 < current_ema50:
                score -= 1.5
                analysis_reasons.append("📉 โครงสร้างราคาอยู่ในทิศทางขาลงอ่อนแรง (Bearish Wave) แนวโน้มหลักเสียทรง แนะนำให้ชะลอการลงทุน")
                
            # สัญญาณดัชนีโมเมนตัมกำลังการซื้อขาย (RSI)
            if current_rsi < 33:
                score += 2
                analysis_reasons.append(f"🟢 โมเมนตัม RSI อยู่ในจุดต่ำสุดที่ **{current_rsi:.1f}** บ่งชี้ภาวะขายมากเกินไป (Oversold Area) มีโอกาสเกิดรอบ Technical Rebound เด้งกลับ")
            elif current_rsi > 67:
                score -= 2
                analysis_reasons.append(f"🔴 โมเมนตัม RSI วิ่งขึ้นสูงที่ **{current_rsi:.1f}** บ่งชี้สภาวะซื้อมากเกินไป (Overbought Area) ตลาดเริ่มร้อนแรงและมีความเสี่ยงย่อตัวระยะสั้น")
            else:
                analysis_reasons.append(f"⚪ ค่า RSI เป็นกลางอยู่ที่ **{current_rsi:.1f}** แรงซื้อและแรงขายค่อนข้างสมดุล")

            # ประเมินคำแนะนำขั้นเด็ดขาด (Verdict Evaluation)
            if score >= 2:
                verdict_status = "🎯 แนะนำ: ซื้อสะสม (STRONG BUY / ACCUMULATE)"
                verdict_color = "#10b981"  # สีเขียวสด
                verdict_bg = "rgba(16, 185, 129, 0.15)"
            elif score <= -2:
                verdict_status = "⚠️ แนะนำ: ขาย หรือ ลดน้ำหนักพอร์ต (SELL / TAKE PROFIT)"
                verdict_color = "#ef4444"  # สีแดงสด
                verdict_bg = "rgba(239, 68, 68, 0.15)"
            else:
                verdict_status = "⏳ แนะนำ: ถือครอง / รอดูสัญญาณเพื่อเลือกข้าง (HOLD / WAIT & SEE)"
                verdict_color = "#f59e0b"  # สีเหลืองส้ม
                verdict_bg = "rgba(245, 158, 11, 0.15)"

            # แสดงข้อมูลหัวกระดาษหน้าบอร์ด
            st.write(f"### 🇺🇸 ตลาดหลักทรัพย์สหรัฐฯ > {ticker}")
            st.markdown(f"<h1 style='margin-top:-15px; color:#ffffff;'>{company_name}</h1>", unsafe_allow_html=True)
            
            # โซนสรุปคำแนะนำในรูปแบบแถบหรูหราสะดุดตา
            st.markdown(f"""
                <div style="background-color: {verdict_bg}; padding: 22px; border-radius: 16px; border-left: 8px solid {verdict_color}; margin-bottom: 25px;">
                    <h3 style="margin: 0; color: {verdict_color}; font-weight:700; font-size:22px;">{verdict_status}</h3>
                    <div style="margin-top: 12px; color: #e2e8f0; font-size: 15px; line-height: 1.7;">
                        {'<br>'.join([f"• {reason}" for reason in analysis_reasons])}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # แสดงตารางแสดงข้อมูลสรุป 4 ตัวเลขดัชนีสำคัญ (Metrics Row)
            col_p, col_r, col_s, col_rsi = st.columns(4)
            with col_p:
                st.metric(
                    label="💵 ราคาปัจจุบันล่าสุด", 
                    value=f"${last_close:.2f}", 
                    delta=f"{price_change:+.2f} ({pct_change:+.2f}%)"
                )
            with col_r:
                st.metric(
                    label="🎯 แนวต้านสำคัญ (กรอบรอบนี้)", 
                    value=f"${resistance:.2f}", 
                    delta=f"ห่างอีก ${(resistance - last_close):.2f}" if (resistance - last_close) > 0 else "ชนแนวต้าน",
                    delta_color="inverse"
                )
            with col_s:
                st.metric(
                    label="🛡️ แนวรับหลักสำคัญ", 
                    value=f"${support:.2f}", 
                    delta=f"ห่างอีก ${(last_close - support):.2f}"
                )
            with col_rsi:
                rsi_state = "ปกติ"
                if current_rsi > 70: rsi_state = "Overbought (ซื้อมากไป)"
                elif current_rsi < 30: rsi_state = "Oversold (ขายมากไป)"
                st.metric(
                    label="📊 โมเมนตัม RSI (14)", 
                    value=f"{current_rsi:.1f}", 
                    delta=rsi_state,
                    delta_color="normal" if current_rsi < 30 else "inverse" if current_rsi > 70 else "off"
                )

            st.write("---")

            st.subheader("📈 กราฟเทคนิคัลวิเคราะห์แบบเชิงรุก")
            
            # ตัดข้อมูลสำหรับวาดพล็อตเฉพาะกรอบเวลาผู้ใช้เลือก
            df_chart = df.loc[df_view.index[0]:df_view.index[-1]].copy()
            
            # ค้นหาจุดพิกัด Buy และ Sell Signal เพื่อแสดงหมุดในรูปแบบ Arrow สวยงาม
            df_chart['Buy_Marker'] = np.nan
            df_chart['Sell_Marker'] = np.nan
            
            # เงื่อนไขสร้างจุดหมุดพิกัดในประวัติศาสตร์ราคาบนกราฟ
            df_chart.loc[df_chart['RSI'] < 33, 'Buy_Marker'] = df_chart['Low'] * 0.985
            df_chart.loc[df_chart['RSI'] > 67, 'Sell_Marker'] = df_chart['High'] * 1.015

            # ออกแบบโครงสร้างกราฟแบ่งออกเป็น 2 ส่วนย่อย (บน: ราคากราฟแท่งเทียน, ล่าง: RSI ดัชนีวัดความร้อนแรง)
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
                decreasing_line_color='#ef4444',
                increasing_fillcolor='#10b981',
                decreasing_fillcolor='#ef4444'
            ), row=1, col=1)

            # เส้น EMA20 (สีฟ้า) และ เส้น EMA50 (สีชมพู)
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['EMA20'],
                line=dict(color='#60a5fa', width=1.8),
                name='EMA 20 วัน (เทรนด์เร็ว)'
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['EMA50'],
                line=dict(color='#f43f5e', width=1.8),
                name='EMA 50 วัน (เทรนด์กลาง)'
            ), row=1, col=1)

            # พลอตวาดเส้นระบุแนวต้านหลักสีแดงปะ และแนวรับสีเขียวปะ
            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], 
                y=[resistance, resistance],
                mode="lines",
                line=dict(color="#ef4444", width=2, dash="dash"),
                name="เส้นระบุแนวต้านสำคัญ"
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], 
                y=[support, support],
                mode="lines",
                line=dict(color="#10b981", width=2, dash="dash"),
                name="เส้นระบุแนวรับสถิติหลัก"
            ), row=1, col=1)

            # พลอตจุดระบุ Buy และ Sell Signal บนกราฟแท่งเทียนจริงๆ
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Buy_Marker'],
                mode='markers',
                marker=dict(symbol='triangle-up', size=13, color='#10b981', line=dict(width=1, color='white')),
                name='สัญญาณซื้อ (RSI ดรอป)'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Sell_Marker'],
                mode='markers',
                marker=dict(symbol='triangle-down', size=13, color='#ef4444', line=dict(width=1, color='white')),
                name='สัญญาณขาย (RSI พีค)'
            ), row=1, col=1)

            # 2. กราฟด้านล่าง: RSI Panel
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['RSI'],
                line=dict(color='#a855f7', width=2),
                name='Relative Strength Index (RSI)'
            ), row=2, col=1)

            # ขีดเส้นระดับอันตราย Overbought (70) และ Oversold (30)
            fig.add_shape(
                type="line", x0=df_chart.index[0], x1=df_chart.index[-1],
                y0=70, y1=70, line=dict(color="#ef4444", width=1.5, dash="dot"),
                row=2, col=1
            )
            fig.add_shape(
                type="line", x0=df_chart.index[0], x1=df_chart.index[-1],
                y0=30, y1=30, line=dict(color="#10b981", width=1.5, dash="dot"),
                row=2, col=1
            )

            # ปรับแต่งรายละเอียดหน้าตากราฟทั้งหมดให้เป็นรูปแบบพรีเมียมธีมมืด
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                height=720,
                margin=dict(l=40, r=40, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_yaxes(title_text="ระดับราคา ($)", row=1, col=1)
            fig.update_yaxes(title_text="RSI Value", range=[10, 90], row=2, col=1)

            # นำมาแสดงผลบนเว็บเบราว์เซอร์
            st.plotly_chart(fig, use_container_width=True)

            # ขยายหน้าต่างข้อมูลดิบเพิ่มเติมสำหรับนักวิเคราะห์ที่ชอบจดสถิติตัวเลข
            with st.expander("📝 เปิดดูตารางวิเคราะห์สถิติตัวเลขย้อนหลังโดยละเอียด"):
                df_show = df_chart[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'EMA20']].sort_index(ascending=False)
                st.dataframe(df_show, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ เกิดข้อผิดพลาดในการดึงประมวลผลข้อมูลราคา: {e}")
