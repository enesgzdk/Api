import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# API key’i ortam değişkeninden al
API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/feedback", methods=["POST"])
def get_feedback():
    if not API_KEY or not client:
        return jsonify({"feedback": "Sunucu yapılandırması eksik: GOOGLE_API_KEY tanımlı değil."}), 500

    data = request.get_json(force=True)
    essay = (data.get("essay") or "").strip()
    if not essay:
        return jsonify({"feedback": "Lütfen bir essay gönderin."}), 400

    prompt = f"""
Sen bir akademik yazı öğretmenisin. Aşağıdaki essay’i BUEPT WRITING MARKING SCHEME’e göre değerlendir.
Geri bildirimi **Türkçe** ve **tek parça bütün metin** halinde ver. Puan tablosu ya da JSON verme.

Essay:
---
{essay}
---
"""

    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            # ÖNEMLİ: max_output_tokens burada, top-level değil
            config={"max_output_tokens": 4000}
        )
        feedback_text = (getattr(resp, "text", "") or "").strip()
        if not feedback_text:
            return jsonify({"feedback": "Modelden boş yanıt geldi. Model/anahtar ayarlarını kontrol edin."}), 500

        return jsonify({"feedback": feedback_text})

    except Exception as e:
        return jsonify({"feedback": f"Hata oluştu: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
