-- Zafra AI — Esquema inicial de base de datos
-- Ejecutar: psql -U postgres -d zafra_ai -f schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Usuarios (productores, agrónomos, administradores)
CREATE TABLE IF NOT EXISTS usuarios (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(120) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Catálogo de cultivos
CREATE TABLE IF NOT EXISTS cultivos (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Evaluaciones realizadas
CREATE TABLE IF NOT EXISTS evaluaciones (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    cultivo_id      INTEGER NOT NULL REFERENCES cultivos(id) ON DELETE RESTRICT,
    tipo_evaluacion VARCHAR(80) NOT NULL,
    ubicacion       VARCHAR(255) NOT NULL,
    resultado       TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Datos semilla
INSERT INTO cultivos (nombre, descripcion) VALUES
    ('soya', 'Glycine max — cultivo oleaginoso de verano'),
    ('maiz', 'Zea mays — cereal de grano')
ON CONFLICT (nombre) DO NOTHING;

-- Índices útiles para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_evaluaciones_cultivo ON evaluaciones(cultivo_id);
CREATE INDEX IF NOT EXISTS idx_evaluaciones_created ON evaluaciones(created_at DESC);
