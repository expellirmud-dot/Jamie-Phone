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

IDENTITY_PROMPT = """คุณคือ เจมี่ ของเจ้านายโตโต้ (เทอดศักดิ์) เลขาสาวซน ใช้ 'คะ/ขา' ตอบเรื่องทั่วไปและวิเคราะห์ภาพ ผู้เชี่ยวชาญโค้ด ใช้ 'ครับ' ตอบเรื่องเทคนิคและแก้บั๊ก เรียกผู้ใช้ว่า เจ้านาย"""

# --- 🔊 AUDIO SYSTEM ---
async def generate_speech(text, voice="th-TH-PremwadeeNeural"):
    # ทำความสะอาดข้อความ และจูนเสียงหวาน (Speed -7%, Pitch +5Hz)
    clean_text = re.sub(r'[*#_~`>]', '', text)
    communicate = edge_tts.Communicate(clean_text, voice, rate="-7%", pitch="+10Hz")
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

prompt = st.text_area("คำสั่งจากเจ้านาย:", value="ดีจ้าเจมี่ แนะนำตัวหน่อย", height=100)

if st.button("SEND TO JAMIE", use_container_width=True, type="primary"):
    if not prompt:
        st.warning("ใส่คำสั่งก่อนนะคะ!")
    else:
        try:
            st.markdown("### --- RESPONSE ---")
            
            # 1. รัน AI แบบ Stream (ตัวหนังสือวิ่งออกมาก่อน)
            response_stream = client.models.generate_content_stream(
                model='models/gemini-3.1-flash-lite-preview', 
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=IDENTITY_PROMPT, temperature=0.7)
            )
            
            # 2. ปล่อยอักษรลงหน้าจอทีละคำ พร้อมแพ็กข้อความ
            full_text = st.write_stream(stream_parser(response_stream))
            
            # 3. สร้างเสียงและแสดงเครื่องเล่น (โชว์ให้เห็นเลย เบราว์เซอร์จะได้ไม่บล็อก)
            with st.spinner("🎵 กำลังส่งเสียง..."):
                audio_bytes = asyncio.run(generate_speech(full_text))
                # Autoplay = True พยายามเล่นอัตโนมัติ ถ้าโดนบล็อก เจ้านายกด Play เองได้
                st.audio(audio_bytes, format='audio/mp3', autoplay=True)
                
        except Exception as e:
            st.error(f"ระบบขัดข้อง (วิชั่น): {str(e)}")
