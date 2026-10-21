# Stage 23: Media service (FastAPI)

Where: `services/media`. Prerequisites: stage 14.

- [ ] **S23.T01** MinIO in Compose, service skeleton; ADR 0047 S3 client and image library
  Must know: S3 API, MinIO

- [ ] **S23.T02** `Asset` model + state machine `pending → uploaded → processing → ready / failed → deleted`
  Must know: state machine

- [ ] **S23.T03** Presigned POST upload with size/content-type policy and short TTL
  Must know: presigned URLs, POST policies

- [ ] **S23.T04** Confirm endpoint: object exists, real size, magic-bytes type check
  Must know: file type detection

- [ ] **S23.T05** Tenant key prefix and 404 isolation
  Must know: key design

- [ ] **S23.T06** Processing worker: thumbnails, WebP, EXIF strip, decompression bomb limit
  Must know: Pillow, image safety

- [ ] **S23.T07** Public vs private files: cache headers/ETag vs presigned GET
  Must know: object ACLs, caching

- [ ] **S23.T08** `media.asset.ready.v1`; monolith stores `asset_id`; product images wired
  Must know: events

- [ ] **S23.T09** Orphan cleanup: lifecycle rule for unfinished uploads, GC for unreferenced assets
  Must know: lifecycle rules, GC job

- [ ] **S23.T10** Move import files and PDF receipts to Media
  Must know: refactor

- [ ] **S23.T11** `[EXT]` Storage quota via entitlements, sha256 dedup; `[OPT]` ClamAV, CDN
  Must know: quotas, dedup
