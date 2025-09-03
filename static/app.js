const sendBtn = document.getElementById("send");
const essayEl = document.getElementById("essay");
const resultBox = document.getElementById("result");
const feedbackP = document.getElementById("feedback");

sendBtn.addEventListener("click", async () => {
  const essay = (essayEl.value || "").trim();
  if (!essay) {
    alert("Lütfen essay girin.");
    return;
  }

  resultBox.style.display = "block";
  feedbackP.textContent = "Feedback alınıyor...";

  try {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ essay })
    });

    // Backend her durumda JSON döndürüyor
    const data = await res.json();
    const text = data.feedback || "Feedback alınamadı.";
    // Satır sonlarını koru
    feedbackP.innerHTML = String(text).replace(/\n/g, "<br>");
  } catch (err) {
    feedbackP.textContent = "Hata: " + err;
  }
});
