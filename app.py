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
You are an expert academic writing teacher. Analyze the essay below and respond ONLY with a valid JSON object:
{
  "scores": {"grammar": int(0-5), "vocabulary": int(0-5), "coherence": int(0-5), "task": int(0-5)},
  "highlights": [
    {"sentence_index": int, "sentence": "original sentence", "issue": "Grammar|Vocabulary|Coherence|Other", "suggestion": "short suggestion"}
  ],
  "corrected_essay": "the essay with suggested corrections applied",
  "overall_comment": "short overall feedback"
}
Essay:
---
{essay}
---
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
        )
        text = resp.text

        # JSON parse
        parsed = None
        try:
            parsed = json.loads(text)
        except Exception:
            m = re.search(r'(\{.*\})', text, re.S)
            if m:
                try:
                    parsed = json.loads(m.group(1))
                except Exception:
                    parsed = None

        return jsonify({"raw": text, "parsed": parsed})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
