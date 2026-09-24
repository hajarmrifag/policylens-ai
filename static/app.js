const documentsEl = document.querySelector("#documents");
const docCountEl = document.querySelector("#doc-count");
const fileInput = document.querySelector("#file-input");
const dropZone = document.querySelector("#drop-zone");
const uploadStatus = document.querySelector("#upload-status");
const questionEl = document.querySelector("#question");
const askButton = document.querySelector("#ask-button");
const emptyState = document.querySelector("#empty-state");
const resultEl = document.querySelector("#result");

const escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;").replaceAll('"', "&quot;");

async function loadDocuments() {
  const response = await fetch("/documents");
  const { documents } = await response.json();
  docCountEl.textContent = `${documents.length} ${documents.length === 1 ? "doc" : "docs"}`;
  documentsEl.innerHTML = documents.map((doc) => `
    <div class="document"><span class="file-icon">${doc.name.split(".").pop().toUpperCase()}</span>
      <div><strong title="${escapeHtml(doc.name)}">${escapeHtml(doc.name)}</strong>
      <small>${doc.chunks} evidence chunks · ${(doc.characters / 1000).toFixed(1)}k chars${doc.is_demo ? " · demo" : ""}</small></div>
    </div>`).join("");
}

async function uploadFiles(files) {
  for (const file of files) {
    uploadStatus.textContent = `Indexing ${file.name}…`;
    const form = new FormData();
    form.append("file", file);
    const response = await fetch("/documents", { method: "POST", body: form });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Upload failed");
  }
  uploadStatus.textContent = `${files.length} document${files.length === 1 ? "" : "s"} ready for questions.`;
  await loadDocuments();
}

fileInput.addEventListener("change", () => uploadFiles([...fileInput.files]).catch(showError));
["dragenter", "dragover"].forEach((event) => dropZone.addEventListener(event, (e) => { e.preventDefault(); dropZone.classList.add("dragging"); }));
["dragleave", "drop"].forEach((event) => dropZone.addEventListener(event, (e) => { e.preventDefault(); dropZone.classList.remove("dragging"); }));
dropZone.addEventListener("drop", (e) => uploadFiles([...e.dataTransfer.files]).catch(showError));
document.querySelectorAll(".suggestions button").forEach((button) => button.addEventListener("click", () => { questionEl.value = button.textContent; questionEl.focus(); }));
questionEl.addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key === "Enter") askQuestion(); });
askButton.addEventListener("click", askQuestion);

async function askQuestion() {
  const question = questionEl.value.trim();
  if (question.length < 3) { questionEl.focus(); return; }
  askButton.disabled = true;
  askButton.querySelector("span").textContent = "Tracing evidence…";
  try {
    const response = await fetch("/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Question failed");
    renderAnswer(data);
  } catch (error) { showError(error); }
  finally { askButton.disabled = false; askButton.querySelector("span").textContent = "Ask PolicyLens"; }
}

function renderAnswer(data) {
  emptyState.hidden = true;
  resultEl.hidden = false;
  const status = document.querySelector("#answer-status");
  const refused = data.status === "insufficient_evidence";
  status.textContent = refused ? "Insufficient evidence" : "Grounded answer";
  status.classList.toggle("refused", refused);
  document.querySelector("#answer-meta").textContent = `${Math.round(data.confidence * 100)}% top match · ${data.latency_ms} ms`;
  document.querySelector("#answer").textContent = data.answer;
  document.querySelector("#sources").innerHTML = data.sources.map((source, index) => `
    <article class="source"><span class="source-number">0${index + 1}</span><p>${escapeHtml(source.text)}</p>
      <div class="source-meta"><span>${escapeHtml(source.document_name || "Document")}</span><span>${Math.round(source.relevance_score * 100)}% relevant</span></div>
      <div class="score-bar"><i style="width:${Math.max(0, Math.min(100, source.relevance_score * 100))}%"></i></div>
    </article>`).join("");
  resultEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function showError(error) { uploadStatus.textContent = error.message || String(error); }
loadDocuments().catch(showError);
