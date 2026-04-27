import streamlit as st
from google import genai
from google.genai import types
import os

# --- ⚙️ CONFIGURATION ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# 🧠 SYSTEM INSTRUCTION: กำหนดตัวตน เจมี่ Jamie
IDENTITY_PROMPT = """
คุณคือ เจมี่ (Jamie) ระบบปฏิบัติการอัจฉริยะของเจ้านาย  
1. เลขาสาวฉลาดซน ขี้เล่น ใช้หางเสียง 'คะ/ขา' เรียกผู้ใช้ว่า 'เจ้านาย' หน้าที่: ตอบคำถามทั่วไป, วิเคราะห์ภาพถ่าย, วางแผนงาน, คุยเล่นสร้างรอยยิ้ม
2. ผู้เชี่ยวชาญด้านโค้ดและเทคนิค หน้าที่: แก้บั๊กโค้ด Python, วิเคราะห์โครงสร้างโปรแกรม
(เจ้านายชื่อคุณโตโต้ เทอดศักดิ์ แฟนชื่อพี่ปลา)
"""

# --- 🎨 UI DESIGN (Minimal Style) ---
st.set_page_config(page_title="Jamie : J.A.V.I.S. Mobile", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f0f2f5; }}
    .main-title {{ color: #2c3e50; font-weight: bold; text-align: center; letter-spacing: 5px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'> J A M I E | A P P </h1>", unsafe_allow_html=True)
st.write(f"สวัสดีค่ะเจ้านายโตโต้! วันนี้มีอะไรให้เจมี่ช่วยไหมคะ?")

# --- 📁 ส่วนเลือกไฟล์ ---
uploaded_files = st.file_uploader("ส่งไฟล์ให้ระบบวิเคราะห์:", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# --- 💬 ส่วนป้อนคำสั่ง ---
prompt = st.text_area("คำสั่งจากเจ้านาย:", placeholder="เช่น... เจมี่ดูรูปงานแต่งนี้หน่อย หรือ วิชั่นแก้โค้ดตรงนี้ให้ที", height=120)

if st.button("SEND TO JAMIE", use_container_width=True, type="primary"):
    if not prompt:
        st.warning("⚠️ เจ้านายขา ลืมใส่คำสั่งหรือเปล่าคะ?")
    else:
        with st.spinner("..J.A.V.I.S. System Processing.."):
            try:
                contents = [prompt]
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        img = types.Part.from_bytes(
                            data=uploaded_file.getvalue(), 
                            mime_type=uploaded_file.type
                        )
                        contents.append(img)
                
                # 🚀 เรียกใช้โมเดล (แนะนำให้ใช้ gemini-3-flash-preview จะนิ่งกว่า Lite มากครับ)
                response = client.models.generate_content(
                    model='models/gemini-3.1-flash-lite-preview', 
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=IDENTITY_PROMPT,
                        temperature=0.7
                    )
                )
                st.markdown("### --- RESPONSE ---")
                st.write(response.text)
            
            except Exception as e:
                # เพิ่มตัวดักจับ 503 ให้เจ้านายเห็นชัดๆ ค่ะ
                if "503" in str(e):
                    st.error("⚠️ วิชั่นรายงาน: เซิร์ฟเวอร์ Google งานยุ่งชั่วคราว (503) เจ้านายโตโต้ลองกดส่งอีกรอบนะคะ!")
                else:
                    st.error(f"ระบบขัดข้อง (วิชั่น): {str(e)}")
