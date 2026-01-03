import streamlit as st
import google.generativeai as genai
import time
import re

st.set_page_config(page_title="المترجم السينمائي المحترف", page_icon="🎬")
st.title("🎬 تعريب SRT (الجودة الكاملة - Gemini)")

api_key = st.sidebar.text_input("Gemini API Key:", type="password")

def fix_direction(text):
    rlm = "\u200F"
    return '\n'.join([rlm + l if re.search(r'[\u0600-\u06FF]', l) else l for l in text.split('\n')])

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    file = st.file_uploader("ارفع ملف الترجمة SRT", type=['srt'])
    
    if file and st.button("ابدأ التعريب السينمائي"):
        try:
            raw_content = file.getvalue().decode("utf-8")
        except:
            raw_content = file.getvalue().decode("windows-1256", errors="replace")

        blocks = [b.strip() for b in raw_content.split('\n\n') if b.strip()]
        translated_content = []
        progress_bar = st.progress(0)
        status = st.empty()
        
        # نرسل 10 كتل للحفاظ على السياق الدرامي
        chunk_size = 10 
        for i in range(0, len(blocks), chunk_size):
            chunk = "\n\n".join(blocks[i:i+chunk_size])
            
            # الـ Prompt السينمائي الذي تريده بدون تغيير
            prompt = f"""
            You are a professional cinematic translator. 
            Translate the following SRT blocks into natural, dramatic Arabic (Fusha). 
            Keep timestamps and sequence numbers exactly as they are. 
            Output ONLY the translated SRT content.
            
            Text:
            {chunk}
            """
            
            success = False
            for attempt in range(3): # محاولة إعادة الطلب في حال الفشل
                try:
                    response = model.generate_content(prompt)
                    if response and response.text:
                        translated_content.append(fix_direction(response.text))
                        success = True
                        break
                except:
                    time.sleep(10) # انتظار طويل في حال حدوث ضغط
            
            if not success:
                translated_content.append(chunk) # حفظ الأصل إذا فشل تماماً
            
            progress_bar.progress(min((i + chunk_size) / len(blocks), 1.0))
            status.text(f"⏳ يتم الآن تعريب الكتلة {i} من {len(blocks)}...")
            time.sleep(8) # وقت كافٍ جداً للسيرفر لمعالجة الـ Prompt المعقد

        final_srt = "\n\n".join(translated_content)
        st.subheader("معاينة الترجمة الاحترافية:")
        st.text_area("تأكد من الجودة هنا:", final_srt[:1000], height=200)
        st.download_button("تحميل الملف المعرب", final_srt, file_name="movie_translated.srt")
      
