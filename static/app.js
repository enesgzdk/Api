document.getElementById("send").onclick = async () => {
    const essay = document.getElementById("essay").value.trim();
    if (!essay) { alert("Essay boş!"); return; }

    const resultsDiv = document.getElementById("results");
    resultsDiv.style.display = "none";
    document.getElementById("band").textContent = "İşleniyor...";

    try {
        const res = await fetch("/api/feedback", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({essay})
        });
        const data = await res.json();

        // JSON parse güvenli
        let parsed = data.parsed;
        if (!parsed) {
            // Model JSON vermezse, regex ile JSON bulmaya çalış
            const match = /(\{.*\})/s.exec(data.raw);
            if (match) {
                try { parsed = JSON.parse(match[1]); } 
                catch(e) { parsed = null; }
            }
        }

        if (!parsed) {
            alert("Feedback alınamadı. Model geçerli JSON döndürmedi.");
            return;
        }

        // Sonuçları ekrana yaz
        document.getElementById("band").textContent = parsed.score_band || "-";
        document.getElementById("grammar").textContent = parsed.scores?.grammar ?? "-";
        document.getElementById("vocab").textContent = parsed.scores?.vocabulary ?? "-";
        document.getElementById("coherence").textContent = parsed.scores?.coherence ?? "-";
        document.getElementById("task").textContent = parsed.scores?.task ?? "-";

        const highlightsList = document.getElementById("highlights");
        highlightsList.innerHTML = "";
        if (parsed.highlights && parsed.highlights.length > 0) {
            parsed.highlights.forEach(h => {
                const li = document.createElement("li");
                li.textContent = `Sentence ${h.sentence_index}: ${h.issue} → ${h.suggestion}`;
                highlightsList.appendChild(li);
            });
        } else {
            highlightsList.innerHTML = "<li>Öneri yok.</li>";
        }

        document.getElementById("corrected").textContent = parsed.corrected_essay || "Düzeltme yok.";
        document.getElementById("comment").textContent = parsed.overall_comment || "Yorum yok.";

        resultsDiv.style.display = "block";

    } catch (e) {
        alert("Hata: " + e.toString());
    }
};
