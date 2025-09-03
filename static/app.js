const sendBtn = document.getElementById("send");
const essayInput = document.getElementById("essay");
const resultsDiv = document.getElementById("results");
const commentP = document.getElementById("comment");

sendBtn.addEventListener("click", async () => {
    const essayText = essayInput.value.trim();
    if (!essayText) {
        alert("Lütfen essay girin.");
        return;
    }

    resultsDiv.style.display = "block";
    commentP.textContent = "Feedback alınıyor...";

    try {
        const response = await fetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ essay: essayText })
        });

        const data = await response.json();

        commentP.innerHTML = data.feedback ? data.feedback.replace(/\n/g, "<br>") : "Feedback alınamadı.";

    } catch (err) {
        commentP.textContent = `Hata: ${err}`;
    }
});
