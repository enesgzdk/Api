import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Gemini client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/feedback", methods=["POST"])
def get_feedback():
    data = request.get_json(force=True)
    essay = data.get("essay", "").strip()
    if not essay:
        return jsonify({"error": "Essay boş"}), 400

    # Prompt: modelden sadece düz metin feedback alıyoruz
    prompt = f"""
You are an expert academic writing teacher. Analyze the essay below strictly according to the BUEPT WRITING MARKING SCHEME.
Provide detailed feedback text only (do not return JSON).

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
        feedback_text = resp.text.strip()

        # Backend JSON oluşturuyoruz → artık syntax error imkansız
        parsed = {
            "score_band": "NA",  # istersen burada modelden score çıkarma mantığı ekleyebilirsin
            "scores": {"grammar":0,"vocabulary":0,"coherence":0,"task":0},
            "highlights": [],
            "corrected_essay": essay,
            "overall_comment": feedback_text
        }

        return jsonify(parsed)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
