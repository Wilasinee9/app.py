import streamlit as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="US Stock Analysis Bot", layout="wide")
st.title("🇺🇸 US Stock Analysis Dashboard (แนวรับ-แนวต้าน & กราฟ)")
st.write("ดึงข้อมูลหุ้นสหรัฐฯ เรียลไทม์ พร้อมคำนวณจุดซื้อ-ขายทางเทคนิค")

# ส่วนรับค่าจากผู้ใช้
st.sidebar.header("ตั้งค่าการค้นหา")
ticker = st.sidebar.text_input("ใส่ชื่อหุ้นสหรัฐฯ (เช่น AAPL, TSLA, NVDA):", value="AAPL").upper()
period = st.sidebar.selectbox("ช่วงเวลาย้อนหลัง:", ["3mo", "6mo", "1y", "2y"], index=2)

if ticker:
    try:
        # ดึงข้อมูลจาก Yahoo Finance
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            st.error("ไม่พบข้อมูลหุ้นนี้ กรุณาตรวจสอบตัวย่อหุ้นอีกครั้ง")
        else:
            # คำนวณแนวรับ-แนวต้านอย่างง่าย (Pivot Points & Local Min/Max)
            # ในที่นี้ใช้ High/Low/Close ของรอบล่าสุดมาหา Pivot Points
            last_close = df['Close'].iloc[-1]
            high_max = df['High'].max()
            low_min = df['Low'].min()
            
            # คำนวณแบบ Support/Resistance ทั่วไปจากข้อมูลย้อนหลัง
            resistance = df['High'].rolling(window=20).max().iloc[-1]
            support = df['Low'].rolling(window=20).min().iloc[-1]
            
            # ส่วนแสดงผลสรุปราคา
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
