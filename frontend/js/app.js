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
const audioFileInput = document.getElementById("audio-file");
const btnGrabar = document.getElementById("btn-grabar");
const btnDetener = document.getElementById("btn-detener");
const btnLimpiarAudio = document.getElementById("btn-limpiar-audio");
const audioStatus = document.getElementById("audio-status");
const audioPreview = document.getElementById("audio-preview");

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

let mediaRecorder = null;
let audioChunks = [];
let recordedBlob = null;
let recordingStream = null;

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
  Object.values(resultCards).forEach((card) => card.classList.remove("is-active"));
  Object.values(resultContents).forEach((content) => {
    content.hidden = true;
    content.textContent = "";
  });
}

function updateAudioStatus(message) {
  audioStatus.textContent = message;
}

function setAudioPreview(blob) {
  if (!blob) {
    audioPreview.hidden = true;
    audioPreview.removeAttribute("src");
    return;
  }

  audioPreview.src = URL.createObjectURL(blob);
  audioPreview.hidden = false;
}

function clearAudio() {
  recordedBlob = null;
  audioChunks = [];
  audioFileInput.value = "";
  btnLimpiarAudio.disabled = true;
  setAudioPreview(null);
  updateAudioStatus("Sin audio seleccionado.");
}

function getActiveAudioFile() {
  if (recordedBlob) {
    return new File([recordedBlob], "nota-grabada.webm", {
      type: recordedBlob.type || "audio/webm",
    });
  }

  if (audioFileInput.files.length > 0) {
    return audioFileInput.files[0];
  }

  return null;
}

function hasTextoOAudio() {
  return textoInput.value.trim().length > 0 || getActiveAudioFile() !== null;
}

async function startRecording() {
  try {
    recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(recordingStream);
    audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    });

    mediaRecorder.addEventListener("stop", () => {
      recordedBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || "audio/webm" });
      audioFileInput.value = "";
      setAudioPreview(recordedBlob);
      btnLimpiarAudio.disabled = false;
      updateAudioStatus(`Grabación lista (${formatBytes(recordedBlob.size)}).`);
      recordingStream.getTracks().forEach((track) => track.stop());
      recordingStream = null;
    });

    mediaRecorder.start();
    btnGrabar.disabled = true;
    btnDetener.disabled = false;
    updateAudioStatus("Grabando...");
  } catch (error) {
    showToast("No se pudo acceder al micrófono.", true);
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }

  btnGrabar.disabled = false;
  btnDetener.disabled = true;
}

function showPlaceholderResults(data) {
  resultCards.recomendacion.classList.add("is-active");
  resultContents.recomendacion.hidden = false;

  const textoHtml = data.texto
    ? `<p><strong>Texto:</strong> ${data.texto}</p>`
    : `<p><strong>Texto:</strong> <em>Sin notas escritas</em></p>`;

  const audioHtml = data.audio_recibido
    ? `<p><strong>Audio:</strong> ${data.audio_nombre} (${formatBytes(data.audio_tamano_bytes)})</p>`
    : `<p><strong>Audio:</strong> <em>No enviado</em></p>`;

  const coordsHtml = data.latitud != null && data.longitud != null
    ? `<p><strong>Coordenadas:</strong> ${data.latitud.toFixed(6)}, ${data.longitud.toFixed(6)}</p>`
    : "";

  resultContents.recomendacion.innerHTML = `
    <p><strong>Cultivo:</strong> ${formatCultivo(data.cultivo)}</p>
    <p><strong>Evaluación:</strong> ${formatTipo(data.tipo_evaluacion)}</p>
    <p><strong>Ubicación:</strong> ${data.ubicacion}</p>
    ${coordsHtml}
    ${textoHtml}
    ${audioHtml}
    <p style="margin-top:0.75rem;color:var(--color-gray-500)">${data.mensaje}</p>
  `;
}

async function enviarEvaluacion(formData) {
  const response = await fetch(`${API_BASE_URL}/evaluar`, {
    method: "POST",
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

btnGrabar.addEventListener("click", startRecording);
btnDetener.addEventListener("click", stopRecording);
btnLimpiarAudio.addEventListener("click", clearAudio);

audioFileInput.addEventListener("change", () => {
  const file = audioFileInput.files[0];
  if (!file) {
    clearAudio();
    return;
  }

  recordedBlob = null;
  audioChunks = [];
  setAudioPreview(file);
  btnLimpiarAudio.disabled = false;
  updateAudioStatus(`Archivo seleccionado: ${file.name} (${formatBytes(file.size)}).`);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

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

  if (!hasTextoOAudio()) {
    showToast("Agregá una nota de texto o un audio antes de analizar.", true);
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
    showPlaceholderResults(data);
    showToast("Evaluación enviada correctamente.");
  } catch (error) {
    showToast(error.message, true);
  } finally {
    setLoading(false);
  }
});
