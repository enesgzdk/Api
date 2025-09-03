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

    # Türkçe ve tek seferde feedback
    prompt = f"""
Sen bir akademik yazı öğretmenisin. Aşağıdaki essay’i BUEPT WRITING MARKING SCHEME’e göre değerlendir. 
Geri bildirimi **Türkçe** olarak ver, tek seferde, parça parça bölmeden, bütün metin halinde.

BUEPT WRITING MARKING SCHEME
 
E – EXCELLENT: The writer develops the topic fully with systematic discussion and sophisticated argumentation and he or she is able to develop a personal stance communicating degrees of emotion, importance, conviction, etc. in an effective style. The essay is effectively organised and coherent with a sound logical structure and connections. Organisation naturally flows from the ideas and contributes to the effectiveness of the discussion. The language is marked with fluency and accuracy showing that the writer has a firm control and flexible use of complex structures and a wide range of vocabulary. The essay is free of errors except for very minor, negligible slips. The overall impression is of someone who is in total command of language.
 
VG – VERY GOOD ACADEMIC ENGLISH: The writer develops the topic with extended argumentation and support, and he or she is able to elaborate on and highlight the significance of certain points in a fluent style. The essay is effectively organised and coherent with a sound logical structure and connections. The writer uses complex structures and a range of vocabulary items and related word forms effectively with only occasional errors in word choice and collocations and typical lapses in grammatical forms (i.e.: articles). Overall impression is of someone in almost total command of the language.
 
MA – CLEARLY MORE THAN ADEQUATE: The writer addresses the task and develops the topic by providing support with additional ideas and examples. The essay has a clear organisational structure; paragraphs have inner coherence and the argumentation flows logically throughout the essay. The language exhibits a blend of simple and complex sentences with a few possible lapses in more complex structures. The writer can use task-specific vocabulary adequately although there may be some collocation errors. There may be a few language errors but meaning is never obscured. Overall impression is of someone using the language competently without difficulty.
 
A – ADEQUATE FOR UNIVERSITY STUDY: The writer addresses the task and develops the topic as specified by providing adequate elaboration and examples to the points given in the task. The essay has a clear, logical organization presenting each aspect in separate paragraphs. There might be slight coherence problems at paragraph level but no irrelevant arguments or digressions. The language may be mostly simple but almost fully correct or it may contain more complex structures with some errors. The essay has frequent error-free sentences and the writer exhibits some competence in handling complex structures. There is limited range of vocabulary with occasional collocation errors; however the range of vocabulary is adequate to express ideas in an intelligible manner and the writer is able to use a range of vocabulary other than the ones given in the task. There is almost no interference with meaning.  No difficulty is experienced by the reader. Overall impression is of someone who writes competently but within a limited range of language.  Assign this score if you think this essay should pass.
 
D – DOUBTS ABOUT ADEQUACY: The writer addresses the task and provides generally relevant and adequate content. However, some of the points may be supported with only simple arguments or may be inadequately developed. On the whole, the writing demonstrates an adequately developed organisational structure, though there may occasionally be a lack of clarity or consistency. The writer can handle only simple sentences with ease; there may be some errors at complex sentences. The writer uses limited range of task-related vocabulary with some cases of wrong word choice and collocation problems and cannot comfortably extend the vocabulary given in the task. Errors, on the whole, do not interfere with meaning although there may be cases of slight lack of clarity. However, overall impression is of someone who falls just short of competence and who needs a short training in Advanced English to be able to cope with freshman level writing demands. Assign this score if you cannot decide whether this essay should pass or not.
 
NA – NOT ADEQUATE: The writer doesn’t address all of the writing task, or cannot develop ideas beyond the prompts/guidelines given, just replicates and repeats the same concepts in a simplistic manner. The essay may have some surface organisation. However, there may be paragraphing problems such as too long an introduction, comparatively short developmental paragraphs or problems in paragraph unity. Ideas may not logically follow each other. At points, the language is marked with major sentence structure problems such as frequent run-ons, word order problems, S-V and tense disagreement and sentence fragments. There are frequent errors in word choice and collocations. Errors impede meaning at points. In parts the text is incomprehensible.  Overall impression is of someone using the language with difficulty.  Assign this score if you think this essay cannot pass.
 
A text which mostly consists of rote-learned introduction and conclusion sentences and memorized pat phrases, clichés - such as typical sentence openings, empty sentences such as ‘Government has to take necessary precautions’ - and presents no genuine argumentation in adequate length can only achieve this level.
 
FBA – FAR BELOW ADEQUACY: The writer fails to address the task or addresses it in a very limited way by producing only simple messages or unintelligible discussion. The essay lacks any identifiable organisation. Coherence is seriously disrupted. The reader may find it very difficult to follow the flow of ideas in the essay. The language is frequently unintelligible due to frequent errors in sentence structure and vocabulary. Overall impression is of someone using the language with great difficulty.  
 
INS – INSUFFICIENT: A text consisting of only a few lines which does not provide enough output for the rater to evaluate.
 
A text which is completely off-topic and/or clearly rote-learned can only achieve this level.
 
WN – WROTE NOTHING: No text.  Just the candidate’s name appears on the paper.
 
ABS – ABSENT 
 
• The essays that go off-topic only at a certain point should be assigned a score that is one band lower than the score the essay would get otherwise.
 
• The essays that are shorter than the expected length (an essay that is only half a page instead of one full page, an essay that lacks a paragraph, or 50-60 words shorter than the required length) should be assigned a score that is one band lower than the score the essay would get otherwise.

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

        # Direkt feedback metni JSON içinde
        return jsonify({"feedback": feedback_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
