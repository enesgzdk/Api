const submitBtn = document.getElementById("submitBtn");
const essayInput = document.getElementById("essayInput");
const feedbackContainer = document.getElementById("feedbackContainer");

submitBtn.addEventListener("click", async () => {
    const essayText = essayInput.value.trim();
    if (!essayText) {
        alert("Lütfen essay girin.");
        return;
    }

    feedbackContainer.innerHTML = "Feedback alınıyor...";

    try {
        const response = await fetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ essay: essayText })
        });

        const data = await response.json();

        // Her zaman backend JSON döndürüyor → JSON.parse hatası yok
        feedbackContainer.innerHTML = `
            <h2>Feedback:</h2>
            <p>${data.overall_comment.replace(/\n/g, "<br>")}</p>
        `;
    } catch (err) {
        feedbackContainer.innerHTML = `<p style="color:red;">Hata: ${err}</p>`;
    }
});
