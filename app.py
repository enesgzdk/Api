import os
import json
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Gemini istemcisi
client = genai.Client()
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

FEEDBACK_PROMPT = """
You are an expert academic writing teacher. Analyze the essay below strictly according to the BUEPT WRITING MARKING SCHEME.

Provide your evaluation in JSON format only, strictly following this schema:
{
  "score_band": "E / VG / MA / A / D / NA / FBA / INS / WN / ABS",
  "scores": {"grammar":0-5, "vocabulary":0-5, "coherence":0-5, "task":0-5},
  "highlights":[{"sentence_index":0,"sentence":"text","issue":"Grammar|Vocabulary|Coherence|Task","suggestion":"text"}],
  "corrected_essay":"text",
  "overall_comment":"text"
}

Essay:
---
{essay}
---
IMPORTANT: ONLY RETURN VALID JSON, NOTHING ELSE.
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/feedback", methods=["POST"])
def get_feedback():
    data = request.get_json(force=True)
    essay = data.get("essay", "").strip()
    if not essay:
        return jsonify({"error": "Essay boş"}), 400

    prompt = FEEDBACK_PROMPT.format(essay=essay)
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            max_output_tokens=2000  # uzun essay için yeterli
        )
        text = resp.text

        # JSON parse güvenli
        parsed = None
        try:
            parsed = json.loads(text)
        except:
            # Eğer model JSON dışında bir şey eklediyse regex ile JSON kısmını yakala
            m = re.search(r'(\{.*\})', text, re.S)
            if m:
                try:
                    parsed = json.loads(m.group(1))
                except:
                    parsed = None

        # Hala parse edilemediyse boş feedback dön
        if not parsed:
            parsed = {
                "score_band":"NA",
                "scores":{"grammar":0,"vocabulary":0,"coherence":0,"task":0},
                "highlights":[],
                "corrected_essay":"",
                "overall_comment":"JSON parse edilemedi, essay çok uzun veya format hatalı."
            }

        return jsonify({"raw": text, "parsed": parsed})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
