# Documentación Agronómica — Zafra AI

Este documento centraliza las reglas agronómicas que Zafra AI utilizará para generar recomendaciones. Se irá ampliando durante el hackathon.

## Cultivos soportados

| Cultivo | Nombre científico | Temporada principal |
|---------|-------------------|---------------------|
| Soya    | *Glycine max*     | Verano              |
| Maíz    | *Zea mays*        | Verano              |

## Tipos de evaluación

1. **Siembra** — Ventana óptima, profundidad, densidad, condiciones de suelo.
2. **Fertilización** — NPK, micronutrientes, momento de aplicación.
3. **Riego** — Déficit hídrico, ETc, pronóstico de lluvias.
4. **Plagas** — Umbrales de intervención, monitoreo, manejo integrado.
5. **Cosecha** — Humedad de grano, punto de corte, rendimiento estimado.

## Variables meteorológicas relevantes (futuro)

- Temperatura (mín, máx, promedio)
- Precipitación acumulada (24 h, 7 días)
- Humedad relativa
- Evapotranspiración (ET₀)
- Radiación solar

## Reglas agronómicas (placeholder)

> Las reglas concretas se definirán con el equipo agronómico.

### Ejemplo — Siembra de soya

```
SI temperatura_suelo >= 15°C
Y humedad_suelo >= umbral_minimo
Y pronostico_lluvia_48h < 30mm
ENTONCES ventana_siembra = "favorable"
```

### Ejemplo — Riego de maíz

```
SI ETc_acumulada > precipitacion_acumulada + reserva_suelo
Y fase_cultivo IN ("VT", "R1", "R2")
ENTONCES recomendar_riego = true
```

## Fuentes de referencia

- INTA — Instituto Nacional de Tecnología Agropecuaria
- EMBRAPA — Empresa Brasileira de Pesquisa Agropecuária
- FAO — Food and Agriculture Organization

## Notas para desarrollo

- Las reglas deben ser **explicables**: cada recomendación incluirá el razonamiento.
- Zafra AI **no reemplaza** al ingeniero agrónomo; es un copiloto.
- Priorizar reglas simples y verificables antes de modelos complejos.
