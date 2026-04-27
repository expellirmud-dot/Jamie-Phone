import streamlit as st
from google import genai
from google.genai import types
import os

# --- ⚙️ CONFIGURATION (2026 SDK Standard) ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

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

# --- 📁 ส่วนเลือกไฟล์ ---
uploaded_files = st.file_uploader("เลือกไฟล์ภาพ (Multiple)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# --- 💬 ส่วนป้อนคำสั่ง ---
prompt = st.text_area("คำถามหรือคำสั่ง:", value="เจมี่คะ ช่วยสรุปข้อมูลจากไฟล์เหล่านี้ให้หน่อยค่ะ", height=150)

if st.button("SEND TO JAMIE", use_container_width=True, type="primary"):
    if not uploaded_files:
        st.warning("⚠️ เจ้านายขา เลือกไฟล์ก่อนนะคะ!")
    else:
        with st.spinner("Connecting to Jamie (2026 Engine)..."):
            try:
                # เตรียมข้อมูลภาพสำหรับ SDK ใหม่
                contents = [prompt]
                for uploaded_file in uploaded_files:
                    img = types.Part.from_bytes(
                        data=uploaded_file.getvalue(),
                        mime_type=uploaded_file.type
                    )
                    contents.append(img)
                
                # เรียกใช้โมเดลล่าสุด (Gemini 3 Flash)
                response = client.models.generate_content(
                    model='gemini-3-flash',
                    contents=contents
                )
                
                st.success("✅ COMPLETED")
                st.markdown("### --- ANALYSIS ---")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"วิชั่นรายงานข้อผิดพลาด: {str(e)}")

st.sidebar.info("แอปนี้รันบนก้อนเมฆ (Streamlit Cloud) สแตนด์บายรอเจ้านาย 24 ชม. ค่ะ!")
