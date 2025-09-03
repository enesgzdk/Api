import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# API key kontrolü
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY ortam değişkeni tanımlı değil!")

client = genai.Client(api_key=API_KEY)
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/feedback", methods=["POST"])
def get_feedback():
    data = request.get_json(force=True)
    essay = data.get("essay", "").strip()
    if not essay:
        return jsonify({"feedback": "Essay boş gönderildi."}), 400

    prompt = f"""
Sen bir akademik yazı öğretmenisin. Aşağıdaki essay’i BUEPT WRITING MARKING SCHEME’e göre değerlendir. 
Geri bildirimi **Türkçe** olarak ver, tek seferde, parça parça bölmeden, bütün metin halinde.

Essay:
---
{essay}
---
"""

    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            max_output_tokens=2000
        )

        # Gemini'den cevap geldiyse
        feedback_text = getattr(resp, "text", "").strip()
        if not feedback_text:
            return jsonify({"feedback": "Gemini’den boş yanıt geldi, model ayarlarını kontrol et."}), 500

        return jsonify({"feedback": feedback_text})

    except Exception as e:
        return jsonify({"feedback": f"Hata oluştu: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
