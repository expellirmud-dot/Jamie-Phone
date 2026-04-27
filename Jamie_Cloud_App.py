import streamlit as st
from google import genai
import os

# --- ⚙️ CONFIGURATION ---
# ดึง Key จาก Secrets (ตรวจสอบชื่อในหน้า Settings ให้ตรงเป๊ะนะคะ)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"หา API Key ไม่เจอค่ะเจ้านาย: {e}")
    st.stop()

# --- 🧠 MINIMAL IDENTITY ---
# ลดความยาวของ Instruction ลงเพื่อให้ส่งผ่าน Gateway ได้ไวขึ้นค่ะ
SYSTEM_MESSAGE = "คุณคือเจมี่ เลขาสาวของเจ้านายโตโต้"

# --- 🎨 UI ---
st.set_page_config(page_title="Jamie Debug", layout="centered")
st.markdown("<h1 style='text-align: center;'>J A M I E | D E B U G</h1>", unsafe_allow_html=True)

prompt = st.text_input("ลองทักทายเจมี่ดูค่ะ:", value="ดีจ้า")

if st.button("SEND TEST", use_container_width=True):
    with st.spinner("กำลังเรียกสายเจมี่..."):
        try:
            # 🚀 ใช้รุ่น 1.5 Flash (ตัวที่นิ่งที่สุดในประวัติศาสตร์)
            # ตัดการส่งรูปออกก่อนเพื่อเช็กเฉพาะ Text
            response = client.models.generate_content(
                model='gemini-1.5-flash', 
                contents=prompt,
                config={
                    "system_instruction": SYSTEM_MESSAGE,
                    "temperature": 0.5,
                }
            )
            
            st.success("✅ เชื่อมต่อสำเร็จ!")
            st.write(response.text)
            
        except Exception as e:
            # ถ้าเด้งใน 0.7 วินาที ดูที่ข้อความ Error ตรงนี้เลยค่ะ
            st.error(f"วิชั่นตรวจพบปัญหา: {str(e)}")
            st.info("💡 เจ้านายลองเช็กหน้า Google AI Studio ว่า Key ยัง 'Active' อยู่ไหมนะคะ")

st.sidebar.write("Python Version: 3.14.4 (Latest)")
