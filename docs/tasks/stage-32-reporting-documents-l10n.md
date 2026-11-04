# Stage 32: Reporting, documents and localization

Where: `modules/reporting`, `modules/documents`. Prerequisites: stages 23 and 26.

## Documents

- [ ] **S32.T01** `DocumentTemplate` model: per tenant/type, Jinja2 source, versioned variable schema
  Must know: Jinja2 sandbox, JSON schema

- [ ] **S32.T02** Rendering worker → PDF (ADR 0057 library; Latin/Cyrillic fonts), barcodes/QR; snapshot stored in Media
  Must know: PDF generation, fonts

- [ ] **S32.T03** Numbering from stage 30; verification hash on documents
  Must know: hashing

- [ ] **S32.T04** `[EXT]` Delivery via Notification with Media links
  Must know: commands

## Reporting engine

- [ ] **S32.T05** `ReportDefinition` model: parameters, whitelisted source, columns
  Must know: safe query building

- [ ] **S32.T06** Async execution with progress; scheduled reports (beat, tenant tz) delivered through Media/Notification
  Must know: Celery, scheduling

- [ ] **S32.T07** Streaming exports: CSV, XLSX, 1C format; memory-bounded test on the largest tenant
  Must know: streaming, openpyxl write-only mode

- [ ] **S32.T08** Row-level security on reports (locations by permission)
  Must know: permission filtering

- [ ] **S32.T09** `[EXT]` BI export API; `[OPT]` pivot reports
  Must know: cursor APIs

## Localization

- [ ] **S32.T10** Locales uz-Latn, uz-Cyrl, ru (ADR 0058 gettext vs catalogue); formatting per tenant
  Must know: i18n, Babel

- [ ] **S32.T11** Multi-language catalog fields with fallback; cross-locale search
  Must know: JSONB translations, FTS

- [ ] **S32.T12** `[EXT]` Tax/receipt format rules as configuration
  Must know: configuration as data
