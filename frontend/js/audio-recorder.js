/**
 * Zafra AI — Grabación de audio + dictado en tiempo real (Web Speech API).
 * Grabar inicia el micrófono; Detener lo cierra. Sin auto-inicio ni estados ambiguos.
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

  function AudioRecorder(options) {
    this.onStatus = options.onStatus || function () {};
    this.onTranscript = options.onTranscript || function () {};
    this.onComplete = options.onComplete || function () {};
    this.onError = options.onError || function () {};
    this.onStateChange = options.onStateChange || function () {};

    this._mediaRecorder = null;
    this._stream = null;
    this._chunks = [];
    this._mimeType = "";
    this._speech = null;
    this._baseText = "";
    this._finalText = "";
    this._interimText = "";
    this._state = "idle"; // idle | requesting | recording | processing
    this._speechActive = false;
    this._cancelRequested = false;
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

  AudioRecorder.prototype._emitTranscript = function () {
    const parts = [];
    if (this._baseText) parts.push(this._baseText);
    if (this._finalText) parts.push(this._finalText);
    const committed = parts.join(parts.length > 1 && this._baseText && this._finalText ? " " : "");
    this.onTranscript({
      display: [committed, this._interimText].filter(Boolean).join(committed && this._interimText ? " " : ""),
      committed: committed.trim(),
      interim: this._interimText.trim(),
      isRecording: this._state === "recording",
    });
  };

  AudioRecorder.prototype._startSpeech = function () {
    const SpeechRecognition = getSpeechRecognition();
    if (!SpeechRecognition || this._state !== "recording") {
      return false;
    }

    try {
      this._speech = new SpeechRecognition();
      this._speech.lang = "es-BO";
      this._speech.continuous = true;
      this._speech.interimResults = true;
      this._speech.maxAlternatives = 1;

      this._speech.onresult = (event) => {
        if (this._state !== "recording") return;

        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const result = event.results[i];
          const text = result[0]?.transcript?.trim();
          if (!text) continue;
          if (result.isFinal) {
            this._finalText = [this._finalText, text].filter(Boolean).join(" ");
          } else {
            interim = [interim, text].filter(Boolean).join(" ");
          }
        }
        this._interimText = interim;
        this._emitTranscript();
      };

      this._speech.onerror = (event) => {
        if (event.error === "no-speech" || event.error === "aborted") {
          return;
        }
        if (event.error === "not-allowed") {
          this.onError("No se pudo usar el dictado por voz. Podés escribir manualmente.");
        }
      };

      this._speech.onend = () => {
        if (this._state === "recording" && this._speechActive) {
          try {
            this._speech.start();
          } catch (_err) {
            this._speechActive = false;
          }
        }
      };

      this._speech.start();
      this._speechActive = true;
      return true;
    } catch (_err) {
      this._speech = null;
      this._speechActive = false;
      return false;
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
  };

  AudioRecorder.prototype._finishCancelled = function () {
    this._stopSpeech();
    this._cleanupStream();
    this._resetSession();
    this._setState("idle");
    this.onStatus("Grabación cancelada.");
  };

  /**
   * Iniciar grabación al pulsar Grabar (llamar desde click, sin await previo).
   */
  AudioRecorder.prototype.start = function (baseText) {
    if (this._state === "requesting" || this._state === "recording" || this._state === "processing") {
      return;
    }

    if (!AudioRecorder.isRecordingSupported()) {
      const msg = isSecureContext()
        ? "Tu navegador no permite grabar audio. Probá Chrome o subí un archivo."
        : "La grabación requiere HTTPS. Abrí la app desde https://agro-floppy.vercel.app";
      this.onError(msg);
      return;
    }

    this._baseText = (baseText || "").trim();
    this._finalText = "";
    this._interimText = "";
    this._chunks = [];
    this._mimeType = pickMimeType();
    this._cancelRequested = false;

    this._setState("requesting");
    this.onStatus("Solicitando micrófono…");

    const constraints = {
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    };

    navigator.mediaDevices
      .getUserMedia(constraints)
      .then((stream) => {
        if (this._cancelRequested) {
          stream.getTracks().forEach((track) => track.stop());
          this._finishCancelled();
          return;
        }

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

        if (this._cancelRequested) {
          this._finishCancelled();
          return;
        }

        this._setState("recording");
        this._mediaRecorder.start(250);

        const speechStarted = this._startSpeech();
        if (speechStarted) {
          this.onStatus("Grabando… el texto aparece en Notas mientras hablás.");
        } else {
          this.onStatus("Grabando audio… tocá Detener cuando termines.");
        }
        this._emitTranscript();
      })
      .catch((error) => {
        this._cleanupStream();
        this._resetSession();
        this._setState("idle");

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

  /** Detener grabación al pulsar Detener. */
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
