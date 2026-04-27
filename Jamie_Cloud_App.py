import streamlit as st
from google import genai
from google.genai import types

# --- ⚙️ CONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"หา API Key ไม่เจอค่ะเจ้านาย: {e}")
    st.stop()

# 🧠 SYSTEM INSTRUCTION: ระบุตัวตน J.A.V.I.S. V3
IDENTITY_PROMPT = """คุณคือ J.A.V.I.S. ของเจ้านายโตโต้ (เทอดศักดิ์) มี 2 ตัวตน:
1. เจมี่: เลขาสาวซน ใช้ 'คะ/ขา' ตอบเรื่องทั่วไปและวิเคราะห์ภาพ
2. วิชั่น: ผู้เชี่ยวชาญโค้ด ใช้ 'ครับ' ตอบเรื่องเทคนิคและแก้บั๊ก
"""

# --- 🎨 UI DESIGN (Minimal Style) ---
st.set_page_config(page_title="Jamie | J.A.V.I.S.", layout="centered")
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>J A M I E | A P P</h1>", unsafe_allow_html=True)

# 📁 ส่วนเลือกไฟล์ (รองรับหลายไฟล์)
uploaded_files = st.file_uploader("ส่งรูปให้เจมี่ดูหน่อยค่ะ:", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 💬 ส่วนป้อนคำสั่ง
prompt = st.text_area("คำสั่งจากเจ้านายโตโต้:", value="ดีจ้าเจมี่ ช่วยดูรูปนี้หน่อย", height=100)

if st.button("EXECUTE COMMAND", use_container_width=True, type="primary"):
    if not prompt:
        st.warning("ใส่คำสั่งก่อนค่ะเจ้านาย!")
    else:
        with st.spinner("..J.A.V.I.S. Processing.."):
            try:
                # เตรียมข้อมูลสำหรับส่ง (Text + Images)
                contents = [prompt]
                if uploaded_files:
                    for f in uploaded_files:
                        img_part = types.Part.from_bytes(data=f.getvalue(), mime_type=f.type)
                        contents.append(img_part)
                
                # 🚀 เรียกใช้โมเดล (ใช้รุ่นที่นิ่งที่สุดเพื่อลด 503)
                response = client.models.generate_content(
                    model='models/gemini-3.1-flash-lite-preview', # วิชั่นแนะนำรุ่นนี้ครับ นิ่งและไวมาก
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=IDENTITY_PROMPT,
                        temperature=0.7
                    )
                )
                
                st.markdown("### --- RESPONSE ---")
                st.write(response.text)
                
            except Exception as e:
                if "503" in str(e):
                    st.error("⚠️ วิชั่นรายงาน: Google ดีดคำขอ (503) เจ้านายลองกดส่งใหม่อีกรอบนะค!")
                else:
                    st.error(f"ระบบขัดข้อง: {str(e)}")

st.sidebar.write(f"Status: Connected ✅")
st.sidebar.info("ติดตั้งเป็นแอป: เปิดในมือถือ > กด Share > Add to Home Screen")
