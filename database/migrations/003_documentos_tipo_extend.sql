-- Ampliar tipos de documento (markdown, faq)
BEGIN;

ALTER TABLE documentos DROP CONSTRAINT IF EXISTS documentos_tipo_check;
ALTER TABLE documentos ADD CONSTRAINT documentos_tipo_check
    CHECK (tipo IN ('excel', 'pdf', 'json', 'codigo', 'markdown', 'faq'));

COMMIT;
