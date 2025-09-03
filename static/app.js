document.getElementById("send").onclick = async () => {
  const essay = document.getElementById("essay").value.trim();
  if (!essay) { alert("Essay boş!"); return; }
  document.getElementById("out").textContent = "İşleniyor...";
  try {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({essay})
    });
    const data = await res.json();
    document.getElementById("out").textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById("out").textContent = "Hata: " + e.toString();
  }
};
