/**
 * Zafra AI — Frontend
 * Conecta el formulario con la API FastAPI (texto + audio).
 */

const API_BASE_URL = APP_CONFIG.apiBaseUrl;

const form = document.getElementById("evaluacion-form");
const btnAnalizar = document.getElementById("btn-analizar");
const btnText = btnAnalizar.querySelector(".btn__text");
const btnLoader = btnAnalizar.querySelector(".btn__loader");
const toast = document.getElementById("toast");

const textoInput = document.getElementById("texto");
const btnGrabar = document.getElementById("btn-grabar");
const btnDetener = document.getElementById("btn-detener");
const btnLimpiarAudio = document.getElementById("btn-limpiar-audio");
const audioStatus = document.getElementById("audio-status");
const audioPreview = document.getElementById("audio-preview");
const audioPanel = document.getElementById("audio-panel");
const recordingIndicator = document.getElementById("recording-indicator");
const dictationBadge = document.getElementById("dictation-badge");
const dictationHint = document.getElementById("dictation-hint");

const resultCards = {
  clima: document.getElementById("card-clima"),
  recomendacion: document.getElementById("card-recomendacion"),
  explicacion: document.getElementById("card-explicacion"),
};

const resultContents = {
  clima: document.getElementById("clima-content"),
  recomendacion: document.getElementById("recomendacion-content"),
  explicacion: document.getElementById("explicacion-content"),
};

let recordedBlob = null;
let recordedMimeType = "audio/webm";
let recordedExtension = ".webm";
let audioRecorder = null;

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("toast--error", isError);
  toast.hidden = false;
  toast.classList.add("is-visible");

  setTimeout(() => {
    toast.classList.remove("is-visible");
    setTimeout(() => { toast.hidden = true; }, 300);
  }, 3500);
}

function setLoading(loading) {
  btnAnalizar.disabled = loading;
  btnText.hidden = loading;
  btnLoader.hidden = !loading;
}

function formatCultivo(value) {
  return value === "soya" ? "Soya" : "Maíz";
}

function formatTipo(value) {
  const labels = {
    siembra: "Siembra",
    fertilizacion: "Fertilización",
    riego: "Riego",
    plagas: "Plagas",
    cosecha: "Cosecha",
  };
  return labels[value] || value;
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function resetResults() {
  Object.values(resultCards).forEach((card) => {
    card.classList.remove("is-active");
    const placeholder = card.querySelector(".card__placeholder");
    if (placeholder) placeholder.hidden = false;
  });
  Object.values(resultContents).forEach((content) => {
    content.hidden = true;
    content.innerHTML = "";
  });
}

function updateAudioStatus(message) {
  audioStatus.textContent = message;
}

function setRecordingUi(active, phase) {
  const isRecording = phase === "recording";
  audioPanel?.classList.toggle("audio-panel--recording", isRecording);
  btnGrabar.classList.toggle("btn--recording", isRecording);
  btnGrabar.disabled = active;
  btnDetener.disabled = !active || phase === "processing";
  if (recordingIndicator) {
    recordingIndicator.classList.toggle("is-active", isRecording);
    recordingIndicator.hidden = !isRecording;
  }
}

function resetSavedAudio() {
  recordedBlob = null;
  recordedMimeType = "audio/webm";
  recordedExtension = ".webm";
  btnLimpiarAudio.disabled = true;
  setAudioPreview(null);
}

function setAudioPreview(blob) {
  if (!blob) {
    audioPreview.hidden = true;
    audioPreview.removeAttribute("src");
    audioPreview.removeAttribute("playsinline");
    return;
  }

  audioPreview.src = URL.createObjectURL(blob);
  audioPreview.setAttribute("playsinline", "");
  audioPreview.hidden = false;
}

function clearAudio() {
  if (audioRecorder?.isActive()) {
    audioRecorder.stop();
  }

  resetSavedAudio();
  setRecordingUi(false);
  textoInput.classList.remove("form__textarea--dictating");
  updateAudioStatus("Sin audio seleccionado.");
}

function getActiveAudioFile() {
  if (recordedBlob) {
    const filename = `nota-grabada${recordedExtension}`;
    return new File([recordedBlob], filename, {
      type: recordedMimeType || recordedBlob.type || "audio/webm",
    });
  }

  return null;
}

function updateDictationBadge(active, detail, hint) {
  if (!dictationBadge) return;

  if (detail === "unsupported") {
    dictationBadge.hidden = false;
    dictationBadge.classList.add("is-visible");
    dictationBadge.textContent = hint || "Dictado en vivo: no disponible (usá Chrome en Android/Samsung)";
    dictationBadge.className = "dictation-badge dictation-badge--warn is-visible";
    return;
  }

  if (!active) {
    dictationBadge.hidden = true;
    dictationBadge.classList.remove("is-visible");
    dictationBadge.className = "dictation-badge dictation-badge--off";
    return;
  }

  dictationBadge.hidden = false;
  dictationBadge.classList.add("is-visible");
  dictationBadge.textContent = "Dictado en vivo: activo — mirá Notas mientras hablás";
  dictationBadge.className = "dictation-badge dictation-badge--on is-visible";
}

function showCompatibilityHint() {
  if (!window.ZafraAudioRecorder?.getCompatibilityHint || !dictationHint) return;

  const hint = ZafraAudioRecorder.getCompatibilityHint();
  if (!hint) return;

  dictationHint.textContent = hint.message;
  if (hint.level === "error" && dictationBadge) {
    dictationBadge.hidden = false;
    dictationBadge.textContent = hint.message;
    dictationBadge.className = "dictation-badge dictation-badge--warn";
  }
}

function hasTextoOAudio() {
  return textoInput.value.trim().length > 0 || getActiveAudioFile() !== null;
}

function hasTextoConsulta() {
  return textoInput.value.trim().length > 0;
}

function initAudioRecorder() {
  if (!window.ZafraAudioRecorder) {
    return;
  }

  audioRecorder = new ZafraAudioRecorder({
    onStatus: (message) => updateAudioStatus(message),
    onStateChange: ({ isActive, isRecording, isProcessing }) => {
      const phase = isRecording ? "recording" : (isProcessing ? "processing" : "requesting");
      setRecordingUi(isActive, isActive ? phase : null);
      if (!isActive) {
        textoInput.classList.remove("form__textarea--dictating");
      }
    },
    onDictationChange: ({ active, detail, hint }) => {
      updateDictationBadge(active, detail, hint);
    },
    onTranscript: ({ display, isRecording }) => {
      if (display && (isRecording || audioRecorder?.isActive())) {
        textoInput.value = display;
        textoInput.classList.add("form__textarea--dictating");
        textoInput.scrollTop = textoInput.scrollHeight;
      }
    },
    onComplete: ({ blob, mimeType, extension, textOnly }) => {
      if (blob) {
        recordedBlob = blob;
        recordedMimeType = mimeType;
        recordedExtension = extension;
        setAudioPreview(recordedBlob);
        btnLimpiarAudio.disabled = false;
        updateAudioStatus(`Grabación lista (${formatBytes(recordedBlob.size)}). Revisá las notas y tocá Analizar.`);
      } else {
        recordedBlob = null;
        setAudioPreview(null);
        btnLimpiarAudio.disabled = true;
        updateAudioStatus(textOnly ? "Texto listo. Revisá Notas y tocá Analizar." : "Listo. Revisá Notas y tocá Analizar.");
      }

      setRecordingUi(false);
      updateDictationBadge(false, "idle");
      textoInput.classList.remove("form__textarea--dictating");

      const committed = audioRecorder.getCommittedText();
      if (committed) {
        textoInput.value = committed;
      }

      if (!committed) {
        showToast("No se detectó texto. Escribí tu consulta en Notas antes de analizar.", true);
        textoInput.focus();
      }
    },
    onError: (message) => {
      setRecordingUi(false);
      textoInput.classList.remove("form__textarea--dictating");
      showToast(message, true);
    },
  });

  if (!ZafraAudioRecorder.isSpeechSupported()) {
    const browser = ZafraAudioRecorder.getBrowserInfo?.() || {};
    updateDictationBadge(
      false,
      "unsupported",
      browser.id === "samsung"
        ? "Samsung Internet: instalá Chrome para dictado en vivo, o escribí en Notas."
        : "Usá Chrome para dictado en vivo. También podés escribir en Notas."
    );
  }

  showCompatibilityHint();
  setRecordingUi(false);
}

function startRecording() {
  if (!audioRecorder) {
    showToast("La grabación no está disponible en este navegador.", true);
    return;
  }

  if (audioRecorder.isActive()) {
    return;
  }

  resetSavedAudio();
  audioRecorder.start(textoInput.value.trim());
}

function stopRecording() {
  if (!audioRecorder?.isActive()) {
    return;
  }
  audioRecorder.stop();
}

function formatTextoHumano(texto) {
  if (!texto) return "";
  const escaped = String(texto)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped
    .split("\n")
    .map((line) => {
      const trimmed = line.trim();
      if (!trimmed) return "";
      if (trimmed.startsWith("•")) {
        return `<p class="result-bullet">${trimmed}</p>`;
      }
      return `<p>${trimmed}</p>`;
    })
    .join("");
}

function renderFuentes(fuentes) {
  if (!fuentes || fuentes.length === 0) {
    return "";
  }
  return `
    <div class="fuentes-box">
      <p class="result-meta"><strong>Fuentes consultadas</strong></p>
      <ul class="fuentes-list">
        ${fuentes.map((f) => `<li>${f}</li>`).join("")}
      </ul>
    </div>
  `;
}

function showResults(data) {
  const semaforo = data.semaforo || "amarillo";
  const semaforoLabels = { verde: "Favorable", amarillo: "Precaución", rojo: "No recomendado" };

  resultCards.clima.classList.add("is-active");
  resultCards.recomendacion.classList.add("is-active");
  resultCards.explicacion.classList.add("is-active");

  const cond = data.condiciones_actuales || {};
  const fuentes = (data.fuentes_conocimiento && data.fuentes_conocimiento.length)
    ? data.fuentes_conocimiento.join("; ")
    : ((data.fuentes_usadas || []).join(", ") || "—");

  resultContents.clima.hidden = false;
  const climaCard = resultCards.clima;
  const climaPlaceholder = climaCard.querySelector(".card__placeholder");
  if (climaPlaceholder) climaPlaceholder.hidden = true;
  resultContents.clima.innerHTML = `
    <div class="semaforo semaforo--${semaforo}">
      <span class="semaforo__dot" aria-hidden="true"></span>
      <strong>${semaforoLabels[semaforo] || semaforo}</strong>
      ${data.veredicto ? `<span class="semaforo__veredicto">${data.veredicto}</span>` : ""}
    </div>
    <ul class="clima-list">
      <li><strong>Temperatura:</strong> ${cond.temperatura_c ?? "—"}°C</li>
      <li><strong>Humedad:</strong> ${cond.humedad_pct ?? "—"}%</li>
      <li><strong>Viento:</strong> ${cond.viento_kmh ?? "—"} km/h</li>
      <li><strong>Prob. lluvia:</strong> ${cond.prob_lluvia_pct ?? "—"}%</li>
      <li><strong>Temp. suelo:</strong> ${cond.temp_suelo_c ?? "—"}°C</li>
      <li><strong>Humedad suelo:</strong> ${cond.humedad_suelo_pct ?? "—"}%</li>
    </ul>
    <p class="result-meta"><strong>Fuentes:</strong> ${fuentes}</p>
    ${renderAdvertencias(data.advertencias)}
  `;

  resultContents.recomendacion.hidden = false;
  const recPlaceholder = resultCards.recomendacion.querySelector(".card__placeholder");
  if (recPlaceholder) recPlaceholder.hidden = true;
  resultContents.recomendacion.innerHTML = `
    <p><strong>Cultivo:</strong> ${formatCultivo(data.cultivo)}</p>
    <p><strong>Evaluación:</strong> ${formatTipo(data.tipo_evaluacion)}</p>
    <p><strong>Ubicación:</strong> ${data.ubicacion}</p>
    ${data.producto_evaluado ? `<p><strong>Producto:</strong> ${data.producto_evaluado}</p>` : ""}
    <div class="result-highlight">${formatTextoHumano(data.recomendacion) || "<p>Sin recomendación disponible.</p>"}</div>
    ${renderFuentes(data.fuentes_conocimiento)}
    ${data.evaluacion_id ? `<p class="result-meta">ID evaluación: ${data.evaluacion_id}</p>` : ""}
  `;

  resultContents.explicacion.hidden = false;
  const expPlaceholder = resultCards.explicacion.querySelector(".card__placeholder");
  if (expPlaceholder) expPlaceholder.hidden = true;
  resultContents.explicacion.innerHTML = `
    ${formatTextoHumano(data.explicacion || data.mensaje || "Sin explicación disponible.")}
    ${data.texto ? `<p class="result-meta"><strong>Notas:</strong> ${data.texto}</p>` : ""}
    ${data.audio_recibido ? `<p class="result-meta"><strong>Audio:</strong> ${data.audio_nombre}</p>` : ""}
  `;

  scrollToResults();
}

function scrollToResults() {
  const target = document.getElementById("resultados");
  if (!target) return;
  requestAnimationFrame(() => {
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

function renderAdvertencias(advertencias) {
  if (!advertencias || advertencias.length === 0) {
    return `<p class="result-meta">Sin advertencias.</p>`;
  }
  return `
    <ul class="advertencias-list">
      ${advertencias.map((item) => `
        <li class="advertencia-item advertencia-item--${item.severidad || "media"}">
          ${item.mensaje}
        </li>
      `).join("")}
    </ul>
  `;
}

async function enviarEvaluacion(formData) {
  const headers = {};
  if (window.ZafraAuth?.getAccessToken) {
    const token = await window.ZafraAuth.getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/evaluar`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const detail = error.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(" ")
      : detail || "Error al conectar con la API.";
    throw new Error(message);
  }

  return response.json();
}

initAudioRecorder();

btnGrabar.addEventListener("click", startRecording);
btnDetener.addEventListener("click", stopRecording);
btnLimpiarAudio.addEventListener("click", clearAudio);

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (audioRecorder?.isActive()) {
    showToast("Detené la grabación antes de analizar.", true);
    return;
  }

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const latitud = document.getElementById("latitud")?.value;
  const longitud = document.getElementById("longitud")?.value;

  if (!latitud || !longitud) {
    showToast("Seleccioná la ubicación en el mapa antes de analizar.", true);
    return;
  }

  if (!hasTextoConsulta()) {
    showToast("Escribí o dictá tu consulta en Notas antes de analizar.", true);
    textoInput.focus();
    return;
  }

  const formData = new FormData();
  formData.append("cultivo", form.cultivo.value);
  formData.append("tipo_evaluacion", form.tipo_evaluacion.value);
  formData.append("ubicacion", form.ubicacion.value.trim());
  formData.append("latitud", latitud);
  formData.append("longitud", longitud);

  const texto = textoInput.value.trim();
  if (texto) {
    formData.append("texto", texto);
  }

  const audioFile = getActiveAudioFile();
  if (audioFile) {
    formData.append("audio", audioFile, audioFile.name);
  }

  resetResults();
  setLoading(true);

  try {
    const data = await enviarEvaluacion(formData);
    showResults(data);
    showToast("Evaluación enviada correctamente.");
  } catch (error) {
    showToast(error.message, true);
  } finally {
    setLoading(false);
  }
});
