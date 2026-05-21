import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# 1. ตั้งค่าหน้าเว็บสไตล์ Modern Dark Theme
st.set_page_config(
    page_title="AlphaTrader - US Stock Technical Hub",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# สไตล์ตกแต่ง UI เพิ่มเติมด้วย CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #ffffff; }
    div[data-testid="stMetricDelta"] { font-size: 14px; }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# 2. ระบบจัดการหุ้นรายการโปรด (Watchlist) โดยใช้ Session State
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'TSLA', 'NVDA', 'MSFT']

# --- SIDEBAR: แผงควบคุมดีไซน์เน้นใช้งานง่าย ---
with st.sidebar:
    st.title("🦅 AlphaTrader")
    st.caption("ระบบวิเคราะห์หุ้นและสัญญาณเทคนิคัลอัตโนมัติ")
    st.write("---")
    
    # ส่วนของ Watchlist
    st.subheader("⭐ หุ้นรายการโปรด (Watchlist)")
    selected_watchlist = st.selectbox("เลือกจากรายการโปรด:", [""] + st.session_state.watchlist)
    
    # ส่วนค้นหาหุ้นใหม่
    st.subheader("🔍 ค้นหาหุ้นใหม่")
    search_ticker = st.text_input("ใส่ชื่อหุ้นสหรัฐฯ (Ticker):", value="AAPL" if not selected_watchlist else selected_watchlist)
    ticker = search_ticker.upper().strip()
    
    # ปุ่มเพิ่ม/ลบ หุ้นรายการโปรด
    col_add, col_del = st.columns(2)
    with col_add:
        if st.button("➕ เพิ่มในโปรด"):
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                st.rerun()
    with col_del:
        if st.button("❌ ลบจากโปรด"):
            if ticker in st.session_state.watchlist:
                st.session_state.watchlist.remove(ticker)
                st.rerun()
                
    st.write("---")
    period = st.selectbox("ช่วงเวลาย้อนหลัง (Timeframe):", ["3mo", "6mo", "1y", "2y"], index=2)

# --- MAIN CONTENT: หน้าหลักแสดงผลวิเคราะห์อย่างละเอียด ---
if ticker:
    try:
        # ดึงข้อมูลจาก Yahoo Finance
        stock = yf.Ticker(ticker)
        # ดึงเผื่อมาคำนวณอินดิเคเตอร์ย้อนหลัง
        df = stock.history(period="2y") 
        
        if df.empty:
            st.error(f"❌ ไม่พบข้อมูลสำหรับหุ้น {ticker} กรุณาตรวจสอบตัวย่ออีกครั้ง")
        else:
            # ตัดข้อมูลให้เหลือเฉพาะช่วงเวลาที่ผู้ใช้เลือกมาแสดงผล
            if period == "3mo": df_view = df.tail(63)
            elif period == "6mo": df_view = df.tail(126)
            elif period == "1y": df_view = df.tail(252)
            else: df_view = df
            
            # --- 3. คำนวณอินดิเคเตอร์ทางเทคนิคอย่างละเอียด ---
            # เส้นค่าเฉลี่ย EMA 20 และ EMA 50
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            
            # คำนวณ RSI (14 วัน)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # คำนวณแนวรับ-แนวต้านย้อนหลัง 20 วัน
            resistance = df_view['High'].max()
            support = df_view['Low'].min()
            
            # ค่าล่าสุดที่จะนำมาแสดงผล
            last_close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            price_change = last_close - prev_close
            pct_change = (price_change / prev_close) * 100
            last_rsi = df['RSI'].iloc[-1]
            last_ema20 = df['EMA20'].iloc[-1]
            last_ema50 = df['EMA50'].iloc[-1]

            # --- 4. ระบบวิเคราะห์และประเมินสัญญาณ ซื้อ/ขาย (Action Engine) ---
            # เกณฑ์การตัดสินใจ: ผสมผสาน ราคาใกล้แนวรับต้าน + สัญญาณ RSI และ EMA
            score = 0 
            reasons = []
            
            # เช็คระยะห่างแนวรับ/แนวต้าน
            if (last_close - support) / support < 0.02: # ใกล้แนวรับน้อยกว่า 2%
                score += 2
                reasons.append("ราคาลงมาใกล้แนวรับสำคัญ มีโอกาสเด้งกลับ")
            elif (resistance - last_close) / last_close < 0.02: # ใกล้แนวต้านน้อยกว่า 2%
                score -= 2
                reasons.append("ราคาขึ้นมาใกล้แนวต้านสำคัญ ระวังแรงเทขายทำกำไร")
                
            # เช็คความแข็งแกร่งของเทรนด์ (EMA)
            if last_close > last_ema20 > last_ema50:
                score += 1
                reasons.append("ราคาอยู่ในแนวโน้มขาขึ้น (Bullish Trend)")
            elif last_close < last_ema20 < last_ema50:
                score -= 1
                reasons.append("ราคาอยู่ในแนวโน้มขาลง (Bearish Trend)")
                
            # เช็คโมเมนตัม (RSI)
            if last_rsi < 30:
                score += 2
                reasons.append("RSI บ่งบอกภาวะขายมากเกินไป (Oversold) มีโอกาสเกิด Technical Rebound")
            elif last_rsi > 70:
                score -= 2
                reasons.append("RSI บ่งบอกภาวะซื้อมากเกินไป (Overbought) เสี่ยงย่อตัวราคา")

            # สรุปคำแนะนำซื้อขายจากคะแนนสุทธิ
            if score >= 2:
                action_status = "🎯 แนะนำ: ซื้อ (STRONG BUY/ACCUMULATE)"
                action_color = "#22c55e" # สีเขียว
            elif score <= -2:
                action_status = "⚠️ แนะนำ: ขาย หรือ ลดสัดส่วน (SELL/TAKE PROFIT)"
                action_color = "#ef4444" # สีแดง
            else:
                action_status = "⏳ แนะนำ: ถือ/รอดูสถานการณ์ (HOLD/WAIT & SEE)"
                action_color = "#eab308" # สีเหลือง

            # --- ส่วนแสดงผลบนหน้าเว็บ (UX/UI Layout) ---
            st.header(f"📈 เจาะลึกหุ้น {ticker}: {stock.info.get('shortName', '')}")
            
            # โซนสรุปราคาและคำแนะนำสำคัญ (Highlight Panel)
            st.markdown(f"""
                <div style="background-color: #1e222b; padding: 20px; border-radius: 12px; border-left: 8px solid {action_color}; margin-bottom: 25px;">
                    <h3 style="margin: 0; color: {action_color};">{action_status}</h3>
                    <p style="margin: 10px 0 0 0; color: #cbd5e1; font-size: 15px;">
                        📝 <b>เหตุผลทางเทคนิค:</b> {', '.join(reasons) if reasons else 'อินดิเคเตอร์ส่วนใหญ่ยังอยู่ในโซนสมดุล ไม่มีสัญญาณที่ชัดเจน'}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # โซนตัวเลข Metrics (กว้างและเคลียร์)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("ราคาปิดปัจจุบัน", f"${last_close:.2f}", f"{price_change:+.2f} ({pct_change:+.2f}%)")
            col2.metric("🎯 แนวต้านสำคัญ", f"${resistance:.2f}", f"ห่างอีก ${(resistance - last_close):.2f}")
            col3.metric("🛡️ แนวรับสำคัญ", f"${support:.2f}", f"ห่างอีก ${(last_close - support):.2f}")
            col4.metric("📊 โมเมนตัม RSI (14)", f"{last_rsi:.1f}", "Oversold <30 | Overbought >70", delta_color="off")
            
            st.write("---")

            # --- 5. การตีกราฟวิเคราะห์ขั้นสูง (Advance Subplots) ---
            st.subheader("🔍 กราฟเทคนิคอลแบบละเอียด (Candlesticks + EMA + RSI)")
            
            # ซิงค์ข้อมูลสำหรับวาดกราฟตามช่วงเวลาที่เลือก
            df_chart = df.loc[df_view.index[0]:df_view.index[-1]]
            
            # สร้าง 2 กราฟในหน้าเดียว (บนเป็นกราฟแท่งเทียน, ล่างเป็น RSI)
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.08, 
                                row_heights=[0.7, 0.3])
            
            # 5.1 กราฟบน: แท่งเทียน + เส้นแนวรับแนวต้าน + เส้น EMA
            fig.add_trace(go.Candlestick(
                x=df_chart.index, open=df_chart['Open'], high=df_chart['High'],
                low=df_chart['Low'], close=df_chart['Close'], name="ราคา"
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA20'], line=dict(color='#60a5fa', width=1.5), name='EMA 20'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA50'], line=dict(color='#f43f5e', width=1.5), name='EMA 50'), row=1, col=1)
            
            # เส้นปะแนวรับ/แนวต้าน
            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], y=[resistance, resistance],
                mode="lines", line=dict(color="#f43f5e", width=2, dash="dash"), name="แนวต้าน"
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=[df_chart.index[0], df_chart.index[-1]], y=[support, support],
                mode="lines", line=dict(color="#34d399", width=2, dash="dash"), name="แนวรับ"
            ), row=1, col=1)

            # พลอตจุด Buy/Sell Signal บนกราฟเพื่อความสวยงามและชัดเจน
            # หาจุดที่ RSI ต่ำกว่า 30 (Buy Entry) และสูงกว่า 70 (Sell Entry) สำหรับช่วงในกราฟ
            buy_signals = df_chart[df_chart['RSI'] < 35]
            sell_signals = df_chart[df_chart['RSI'] > 65]
            
            fig.add_trace(go.Scatter(
                x=buy_signals.index, y=buy_signals['Low'] * 0.98, mode='markers',
                marker=dict(symbol='triangle-up', size=12, color='#22c55e'), name='จุดลุ้นซื้อ (RSI ต่ำ)'
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=sell_signals.index, y=sell_signals['High'] * 1.02, mode='markers',
                marker=dict(symbol='triangle-down', size=12, color='#ef4444'), name='จุดระวังขาย (RSI สูง)'
            ), row=1, col=1)

            # 5.2 กราฟล่าง: ดัชนี RSI
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['RSI'], line=dict(color='#a855f7', width=2), name='RSI'), row=2, col=1)
            # เส้นแบ่งโซน Overbought / Oversold
            fig.add_shape(type="line", x0=df_chart.index[0], x1=df_chart.index[-1], y0=70, y1=70, line=dict(color="#ef4444", width=1, dash="dot"), row=2, col=1)
            fig.add_shape(type="line", x0=df_chart.index[0], x1=df_chart.index[-1], y0=30, y1=30, line=dict(color="#22c55e", width=1, dash="dot"), row=2, col=1)
            
            # ตั้งค่าธีมและหน้าตาโดยรวมของกราฟ
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                height=700,
                margin=dict(l=50, r=50, t=30, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_yaxes(title_text="ราคา ($)", row=1, col=1)
            fig.update_yaxes(title_text="RSI Value", range=[10, 90], row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ เกิดข้อผิดพลาดในการดึงข้อมูลหรือคำนวณสูตร: {e}")            # ส่วนแสดงผลสรุปราคา
            st.subheader(f"📊 ผลวิเคราะห์หุ้น {ticker}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("ราคาปิดล่าสุด", f"${last_close:.2f}")
            col2.metric("แนวต้านสำคัญ (20 วัน)", f"${resistance:.2f}", delta=f"${resistance - last_close:.2f}", delta_color="inverse")
            col3.metric("แนวรับสำคัญ (20 วัน)", f"${support:.2f}", delta=f"${support - last_close:.2f}")
            col4.metric("ปริมาณการซื้อขาย", f"{df['Volume'].iloc[-1]:,}")

            # สรุปคำแนะนำแบบง่าย
            st.info(f"💡 **มุมมองทางเทคนิค:** ปัจจุบันราคาปิดที่ **${last_close:.2f}** หากราคาทะลุแนวต้านที่ **${resistance:.2f}** จะมีแนวโน้มขาขึ้นต่อ แต่หากหลุดแนวรับที่ **${support:.2f}** ควรระมัดระวังแรงเทขาย")

            # --- ส่วนการวาดกราฟ (Plotly Candlestick) ---
            st.subheader("📈 กราฟเทคนิคัลแนวรับ-แนวต้าน")
            
            fig = go.Figure()
            
            # กราฟแท่งเทียน
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="ราคาหุ้น"
            ))
            
            # เส้นแนวต้าน (สีแดง)
            fig.add_trace(go.Scatter(
                x=[df.index[0], df.index[-1]],
                y=[resistance, resistance],
                mode="lines",
                line=dict(color="red", width=2, dash="dash"),
                name="แนวต้าน (Resistance)"
            ))
            
            # เส้นแนวรับ (สีเขียว)
            fig.add_trace(go.Scatter(
                x=[df.index[0], df.index[-1]],
                y=[support, support],
                mode="lines",
                line=dict(color="green", width=2, dash="dash"),
                name="แนวรับ (Support)"
            ))
            
            # ปรับแต่งหน้าตากราฟ
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                margin=dict(l=20, r=20, t=20, b=20),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # แสดงตารางข้อมูลดิบ
            with st.expander("ดูข้อมูลราคาย้อนหลังแบบละเอียด"):
                st.dataframe(df.tail(20).sort_index(ascending=False))
                
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
