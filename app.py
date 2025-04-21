from flask import Flask, render_template, request
import os
import contextlib
from google import genai

#log kayıtlarını bastırma

with open(os.devnull, 'w') as devnull, contextlib.redirect_stderr(devnull):
    import google.generativeai as genai

app = Flask(__name__)


#api anahtarını çağır

genai.configure(api_key = "API KEY") 

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name = "gemini-2.0-flash",
    generation_config = generation_config
)

# Kurumsal metni dış dosyadan oku
def load_academic_prompt():
    try:
        with open("academicrise_prompt.txt", "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print("Hata:", e)
        return "Kurumsal metin yüklenemedi."

# Kurumsal metin (dosyadan okunarak alınacak)
academicrise_prompt = load_academic_prompt()

# Sohbet oturumunu başlatıyoruz (kurumsal metin arka planda kullanılacak)
chat_session = model.start_chat(history=[])

# Sohbet geçmişi (başlangıçta sadece hoş geldiniz mesajı)
conversation = [
    {"sender": "AcademicRise", "message": "🎓 AcademicRise platformuna hoş geldiniz! Size nasıl yardımcı olabilirim?"}
]

@app.route("/", methods=["GET", "POST"])
def chat():
    global conversation
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input.lower() in ["exit", "quit"]:
            conversation.append({"sender": "Sistem", "message": "Sohbet sonlandırıldı."})
            return render_template("chat.html", conversation=conversation)
        
        # Kullanıcı mesajını sohbet geçmişine ekle
        conversation.append({"sender": "Müşteri", "message": user_input})
        
        # Kullanıcının sorgusunu, kurumsal metinle birleştirerek modele gönderiyoruz
        combined_input = academicrise_prompt + "\nSoru: " + user_input
        response = chat_session.send_message(combined_input)
        
        conversation.append({"sender": "AcademicRise", "message": response.text})
    
    return render_template("chat.html", conversation=conversation)

if __name__ == "__main__":
    app.run(debug=True)