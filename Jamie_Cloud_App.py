import streamlit as st
from google import genai
from google.genai import types
import edge_tts
import asyncio
import re
import base64

# --- ⚙️ CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"วิชั่น: หา API Key ไม่เจอครับเจ้านาย ({e})")
    st.stop()

IDENTITY_PROMPT = """คุณคือ J.A.V.I.S. ของเจ้านายโตโต้
1. เจมี่: เลขาสาวซน ใช้ 'คะ/ขา'
2. วิชั่น: ผู้เชี่ยวชาญโค้ด ใช้ 'ครับ'
ตอบกระชับ เป็นธรรมชาติ เพื่อแปลงเป็นเสียงพูด (TTS) ห้ามใช้เครื่องหมายพิเศษเยอะ"""

# --- 🔊 AUDIO SYSTEM ---
async def generate_speech(text, voice="th-TH-PremwadeeNeural"):
    clean_text = re.sub(r'[*#_~`>]', '', text)
    
    # 🎛️ วิชั่นปรับจูนเสียงตามคำสั่ง: Speed -7%, Pitch +5Hz
    communicate = edge_tts.Communicate(
        clean_text, 
        voice, 
        rate="-7%",     # ปรับความเร็ว (ลบคือช้าลง)
        pitch="+5Hz"    # ปรับคีย์เสียง (บวกคือเสียงสูง/หวานขึ้น)
    )
    
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# --- 🧠 JS AUDIO QUEUE ENGINE ---
# ฝัง Script ลงไปเพื่อสร้างระบบ "เข้าคิว" ไม่ให้เสียงตีกัน
JS_QUEUE = """
<script>
if (!window.parent.audioQueue) {
    window.parent.audioQueue = [];
    window.parent.isPlaying = false;
    
    window.parent.playNext = function() {
        if (window.parent.audioQueue.length > 0) {
            window.parent.isPlaying = true;
            let audio = new Audio(window.parent.audioQueue.shift());
            audio.onended = function() {
                window.parent.isPlaying = false;
                window.parent.playNext(); // เล่นคิวต่อไป
            };
            audio.play().catch(e => {
                console.log("Autoplay blocked.");
                window.parent.isPlaying = false;
                window.parent.playNext();
            });
        } else {
            window.parent.isPlaying = false;
        }
    };
    
    window.parent.enqueueAudio = function(b64) {
        window.parent.audioQueue.push("data:audio/mp3;base64," + b64);
        if (!window.parent.isPlaying) {
            window.parent.playNext();
        }
    };
}
</script>
"""

# --- 🎨 UI DESIGN ---
st.set_page_config(page_title="Jamie | Voice Stream", layout="centered")
st.markdown(JS_QUEUE, unsafe_allow_html=True) # ติดตั้งเครื่องยนต์คิวเสียง
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>J A M I E | A P P</h1>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("ส่งรูปมาเลยค่ะเจ้านาย:", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
prompt = st.text_area("คำสั่งจากเจ้านาย:", value="ดีจ้าเจมี่ แนะนำตัวยาวๆ หน่อย", height=100)

if st.button("SEND TO JAMIE", use_container_width=True, type="primary"):
    if not prompt:
        st.warning("ใส่คำสั่งก่อนนะคะ!")
    else:
        contents = [prompt]
        if uploaded_files:
            for f in uploaded_files:
                contents.append(types.Part.from_bytes(data=f.getvalue(), mime_type=f.type))
        
        st.markdown("### --- RESPONSE ---")
        
        # กล่องสำหรับแสดงข้อความแบบ Real-time
        chat_box = st.empty() 
        display_text = ""
        buffer = ""
        
        try:
            # 1. เรียกใช้งานแบบ Stream
            response_stream = client.models.generate_content_stream(
                model='gemini-2.0-flash', 
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=IDENTITY_PROMPT, temperature=0.7)
            )
            
            # 2. กระบวนการสับท่อน (Chunking) & เข้าคิว (Queuing)
            for chunk in response_stream:
                if chunk.text:
                    display_text += chunk.text
                    buffer += chunk.text
                    chat_box.markdown(display_text) # โชว์ข้อความให้เจ้านายอ่าน
                    
                    # หั่นท่อนเมื่อยาวเกิน 60 อักษร และเจอคำเว้นวรรค หรือจุดจบประโยค
                    if len(buffer) >= 60 and any(x in buffer for x in [" ", "\n", "ค่ะ", "ครับ", "!"]):
                        text_to_speak = buffer.strip()
                        buffer = "" # ล้างกระเป๋าเตรียมรับท่อนใหม่
                        
                        if text_to_speak:
                            audio_bytes = asyncio.run(generate_speech(text_to_speak))
                            b64 = base64.b64encode(audio_bytes).decode()
                            # ส่งเสียงเข้าคิว JS ทันที
                            st.markdown(f'<script>window.parent.enqueueAudio("{b64}");</script>', unsafe_allow_html=True)
            
            # เก็บตกท่อนสุดท้ายที่เหลืออยู่ในกระเป๋า
            if buffer.strip():
                audio_bytes = asyncio.run(generate_speech(buffer.strip()))
                b64 = base64.b64encode(audio_bytes).decode()
                st.markdown(f'<script>window.parent.enqueueAudio("{b64}");</script>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"ระบบขัดข้อง (วิชั่น): {str(e)}")

st.sidebar.info("📱 Note: ระบบคิวเสียง (Chunk Queue) เปิดใช้งานแล้ว!")
