const sendBtn = document.getElementById("send");
const essayInput = document.getElementById("essay");

const resultsDiv = document.getElementById("results");
const bandSpan = document.getElementById("band");
const grammarSpan = document.getElementById("grammar");
const vocabSpan = document.getElementById("vocab");
const coherenceSpan = document.getElementById("coherence");
const taskSpan = document.getElementById("task");
const highlightsList = document.getElementById("highlights");
const correctedPre = document.getElementById("corrected");
const commentP = document.getElementById("comment");

sendBtn.addEventListener("click", async () => {
    const essayText = essayInput.value.trim();
    if (!essayText) {
        alert("Lütfen essay girin.");
        return;
    }

    resultsDiv.style.display = "block";
    bandSpan.textContent = "Yükleniyor...";
    grammarSpan.textContent = "-";
    vocabSpan.textContent = "-";
    coherenceSpan.textContent = "-";
    taskSpan.textContent = "-";
    highlightsList.innerHTML = "";
    correctedPre.textContent = "";
    commentP.textContent = "Feedback alınıyor...";

    try {
        const response = await fetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ essay: essayText })
        });

        const data = await response.json();

        // Backend her zaman güvenli JSON döndürüyor
        bandSpan.textContent = data.score_band || "NA";
        grammarSpan.textContent = data.scores?.grammar ?? "-";
        vocabSpan.textContent = data.scores?.vocabulary ?? "-";
        coherenceSpan.textContent = data.scores?.coherence ?? "-";
        taskSpan.textContent = data.scores?.task ?? "-";

        highlightsList.innerHTML = "";
        if (Array.isArray(data.highlights)) {
            data.highlights.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                highlightsList.appendChild(li);
            });
        }

        correctedPre.textContent = data.corrected_essay || "";
        commentP.textContent = data.overall_comment || "";

    } catch (err) {
        bandSpan.textContent = "Hata";
        commentP.textContent = `Hata: ${err}`;
    }
});
