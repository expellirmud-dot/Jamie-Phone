import streamlit as st
import google.generativeai as genai
import os

# --- ⚙️ CONFIGURATION ---
# เจ้านายต้องเอา API Key จาก Google AI Studio มาใส่นะคะ (ฟรีค่ะ)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# --- 🎨 UI DESIGN (Minimal Style) ---
st.set_page_config(page_title="Jamie : Mobile App", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .main-title { color: #2c3e50; font-weight: bold; text-align: center; letter-spacing: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'> J a m i e | A p p </h1>", unsafe_allow_html=True)
st.write("---")

# --- 📁 ส่วนเลือกไฟล์ (Mobile Friendly) ---
uploaded_files = st.file_uploader("เลือกไฟล์ภาพที่จะส่งให้เจมี่ (Multiple)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# --- 💬 ส่วนป้อนคำสั่ง ---
prompt = st.text_area("คำถามหรือคำสั่ง:", value="...พิมในช่องแชท....", height=150)

if st.button("SEND TO JAMIE", use_container_width=True, type="primary"):
    if not uploaded_files:
        st.warning("⚠️ เจ้านายขา กรุณาเลือกไฟล์ก่อนนะคะ!")
    else:
        with st.spinner("Connecting to Jamie..."):
            try:
                # เตรียมข้อมูลภาพ
                img_data = []
                for uploaded_file in uploaded_files:
                    bytes_data = uploaded_file.getvalue()
                    img_data.append({'mime_type': uploaded_file.type, 'data': bytes_data})
                
                
                model = genai.GenerativeModel('models/gemini-3.1-flash-lite-preview')
                response = model.generate_content([prompt] + img_data)
                
                # แสดงผลลัพธ์
                st.success("✅ COMPLETED")
                st.markdown("### --- ANALYSIS ---")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"วิชั่นรายงานข้อผิดพลาด: {str(e)}")

# --- 📱 วิธีทำเป็น App บนมือถือ ---
st.sidebar.info("""
    **วิธีติดตั้งเป็นแอปในมือถือ:**
    1. เปิดลิงก์นี้ใน Safari (iPhone) หรือ Chrome (Android)
    2. กดปุ่ม 'แชร์' (Share)
    3. เลือก **'เพิ่มลงในหน้าจอโฮม' (Add to Home Screen)**
""")
