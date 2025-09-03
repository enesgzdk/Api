document.getElementById("send").onclick = async () => {
  const essay = document.getElementById("essay").value.trim();
  if (!essay) { alert("Essay boş!"); return; }

  const resultsDiv = document.getElementById("results");
  resultsDiv.classList.add("hidden");
  document.getElementById("band").textContent = "İşleniyor...";
  
  try {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({essay})
    });
    const data = await res.json();
    const parsed = data.parsed;

    if (!parsed) {
      alert("Feedback alınamadı. Model JSON döndürmedi.");
      return;
    }

    // Score & Band
    document.getElementById("band").textContent = parsed.score_band;
    document.getElementById("grammar").textContent = parsed.scores.grammar;
    document.getElementById("vocab").textContent = parsed.scores.vocabulary;
    document.getElementById("coherence").textContent = parsed.scores.coherence;
    document.getElementById("task").textContent = parsed.scores.task;

    // Highlights
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

    // Corrected Essay
    document.getElementById("corrected").textContent = parsed.corrected_essay || "Düzeltme yok.";

    // Overall Comment
    document.getElementById("comment").textContent = parsed.overall_comment || "Yorum yok.";

    resultsDiv.classList.remove("hidden");

  } catch (e) {
    alert("Hata: " + e.toString());
  }
};
