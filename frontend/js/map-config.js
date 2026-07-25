/**
 * Configuración del mapa — editá este archivo cuando tengas tus credenciales.
 *
 * Proveedores soportados (futuro):
 *   - "leaflet"  → OpenStreetMap (sin API key, funciona ahora)
 *   - "google"   → Google Maps (requiere MAP_CONFIG.apiKey)
 *   - "mapbox"   → Mapbox (requiere MAP_CONFIG.apiKey)
 */
const MAP_CONFIG = {
  provider: "leaflet",

  /** Centro inicial del mapa [lat, lng]. Santa Cruz de la Sierra, Bolivia. */
  defaultCenter: [-17.78, -63.18],
  defaultZoom: 9,
  selectedZoom: 13,

  /** Solo para google / mapbox. Dejá vacío mientras usás leaflet. */
  apiKey: "",

  /** Capa de tiles. null = OpenStreetMap estándar. */
  tileUrl: null,
  tileAttribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',

  geocoding: {
    /** "nominatim" (gratis) | "google" (requiere apiKey) */
    provider: "nominatim",
    apiKey: "",
    /** URL base de Nominatim. Podés usar tu propia instancia. */
    nominatimUrl: "https://nominatim.openstreetmap.org",
  },
};
