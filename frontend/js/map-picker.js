/**
 * Selector de ubicación en mapa (Leaflet + geocodificación + referencias Santa Cruz).
 */
(function () {
  const modal = document.getElementById("map-modal");
  const mapContainer = document.getElementById("map-container");
  const btnAbrir = document.getElementById("btn-abrir-mapa");
  const btnCerrar = document.getElementById("btn-cerrar-mapa");
  const btnConfirmar = document.getElementById("btn-confirmar-ubicacion");
  const btnMiUbicacion = document.getElementById("btn-mi-ubicacion");
  const backdrop = modal?.querySelector(".map-modal__backdrop");
  const ubicacionInput = document.getElementById("ubicacion");
  const latInput = document.getElementById("latitud");
  const lngInput = document.getElementById("longitud");
  const coordsHint = document.getElementById("ubicacion-coords");
  const mapStatus = document.getElementById("map-status");

  if (!modal || !btnAbrir) return;

  let map = null;
  let marker = null;
  let pendingSelection = null;
  let referenceLayer = null;

  const TIPO_ICONS = {
    agricola: "🌾",
    ganadera: "🐄",
    mixta: "🌾",
  };

  const CAMPO_COLORS = {
    agricola: { fill: "#22c55e", stroke: "#15803d" },
    ganadera: { fill: "#d97706", stroke: "#92400e" },
    mixta: { fill: "#3b82f6", stroke: "#1d4ed8" },
  };

  function setMapStatus(message) {
    if (mapStatus) mapStatus.textContent = message;
  }

  function formatCoords(lat, lng) {
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  }

  function updateCoordsHint(lat, lng, label) {
    if (!coordsHint) return;
    coordsHint.textContent = label
      ? `${label} (${formatCoords(lat, lng)})`
      : formatCoords(lat, lng);
    coordsHint.classList.toggle("location-field__coords--set", Boolean(lat && lng));
  }

  function createRefIcon(tipo) {
    return L.divIcon({
      className: "map-ref-marker-wrap",
      html: `<span class="map-ref-marker map-ref-marker--${tipo}">${TIPO_ICONS[tipo] || "📍"}</span>`,
      iconSize: [34, 34],
      iconAnchor: [17, 17],
      popupAnchor: [0, -14],
    });
  }

  function buildPopupHtml(lugar) {
    const tipoLabel = TIPO_LABELS[lugar.tipo] || lugar.tipo;
    const cultivoLabel = lugar.cultivo ? CULTIVO_LABELS[lugar.cultivo] : null;
    const stats = [
      lugar.hectareas ? `<li><strong>Superficie:</strong> ${lugar.hectareas.toLocaleString("es-BO")} ha</li>` : "",
      lugar.ganado ? `<li><strong>Ganado:</strong> ${lugar.ganado.toLocaleString("es-BO")} cab.</li>` : "",
      cultivoLabel ? `<li><strong>Cultivo ref.:</strong> ${cultivoLabel}</li>` : "",
    ].join("");

    return `
      <div class="map-popup">
        <p class="map-popup__badge map-popup__badge--${lugar.tipo}">${tipoLabel}</p>
        <h3 class="map-popup__title">${lugar.nombre}</h3>
        <p class="map-popup__zone">${lugar.zona}</p>
        <p class="map-popup__desc">${lugar.descripcion}</p>
        ${stats ? `<ul class="map-popup__stats">${stats}</ul>` : ""}
        <button type="button" class="map-popup__btn" data-lat="${lugar.lat}" data-lng="${lugar.lng}" data-label="${lugar.nombre}, ${lugar.zona}">
          Usar esta ubicación
        </button>
        <p class="map-popup__note">Dato sintético — demo hackathon</p>
      </div>
    `;
  }

  function addReferenceLayers() {
    if (!map || referenceLayer) return;

    referenceLayer = L.layerGroup().addTo(map);

    SANTA_CRUZ_CAMPOS.forEach((campo) => {
      const colors = CAMPO_COLORS[campo.tipo];
      L.polygon(campo.coords, {
        color: colors.stroke,
        fillColor: colors.fill,
        fillOpacity: 0.18,
        weight: 2,
        dashArray: campo.tipo === "ganadera" ? "6 4" : null,
      })
        .bindPopup(`<strong>${campo.nombre}</strong><br>Campo sintético (${TIPO_LABELS[campo.tipo]})`)
        .addTo(referenceLayer);
    });

    SANTA_CRUZ_LUGARES.forEach((lugar) => {
      const refMarker = L.marker([lugar.lat, lugar.lng], {
        icon: createRefIcon(lugar.tipo),
        zIndexOffset: -100,
      })
        .bindPopup(buildPopupHtml(lugar), { maxWidth: 280, className: "map-popup-wrap" })
        .addTo(referenceLayer);

      refMarker.on("popupopen", (event) => {
        const popupEl = event.popup.getElement();
        const btn = popupEl?.querySelector(".map-popup__btn");
        btn?.addEventListener("click", () => {
          selectFromReference(
            parseFloat(btn.dataset.lat),
            parseFloat(btn.dataset.lng),
            btn.dataset.label
          );
          map.closePopup();
        });
      });
    });
  }

  async function reverseGeocode(lat, lng) {
    const cfg = MAP_CONFIG.geocoding;

    if (cfg.provider === "google" && cfg.apiKey) {
      const url = new URL("https://maps.googleapis.com/maps/api/geocode/json");
      url.searchParams.set("latlng", `${lat},${lng}`);
      url.searchParams.set("key", cfg.apiKey);
      url.searchParams.set("language", "es");

      const res = await fetch(url);
      const data = await res.json();
      return data.results?.[0]?.formatted_address || formatCoords(lat, lng);
    }

    const base = cfg.nominatimUrl || "https://nominatim.openstreetmap.org";
    const url = new URL(`${base}/reverse`);
    url.searchParams.set("format", "json");
    url.searchParams.set("lat", String(lat));
    url.searchParams.set("lon", String(lng));
    url.searchParams.set("zoom", "14");
    url.searchParams.set("addressdetails", "1");

    const res = await fetch(url, {
      headers: { Accept: "application/json" },
    });

    if (!res.ok) return formatCoords(lat, lng);

    const data = await res.json();
    return data.display_name || formatCoords(lat, lng);
  }

  function placeMarker(lat, lng) {
    if (!map) return;

    if (marker) {
      marker.setLatLng([lat, lng]);
    } else {
      marker = L.marker([lat, lng], {
        draggable: true,
        zIndexOffset: 1000,
      }).addTo(map);
      marker.on("dragend", () => {
        const pos = marker.getLatLng();
        selectPoint(pos.lat, pos.lng, false);
      });
    }

    map.setView([lat, lng], MAP_CONFIG.selectedZoom || 13);
  }

  async function selectPoint(lat, lng, fetchLabel = true) {
    pendingSelection = { lat, lng, label: formatCoords(lat, lng) };
    placeMarker(lat, lng);
    setMapStatus("Obteniendo dirección...");

    if (fetchLabel) {
      try {
        pendingSelection.label = await reverseGeocode(lat, lng);
      } catch {
        pendingSelection.label = formatCoords(lat, lng);
      }
    }

    setMapStatus(`Seleccionado: ${pendingSelection.label}`);
    btnConfirmar.disabled = false;
  }

  function selectFromReference(lat, lng, label) {
    pendingSelection = { lat, lng, label };
    placeMarker(lat, lng);
    setMapStatus(`Seleccionado: ${label}`);
    btnConfirmar.disabled = false;
  }

  function initMap() {
    if (map) {
      map.invalidateSize();
      return;
    }

    const [lat, lng] = MAP_CONFIG.defaultCenter;
    map = L.map(mapContainer, { zoomControl: true }).setView([lat, lng], MAP_CONFIG.defaultZoom);

    const tileUrl = MAP_CONFIG.tileUrl || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    L.tileLayer(tileUrl, {
      attribution: MAP_CONFIG.tileAttribution,
      maxZoom: 19,
    }).addTo(map);

    addReferenceLayers();

    map.on("click", (event) => {
      selectPoint(event.latlng.lat, event.latlng.lng);
    });

    if (latInput.value && lngInput.value) {
      const savedLat = parseFloat(latInput.value);
      const savedLng = parseFloat(lngInput.value);
      if (!Number.isNaN(savedLat) && !Number.isNaN(savedLng)) {
        placeMarker(savedLat, savedLng);
        pendingSelection = {
          lat: savedLat,
          lng: savedLng,
          label: ubicacionInput.value || formatCoords(savedLat, savedLng),
        };
        setMapStatus(`Seleccionado: ${pendingSelection.label}`);
        btnConfirmar.disabled = false;
      }
    }
  }

  function openModal() {
    modal.hidden = false;
    document.body.classList.add("map-modal-open");
    btnConfirmar.disabled = !pendingSelection;
    setMapStatus("Explorá fincas de referencia o hacé clic para marcar tu lote.");
    requestAnimationFrame(() => initMap());
  }

  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove("map-modal-open");
  }

  function confirmSelection() {
    if (!pendingSelection) return;

    ubicacionInput.value = pendingSelection.label;
    latInput.value = String(pendingSelection.lat);
    lngInput.value = String(pendingSelection.lng);
    updateCoordsHint(pendingSelection.lat, pendingSelection.lng, pendingSelection.label);
    closeModal();
  }

  function useMyLocation() {
    if (!navigator.geolocation) {
      setMapStatus("Tu navegador no soporta geolocalización.");
      return;
    }

    setMapStatus("Obteniendo tu ubicación...");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        selectPoint(position.coords.latitude, position.coords.longitude);
      },
      () => setMapStatus("No se pudo obtener tu ubicación. Marcá el punto manualmente."),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  btnAbrir.addEventListener("click", openModal);
  ubicacionInput?.addEventListener("click", openModal);
  btnCerrar?.addEventListener("click", closeModal);
  backdrop?.addEventListener("click", closeModal);
  btnConfirmar?.addEventListener("click", confirmSelection);
  btnMiUbicacion?.addEventListener("click", useMyLocation);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) closeModal();
  });

  if (latInput.value && lngInput.value) {
    updateCoordsHint(parseFloat(latInput.value), parseFloat(lngInput.value), ubicacionInput.value);
  }
})();
