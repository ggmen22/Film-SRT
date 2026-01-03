import streamlit as st
import google.generativeai as genai
import time
import re

st.set_page_config(page_title="المترجم الاحترافي", page_icon="🎬")
st.title("🎬 تعريب SRT (نسخة Gemini المضمونة)")

api_key = st.sidebar.text_input("Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    file = st.file_uploader("ارفع ملف SRT", type=['srt'])
    
    if file and st.button("ابدأ التعريب"):
        # محاولة قراءة الملف بترميزات مختلفة لضمان قراءة النص
        try:
            raw_content = file.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            raw_content = file.getvalue().decode("windows-1256", errors="replace")

        # تقسيم النص لأسطر بدلاً من كتل معقدة لضمان عدم تخطي أي شيء
        lines = raw_content.splitlines()
        if not lines:
            st.error("الملف فارغ أو لم يتم قراءته بشكل صحيح!")
        else:
            translated_lines = []
            progress_bar = st.progress(0)
            status = st.empty()
            
            # نرسل 15 سطر في المرة (حوالي 3-4 جمل حوارية)
            chunk_size = 15
            for i in range(0, len(lines), chunk_size):
                chunk = "\n".join(lines[i:i+chunk_size])
                
                # نترجم فقط إذا كان السطر يحتوي على كلام (ليس أرقاماً أو توقيتاً)
                if re.search('[a-zA-Z]', chunk):
                    try:
                        prompt = f"Translate the dialogue in this SRT text to natural Arabic. Keep the timestamps and indices exactly as they are. Output ONLY the SRT content:\n\n{chunk}"
                        response = model.generate_content(prompt)
                        translated_lines.append(response.text if response.text else chunk)
                        time.sleep(4) # انتظار لراحة السيرفر
                    except:
                        translated_lines.append(chunk)
                else:
                    translated_lines.append(chunk)
                
                progress_bar.progress(min((i + chunk_size) / len(lines), 1.0))
                status.text(f"⏳ معالجة السطر {i} من {len(lines)}")

            final_srt = "\n".join(translated_lines)
            
            # معاينة صغيرة للتأكد من الترجمة
            st.subheader("معاينة الترجمة:")
            st.text_area("أول 500 حرف من الملف المعرب:", final_srt[:500], height=150)
            
            st.success("✅ اكتمل العمل!")
            st.download_button("تحميل الملف المعرب الآن", data=final_srt, file_name="translated_movie.srt")
else:
    st.info("💡 أدخل مفتاح Gemini API للبدء.")
  
