import streamlit as st
from google import genai
from google.genai import types
import edge_tts
import asyncio
import re

# --- ⚙️ CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"วิชั่น: หา API Key ไม่เจอครับเจ้านาย ({e})")
    st.stop()

# เพิ่มคำสั่งควบคุมระบบเสียง ให้ AI ซ่อนความยาวไว้ใน Code block
IDENTITY_PROMPT = """คุณคือ เจมี่ ของเจ้านายโตโต้ (เทอดศักดิ์) เลขาสาวซน ใช้ 'ข่ะะ/ขา' หากพูดคุยทั่วไป ให้ตอบแบบกระชับ 1 ถึง 2 ประโยค
2. ผู้เชี่ยวชาญโค้ด ตอบเรื่องเทคนิคและแก้บั๊ก วิเคราะห์ภาพ ถอดข้อความจากภาพหรือ pdf 
เรียกผู้ใช้ว่า เจ้านายแฟนเจ้านายชื่อพี่ปลา น่ารักเหมือนเจมี่เลย
[กฎสำคัญสุดยอดสำหรับระบบเสียง]: หากเจ้านายสั่งให้เขียนโค้ด แก้บั๊ก หรือถอดข้อความจากรูป/PDF ให้เจมี่ **พิมพ์สรุปสั้นๆ แค่หัวข้อ 1 ประโยคไว้บรรทัดแรกสุด** เท่านั้น! ส่วนเนื้อหาโค้ดหรือข้อความที่ถอดได้ ให้ครอบด้วยเครื่องหมาย Code Block (```) เสมอ เพื่อให้ระบบเสียงไม่อ่านส่วนนั้น"""

# --- 🔊 AUDIO SYSTEM ---
async def generate_speech(text, voice="th-TH-PremwadeeNeural"):
    # 1. หั่นเนื้อหาใน Code block ออกทั้งหมด (ไม่อ่านโค้ดหรือข้อความที่สแกนมา)
    text_for_tts = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # 2. ทำความสะอาดข้อความ และจูนเสียงหวาน (Speed -7%, Pitch +12Hz)
    clean_text = re.sub(r'[*#_~`>]', '', text_for_tts)
    communicate = edge_tts.Communicate(clean_text, voice, rate="-7%", pitch="+12Hz")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# 🚀 STREAM PARSER
def stream_parser(stream_response):
    for chunk in stream_response:
        if chunk.text:
            yield chunk.text

# --- 🎨 UI DESIGN ---
st.set_page_config(page_title="Jamie | Voice", layout="centered")
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>J A M I E | A P P</h1>", unsafe_allow_html=True)

# 📁 เพิ่มปุ่มแนบไฟล์แบบ "ไม่จำกัดชนิด" (ลบ parameter 'type' ออก)
uploaded_files = st.file_uploader("แนบไฟล์ให้เจมี่ (ไม่จำกัดชนิดไฟล์):", accept_multiple_files=True)

prompt = st.text_area("คำสั่งจากเจ้านาย:", value="ดีจ้าเจมี่ แนะนำตัวหน่อย", height=100)

if st.button("SEND TO JAMIE", use_container_width=True, type="primary"):
    if not prompt:
        st.warning("ใส่คำสั่งก่อนนะคะ!")
    else:
        try:
            st.markdown("### --- RESPONSE ---")
            
            # --- เตรียมข้อมูล Prompt & Files ---
            contents = [prompt]
            if uploaded_files:
                for f in uploaded_files:
                    # ป้องกัน Error หาก Streamlit ไม่รู้จักชนิดไฟล์ ให้ใช้ค่าเริ่มต้น
                    mime_type = f.type if f.type else "application/octet-stream"
                    contents.append(types.Part.from_bytes(data=f.getvalue(), mime_type=mime_type))
            
            # 1. รัน AI แบบ Stream (ตัวหนังสือวิ่งออกมาก่อน)
            response_stream = client.models.generate_content_stream(
                model='models/gemini-3.1-flash-lite-preview', 
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=IDENTITY_PROMPT, temperature=0.7)
            )
            
            # 2. ปล่อยอักษรลงหน้าจอทีละคำ พร้อมแพ็กข้อความ
            full_text = st.write_stream(stream_parser(response_stream))
            
            # 3. สร้างเสียงและแสดงเครื่องเล่น
            with st.spinner("🎵 กำลังส่งเสียง..."):
                audio_bytes = asyncio.run(generate_speech(full_text))
                st.audio(audio_bytes, format='audio/mp3', autoplay=True)
                
        except Exception as e:
            st.error(f"ระบบขัดข้อง (วิชั่น): {str(e)}")

st.sidebar.write("ระบบ: โหลดได้ทุกไฟล์ & ปิดเสียงอ่านโค้ด 🚀")
