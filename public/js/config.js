/**
 * Configuración del frontend — URLs y entorno.
 */
const APP_CONFIG = {
  /** En Vercel usa /api (mismo dominio). En local usa uvicorn. */
  get apiBaseUrl() {
    const host = window.location.hostname;
    const isLocal = host === "localhost" || host === "127.0.0.1";
    return isLocal ? "http://localhost:8000" : "/api";
  },
};
