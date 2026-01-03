import streamlit as st
import google.generativeai as genai
import time
import re

st.set_page_config(page_title="مترجم Gemini الحذر", page_icon="⚖️")
st.title("⚖️ تعريب SRT هادئ ومستقر (Gemini)")

# إدخال مفتاح Gemini
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

def fix_direction(text):
    rlm = "\u200F"
    return '\n'.join([rlm + l if re.search(r'[\u0600-\u06FF]', l) else l for l in text.split('\n')])

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    file = st.file_uploader("ارفع ملف SRT", type=['srt'])
    
    if file and st.button("ابدأ التعريب (بطيء ومضمون)"):
        content = file.getvalue().decode("utf-8", errors="replace")
        blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
        
        translated_content = []
        progress_bar = st.progress(0)
        status = st.empty()
        
        # حجم الدفعة: 10 كتل فقط كما طلبت
        chunk_size = 10 
        total = len(blocks)

        for i in range(0, total, chunk_size):
            chunk = "\n\n".join(blocks[i:i+chunk_size])
            
            success = False
            for attempt in range(3):
                try:
                    prompt = f"Translate the following SRT subtitles to cinematic Arabic. Keep timestamps and numbers. Output ONLY the translated SRT:\n\n{chunk}"
                    response = model.generate_content(prompt)
                    
                    if response and response.text:
                        translated_content.append(fix_direction(response.text))
                        success = True
                        break
                except Exception as e:
                    if "429" in str(e): # تجاوز الحد
                        status.warning(f"⚠️ تجاوزنا السرعة.. سأنتظر 30 ثانية (كتلة {i})")
                        time.sleep(30)
                    else:
                        time.sleep(5)
            
            if not success:
                translated_content.append(chunk) # إضافة النص الأصلي في حال الفشل التام
            
            # تحديث التقدم وانتظار إلزامي لراحة السيرفر
            progress_bar.progress(min((i + chunk_size) / total, 1.0))
            status.text(f"⏳ تمت معالجة {min(i+chunk_size, total)} من {total}...")
            time.sleep(6) # انتظار 6 ثوانٍ بين كل 10 كتل لضمان الاستقرار

        st.success("✅ اكتمل التعريب بنجاح!")
        st.download_button("تحميل الملف", "\n\n".join(translated_content), "translated_gemini.srt")
else:
    st.info("💡 ضع مفتاح Gemini API للبدء.")
  
