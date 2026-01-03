import streamlit as st
import google.generativeai as genai
import time
import re

st.set_page_config(page_title="المترجم السينمائي - النسخة المضمونة", page_icon="🎬")
st.title("🎬 تعريب SRT (نظام المعالجة المستقلة)")

api_key = st.sidebar.text_input("Gemini API Key:", type="password")

def fix_direction(text):
    rlm = "\u200F"
    return '\n'.join([rlm + l if re.search(r'[\u0600-\u06FF]', l) else l for l in text.split('\n')])

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    file = st.file_uploader("ارفع ملف SRT", type=['srt'])
    
    if file and st.button("بدأ التعريب الآن"):
        try:
            raw_content = file.getvalue().decode("utf-8")
        except:
            raw_content = file.getvalue().decode("windows-1256", errors="replace")

        # تقسيم الملف لكتل
        blocks = raw_content.split('\n\n')
        translated_full = []
        progress = st.progress(0)
        status = st.empty()

        for i, block in enumerate(blocks):
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # فصل التوقيت والرقم عن النص المراد ترجمته
                header = lines[0] + '\n' + lines[1]
                text_to_translate = "\n".join(lines[2:])
                
                prompt = f"Translate this movie dialogue into professional, dramatic, and cinematic Arabic (Fusha). Output ONLY the translation:\n\n{text_to_translate}"
                
                try:
                    response = model.generate_content(prompt)
                    if response and response.text:
                        translated_text = fix_direction(response.text.strip())
                        translated_full.append(f"{header}\n{translated_text}")
                    else:
                        translated_full.append(block)
                except Exception as e:
                    translated_full.append(block)
                    time.sleep(5)
            else:
                translated_full.append(block)
            
            # تحديث التقدم وانتظار بسيط جداً
            progress.progress((i + 1) / len(blocks))
            status.text(f"⏳ يتم تعريب السطر {i+1} من {len(blocks)}...")
            time.sleep(2) # انتظار قليل لأن الطلب صار أصغر وأسرع

        final_srt = "\n\n".join(translated_full)
        st.subheader("معاينة الترجمة:")
        st.text_area("تأكد من وجود العربية هنا:", final_srt[:800], height=200)
        st.download_button("تحميل الملف النهائي", final_srt, file_name="translated_fixed.srt")
