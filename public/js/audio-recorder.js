/**
 * Zafra AI — Grabación de audio + dictado en tiempo real (Web Speech API).
 * En PC: el dictado arranca antes del grabador para evitar conflicto de micrófono.
 */
(function (global) {
  "use strict";

  const MIME_CANDIDATES = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/aac",
    "audio/ogg;codecs=opus",
    "audio/ogg",
  ];

  const SPEECH_LANGS = ["es-ES", "es-MX", "es-BO", "es-US", "es"];

  const EXT_BY_MIME = {
    "audio/webm": ".webm",
    "audio/mp4": ".m4a",
    "audio/aac": ".aac",
    "audio/ogg": ".ogg",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
  };

  function pickMimeType() {
    if (typeof MediaRecorder === "undefined" || !MediaRecorder.isTypeSupported) {
      return "";
    }
    for (const mime of MIME_CANDIDATES) {
      if (MediaRecorder.isTypeSupported(mime)) {
        return mime;
      }
    }
    return "";
  }

  function extensionForMime(mime) {
    if (!mime) return ".webm";
    const base = mime.split(";")[0].trim().toLowerCase();
    return EXT_BY_MIME[base] || ".webm";
  }

  function getSpeechRecognition() {
    return global.SpeechRecognition || global.webkitSpeechRecognition || null;
  }

  function isSecureContext() {
    return global.isSecureContext === true;
  }

  function isMobileDevice() {
    return /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || "");
  }

  function AudioRecorder(options) {
    this.onStatus = options.onStatus || function () {};
    this.onTranscript = options.onTranscript || function () {};
    this.onComplete = options.onComplete || function () {};
    this.onError = options.onError || function () {};
    this.onStateChange = options.onStateChange || function () {};
    this.onDictationChange = options.onDictationChange || function () {};

    this._mediaRecorder = null;
    this._stream = null;
    this._chunks = [];
    this._mimeType = "";
    this._speech = null;
    this._baseText = "";
    this._finalText = "";
    this._interimText = "";
    this._state = "idle";
    this._speechActive = false;
    this._dictationActive = false;
    this._cancelRequested = false;
    this._langIndex = 0;
    this._speechRetryCount = 0;
    this._recorderStarted = false;
  }

  AudioRecorder.isRecordingSupported = function () {
    return (
      isSecureContext() &&
      typeof navigator !== "undefined" &&
      !!navigator.mediaDevices &&
      typeof navigator.mediaDevices.getUserMedia === "function" &&
      typeof MediaRecorder !== "undefined"
    );
  };

  AudioRecorder.isSpeechSupported = function () {
    return !!getSpeechRecognition();
  };

  AudioRecorder.pickMimeType = pickMimeType;
  AudioRecorder.extensionForMime = extensionForMime;

  AudioRecorder.prototype._setState = function (state) {
    this._state = state;
    this.onStateChange({
      state,
      isActive: state === "requesting" || state === "recording" || state === "processing",
      isRecording: state === "recording",
      isProcessing: state === "processing",
    });
  };

  AudioRecorder.prototype._setDictation = function (active, detail) {
    this._dictationActive = active;
    this.onDictationChange({ active, detail: detail || "" });
  };

  AudioRecorder.prototype._emitTranscript = function () {
    const parts = [];
    if (this._baseText) parts.push(this._baseText);
    if (this._finalText) parts.push(this._finalText);
    const committed = parts.join(parts.length > 1 && this._baseText && this._finalText ? " " : "");
    const canUpdate = this._state === "recording" || this._state === "processing";
    this.onTranscript({
      display: [committed, this._interimText].filter(Boolean).join(committed && this._interimText ? " " : ""),
      committed: committed.trim(),
      interim: this._interimText.trim(),
      isRecording: canUpdate,
    });
  };

  AudioRecorder.prototype._bindSpeechHandlers = function () {
    if (!this._speech) return;

    this._speech.onresult = (event) => {
      if (this._state !== "recording") return;

      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i];
        const text = result[0]?.transcript?.trim();
        if (!text) continue;
        if (result.isFinal) {
          this._finalText = [this._finalText, text].filter(Boolean).join(" ");
          this._interimText = "";
        } else {
          interim = [interim, text].filter(Boolean).join(" ");
        }
      }
      if (interim) {
        this._interimText = interim;
      }
      this._setDictation(true, "active");
      this._emitTranscript();
    };

    this._speech.onstart = () => {
      this._setDictation(true, "active");
      this._maybeStartMediaRecorder();
    };

    this._speech.onerror = (event) => {
      const err = event.error || "";

      if (err === "aborted") {
        return;
      }

      if (err === "no-speech") {
        return;
      }

      if (err === "not-allowed") {
        this._setDictation(false, "denied");
        this.onError("Dictado bloqueado. Permití el micrófono o escribí en Notas.");
        this._maybeStartMediaRecorder();
        return;
      }

      if (err === "network") {
        this._setDictation(false, "network");
        this._retrySpeech("Sin conexión para dictado. Reintentando…");
        this._maybeStartMediaRecorder();
        return;
      }

      if (this._langIndex < SPEECH_LANGS.length - 1) {
        this._langIndex += 1;
        this._retrySpeech(`Reintentando dictado (${SPEECH_LANGS[this._langIndex]})…`);
        return;
      }

      this._setDictation(false, "error");
      this._maybeStartMediaRecorder();
    };

    this._speech.onend = () => {
      if (this._state === "recording" && this._speechActive) {
        try {
          this._speech.start();
        } catch (_err) {
          this._speechActive = false;
          this._setDictation(false, "stopped");
        }
      }
    };
  };

  AudioRecorder.prototype._retrySpeech = function (statusMsg) {
    if (this._state !== "recording" || this._speechRetryCount >= 3) {
      return;
    }
    this._speechRetryCount += 1;
    if (statusMsg) {
      this.onStatus(statusMsg);
    }
    window.setTimeout(() => {
      if (this._state === "recording") {
        this._startSpeech();
      }
    }, 400);
  };

  AudioRecorder.prototype._startSpeech = function () {
    const SpeechRecognition = getSpeechRecognition();
    if (!SpeechRecognition || this._state !== "recording") {
      return false;
    }

    try {
      if (this._speech) {
        this._speechActive = false;
        try {
          this._speech.stop();
        } catch (_err) {
          /* noop */
        }
      }

      this._speech = new SpeechRecognition();
      this._speech.lang = SPEECH_LANGS[this._langIndex] || "es-ES";
      this._speech.continuous = true;
      this._speech.interimResults = true;
      this._speech.maxAlternatives = 1;

      this._bindSpeechHandlers();
      this._speech.start();
      this._speechActive = true;
      return true;
    } catch (_err) {
      this._speech = null;
      this._speechActive = false;
      this._setDictation(false, "unsupported");
      return false;
    }
  };

  AudioRecorder.prototype._setupMediaRecorder = function (stream) {
    this._stream = stream;
    const options = this._mimeType ? { mimeType: this._mimeType } : undefined;

    try {
      this._mediaRecorder = options
        ? new MediaRecorder(stream, options)
        : new MediaRecorder(stream);
    } catch (_err) {
      this._mediaRecorder = new MediaRecorder(stream);
    }

    if (!this._mimeType && this._mediaRecorder.mimeType) {
      this._mimeType = this._mediaRecorder.mimeType;
    }

    this._mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) {
        this._chunks.push(event.data);
      }
    });

    this._mediaRecorder.addEventListener("stop", () => {
      const mime = this._mimeType || this._mediaRecorder?.mimeType || "audio/webm";
      const blob = new Blob(this._chunks, { type: mime });
      this._cleanupStream();
      this._resetSession();
      this._setState("idle");
      this._setDictation(false, "idle");
      this.onComplete({
        blob,
        mimeType: mime,
        extension: extensionForMime(mime),
      });
    });

    this._mediaRecorder.addEventListener("error", () => {
      this.onError("Falló la grabación de audio.");
      this.stop();
    });
  };

  AudioRecorder.prototype._maybeStartMediaRecorder = function () {
    if (this._recorderStarted || !this._mediaRecorder || this._state !== "recording") {
      return;
    }

    this._recorderStarted = true;
    try {
      this._mediaRecorder.start(250);
    } catch (_err) {
      this.onError("No se pudo iniciar la grabación de audio.");
    }

    this._updateRecordingStatus();
  };

  AudioRecorder.prototype._beginRecordingPhase = function () {
    this._setState("recording");
    this._recorderStarted = false;
    this._langIndex = 0;
    this._speechRetryCount = 0;

    const speechAvailable = AudioRecorder.isSpeechSupported();
    const desktop = !isMobileDevice();

    if (speechAvailable && desktop) {
      // PC: dictado primero, grabador después (evita conflicto de micrófono en Windows).
      this._setDictation(false, "starting");
      this.onStatus("Iniciando dictado en vivo…");
      const speechStarted = this._startSpeech();
      if (!speechStarted) {
        this._maybeStartMediaRecorder();
        this._updateRecordingStatus();
      } else {
        window.setTimeout(() => {
          this._maybeStartMediaRecorder();
          this._updateRecordingStatus();
        }, 1200);
      }
      return;
    }

    if (speechAvailable) {
      this._maybeStartMediaRecorder();
      this._startSpeech();
    } else {
      this._maybeStartMediaRecorder();
    }

    this._updateRecordingStatus();
    this._emitTranscript();
  };

  AudioRecorder.prototype._updateRecordingStatus = function () {
    if (this._dictationActive) {
      this.onStatus("Grabando… el texto aparece en Notas mientras hablás.");
      return;
    }

    if (AudioRecorder.isSpeechSupported()) {
      this.onStatus("Grabando audio… si no ves texto en Notas, escribí tu consulta manualmente.");
    } else {
      this.onStatus("Grabando audio… escribí tu consulta en Notas (dictado no disponible en este navegador).");
    }
  };

  AudioRecorder.prototype._stopSpeech = function () {
    this._speechActive = false;
    if (!this._speech) return;
    try {
      this._speech.stop();
    } catch (_err) {
      /* noop */
    }
    this._speech = null;
    if (this._interimText) {
      this._finalText = [this._finalText, this._interimText].filter(Boolean).join(" ");
      this._interimText = "";
    }
    this._emitTranscript();
  };

  AudioRecorder.prototype._cleanupStream = function () {
    if (this._stream) {
      this._stream.getTracks().forEach((track) => track.stop());
      this._stream = null;
    }
  };

  AudioRecorder.prototype._resetSession = function () {
    this._mediaRecorder = null;
    this._chunks = [];
    this._mimeType = "";
    this._cancelRequested = false;
    this._recorderStarted = false;
    this._langIndex = 0;
    this._speechRetryCount = 0;
  };

  AudioRecorder.prototype._finishCancelled = function () {
    this._stopSpeech();
    this._cleanupStream();
    this._resetSession();
    this._setState("idle");
    this._setDictation(false, "idle");
    this.onStatus("Grabación cancelada.");
  };

  AudioRecorder.prototype.start = function (baseText) {
    if (this._state === "requesting" || this._state === "recording" || this._state === "processing") {
      return;
    }

    if (!AudioRecorder.isRecordingSupported()) {
      const msg = isSecureContext()
        ? "Tu navegador no permite grabar audio. Probá Chrome o Edge."
        : "La grabación requiere HTTPS. Abrí la app desde https://agro-floppy.vercel.app";
      this.onError(msg);
      return;
    }

    if (!AudioRecorder.isSpeechSupported()) {
      this.onDictationChange({
        active: false,
        detail: "unsupported",
        hint: "Usá Chrome o Edge para dictado en vivo. También podés escribir en Notas.",
      });
    }

    this._baseText = (baseText || "").trim();
    this._finalText = "";
    this._interimText = "";
    this._chunks = [];
    this._mimeType = pickMimeType();
    this._cancelRequested = false;

    this._setState("requesting");
    this.onStatus("Solicitando micrófono…");

    navigator.mediaDevices
      .getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
      .then((stream) => {
        if (this._cancelRequested) {
          stream.getTracks().forEach((track) => track.stop());
          this._finishCancelled();
          return;
        }

        this._setupMediaRecorder(stream);

        if (this._cancelRequested) {
          this._finishCancelled();
          return;
        }

        this._beginRecordingPhase();
      })
      .catch((error) => {
        this._cleanupStream();
        this._resetSession();
        this._setState("idle");
        this._setDictation(false, "idle");

        const name = error?.name || "";
        if (name === "NotAllowedError" || name === "PermissionDeniedError") {
          this.onError("Permiso de micrófono denegado. Activá el micrófono en ajustes del navegador.");
        } else if (name === "NotFoundError") {
          this.onError("No se encontró micrófono en este dispositivo.");
        } else {
          this.onError("No se pudo acceder al micrófono.");
        }
      });
  };

  AudioRecorder.prototype.stop = function () {
    if (this._state === "idle") {
      return;
    }

    if (this._state === "requesting") {
      this._cancelRequested = true;
      this._finishCancelled();
      return;
    }

    if (this._state === "processing") {
      return;
    }

    this._setState("processing");
    this._stopSpeech();
    this._setDictation(false, "idle");
    this.onStatus("Guardando grabación…");

    if (this._mediaRecorder && this._mediaRecorder.state !== "inactive") {
      try {
        this._mediaRecorder.requestData();
        this._mediaRecorder.stop();
      } catch (_err) {
        this._cleanupStream();
        this._resetSession();
        this._setState("idle");
        this.onError("No se pudo guardar la grabación.");
      }
      return;
    }

    this._cleanupStream();
    this._resetSession();
    this._setState("idle");
  };

  AudioRecorder.prototype.isRecording = function () {
    return this._state === "recording";
  };

  AudioRecorder.prototype.isActive = function () {
    return this._state === "requesting" || this._state === "recording" || this._state === "processing";
  };

  AudioRecorder.prototype.getCommittedText = function () {
    const parts = [this._baseText, this._finalText].filter(Boolean);
    return parts.join(parts.length > 1 ? " " : "").trim();
  };

  global.ZafraAudioRecorder = AudioRecorder;
})(window);
