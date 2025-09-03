import os
import json
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

client = genai.Client()
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

FEEDBACK_PROMPT = """
You are an expert academic writing teacher. Analyze the essay below strictly according to the BUEPT WRITING MARKING SCHEME.

Return a valid JSON object only. Do NOT add any extra explanation or text outside JSON.
Wrap all text fields in quotes and escape newlines if needed.

Essay:
---
{essay}
---
"""

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
            max_output_tokens=2000
        )
        text = resp.text

        # JSON parse güvenli
        parsed = None
        # 1. direkt parse
        try:
            parsed = json.loads(text)
        except:
            # 2. regex ile JSON kısmını yakala
            m = re.search(r'\{.*\}', text, re.S)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except:
                    parsed = None

        # 3. hala parse edilemezse fallback
        if not parsed:
            parsed = {
                "score_band":"NA",
                "scores":{"grammar":0,"vocabulary":0,"coherence":0,"task":0},
                "highlights":[],
                "corrected_essay":"",
                "overall_comment":"Model JSON üretemedi."
            }

        return jsonify(parsed)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
