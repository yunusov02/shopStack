# Retail SaaS Platforma: Middle+ Engineer Roadmap (v4: FastAPI + Django)

Multi-tenant SaaS: **POS + ombor + xarid + narx va aksiyalar + mijozlar va loyalty + moliya + analitika + offline POS + e-commerce + yetkazib berish + integratsiyalar**.

Maqsad: loyiha orqali middle+ darajadagi backend tushunchalarini amalda o'rganish va har bir texnik qarorning **nima uchun** qabul qilinganini tushunish.

---

## Qanday foydalanish

- **Vaqt chegarasi yo'q.** Bosqich faqat **"Tugash mezoni"** bajarilganda tugaydi.
- **"Oldingi shart"** bosqichlar tartibini belgilaydi.
- Batafsil qo'llanmalar `roadmap/` papkasida: `00-tayyorgarlik.md`, `01-tenancy-auth.md`, keyingilari navbat bilan qo'shiladi.
- Har bir task belgilangan:

| Belgi | Ma'nosi |
|---|---|
| `[CORE]` | Majburiy. Yangi muhim tushunchani o'rgatadi yoki keyingi bosqichlar unga bog'liq |
| `[EXT]` | Kengaytma. Core tugagandan keyin qilinadi, qo'shimcha tushuncha beradi |
| `[OPT]` | Ixtiyoriy. Vaqt bo'lsa yoki aynan shu mavzu qiziq bo'lsa |

> **Scope qoidasi:** bu ro'yxat to'liq tijorat ERP tizimi hajmida. Haqiqiy kompaniyalarda buni jamoalar yillar davomida quradi. Avval barcha bosqichlarning `[CORE]` qismini oxirigacha yetkazing, `[EXT]` va `[OPT]` ga keyin qayting. Tugallanmagan 100 ta funksiyadan tugallangan 40 tasi ancha qimmatli.

### MVP chizig'i

| Daraja | Bosqichlar (`[CORE]` qismi) | Natija |
|---|---|---|
| 1. Ishga kirishga tayyor | 0, 1, 2, 3, 5, 9, 10 | Ishlaydigan multi-tenant POS, concurrency, performance. **Ish qidirishni boshlang** |
| 2. Kuchli domen | 4, 6, 7, 8 | Xarid, aksiyalar engine'i, loyalty, moliya |
| 3. Senior'ga yaqin | 12, 13, 14, 16 | Offline sinxronizatsiya, event'lar, birinchi servislar |
| 4. To'liq platforma | 11, 15, 17–21 | HR, Platform va Billing (Django), e-commerce, delivery, integratsiyalar, K8s |

---

## Umumiy qoidalar

### Muhandislik qoidalari (har bosqichda)
- [ ] Har bosqich ishlaydigan, testlangan va deploy qilinadigan holatda tugaydi
- [ ] Testlar kod bilan birga yoziladi, CI har doim yashil
- [ ] Har muhim qaror uchun ADR (`docs/adr/`)
- [ ] **"Buz va o'lcha":** optimallashtirishdan oldin va keyin o'lchanadi, natija README'ga yoziladi
- [ ] Har texnologiya uchun javob tayyor: nima uchun aynan bu, alternativasi nima, narxi qanday

### Domen qoidalari (butun loyiha uchun)
- [ ] **Pul faqat `Decimal`** yoki tiyinlarda butun son. Hech qachon `float`
- [ ] **Stock kamayishi hech qachon asinxron emas.** Sotuv va stock o'zgarishi bitta ACID tranzaksiyada
- [ ] **Hujjatlar tahrirlanmaydi, tuzatiladi.** Yakunlangan sotuv, qabul yoki transfer o'zgartirilmaydi; xato yangi hujjat bilan tuzatiladi (qaytarish, adjustment, storno)
- [ ] **Snapshot:** sotuv qatorida narx, tannarx, soliq va qo'llangan aksiyalar o'sha paytdagi qiymati bilan saqlanadi. Keyingi narx o'zgarishi eski sotuvlarni buzmasligi kerak
- [ ] **Barcha qoldiqlar ledger'dan:** stock, mijoz balansi, ballar, qarzlar. Har bir o'zgarish o'zgarmas yozuv
- [ ] **Har hujjatning holat mashinasi bor** (`draft → ... → completed/cancelled`), o'tishlar log'ga yoziladi
- [ ] **Sezgir operatsiyalar** (refund, void, qo'lda chegirma, narx o'zgartirish, adjustment) permission bilan himoyalanadi va audit log'ga yoziladi

---

## Arxitektura (yakuniy holat)

```
  Back-office (HTMX)      POS terminal (React + TS PWA, offline)     E-commerce
          │                          │  sync                              │
          ▼                          ▼                                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │         FastAPI modular monolith (SQLAlchemy 2.0, Pydantic v2)          │
  │ tenants (replika) · accounts · catalog · inventory · procurement        │
  │ sales · pricing · customers · finance · orders · hr · integrations      │
  │ outbox                                                                  │
  └───┬───────────────┬─────────────────┬──────────────────────┬────────────┘
      │               │                 │ outbox relay         │
  PostgreSQL        Redis               ▼                      │
  (RLS, FTS)   (cache, OTP, locks,    Kafka ◄──────────────────┼──────────────┐
                rate limit)             │                      │              │
                              ┌─────────┼────────────┐         │              │
                              ▼         ▼            ▼         ▼              │
  RabbitMQ ──► Celery     Analytics  Delivery   (OpenSearch)  Platform va Billing
      │                   (FastAPI)  (FastAPI)    [OPT]       (Django + DRF)
      └──► Notification   Postgres / PostGIS +                Django admin,
           servisi        ClickHouse WebSocket                o'z Postgres'i,
                          [OPT]                               Celery, Payme/Click

  Observability: OpenTelemetry · Prometheus · Grafana · Loki · Sentry
```

### Nima qayerda

| Qism | Joyi | Sababi |
|---|---|---|
| Auth, katalog, ombor, xarid, sotuv, narxlar, mijozlar, moliya, buyurtmalar, HR | Monolith (FastAPI) | Kuchli izchillik kerak: sotuv, stock, to'lov, mijoz balansi, promo-kod limiti bitta tranzaksiyada |
| Tenant reyestri, tariflar, obunalar, to'lovlar, platforma xodimlari, impersonation | Platform va Billing servisi (Django + DRF) | Control plane: CRUD va xodimlar jarayonlari, Django admin; data plane'dan alohida xavfsizlik chegarasi. Monolith'da tenant'larning faqat o'qiladigan replikasi |
| Notification | Alohida servis | Oddiy, faqat buyruq qabul qiladi |
| Analytics | Alohida servis (FastAPI) | Faqat o'qiydi, og'ir so'rovlar, alohida saqlash (ClickHouse) |
| Delivery | Alohida servis (FastAPI) | Real-time, geo, alohida masshtablanadi |

### Texnologiyalar xaritasi

| Texnologiya | Bosqich | Vazifasi |
|---|---|---|
| FastAPI + Pydantic v2 | 0 dan | Monolith, Analytics, Delivery |
| SQLAlchemy 2.0 (async) + asyncpg | 0 dan | ORM, Unit of Work |
| Alembic | 0 dan | Migratsiyalar |
| Jinja2 + HTMX | 0 dan | Back-office interfeysi |
| Django + DRF + Django admin | 15 | Platform va Billing servisi |
| PostgreSQL | 0 dan | RLS, partitioning, FTS, `pg_trgm`, PostGIS |
| Docker, Compose | 0 dan | Lokal muhit |
| GitHub Actions | 0 (CI), 21 (CD) | Lint, test, build, deploy |
| JWT, OTP, TOTP | 1, 15 | Auth, 2FA |
| Redis | 1 dan | Cache, OTP, rate limit, distributed lock, pub/sub |
| Celery + RabbitMQ | 9, 15 | Fon vazifalari, import/export, billing jadvallari |
| FastAPI WebSocket | 9 `[EXT]` | Masofadan tasdiqlash, jonli dashboard |
| React + TypeScript (PWA, IndexedDB) | 12 | Offline POS terminali |
| Kafka | 13 dan | Domain event'lar oqimi |
| ClickHouse | 16 `[OPT]` | Analitik saqlash |
| OpenSearch | 10 `[OPT]` | Mahsulot qidiruvi (Postgres yetmasa) |
| Prometheus, Grafana, Loki, OpenTelemetry, Sentry | 20 | Observability |
| Kubernetes, Helm | 21 | Deploy |

---

# Bosqichlar

## 0-bosqich: Tayyorgarlik
**Batafsil:** `roadmap/00-tayyorgarlik.md` · **Oldingi shart:** yo'q

- [ ] `[CORE]` Repo, branch himoyasi, conventional commits
- [ ] `[CORE]` `uv`, `pyproject.toml`, lock fayl
- [ ] `[CORE]` Modulli struktura: har domen modulida router, sxemalar, service, repository, modellar
- [ ] `[CORE]` Application factory va lifespan (ulanishlarni ochish va yopish)
- [ ] `[CORE]` Pydantic Settings bilan konfiguratsiya, environment o'zgaruvchilari, barcha vaqtlar UTC va timezone-aware
- [ ] `[CORE]` Async SQLAlchemy engine va sessiya, Alembic, Unit of Work asosi
- [ ] `[CORE]` Multi-stage Dockerfile, Compose (Postgres, Redis), healthcheck
- [ ] `[CORE]` Liveness va readiness endpoint'lari
- [ ] `[CORE]` Ruff, mypy, pre-commit, pytest (async), httpx, Testcontainers
- [ ] `[CORE]` CI: lint, mypy, test, Alembic migratsiyalari tekshiruvi
- [ ] `[CORE]` ADR'lar: modular monolith; nima uchun monolith FastAPI'da, Platform servisi esa Django'da; async yoki sync; repository va Unit of Work; frontend (back-office Jinja2 + HTMX, POS terminal 12-bosqichda PWA)

**Tugash mezoni:** `make up` bilan loyiha ko'tariladi, CI yashil.

---

## 1-bosqich: Tenancy, auth va RBAC
**Batafsil:** `roadmap/01-tenancy-auth.md` · **Oldingi shart:** 0

### Tenancy
- [ ] `[CORE]` `Tenant`, `Domain`, subdomain validatsiyasi, tenant'ni aniqlovchi middleware, Redis cache. Jadvallar shunday loyihalanadiki, 15-bosqichda ular Platform servisidan keladigan replikaga aylanadi
- [ ] `[CORE]` `Location` (filial va ombor bitta modelda: `type = store | warehouse`)
- [ ] `[CORE]` Tenant mixin, SQLAlchemy **global filtr** (fail closed), `contextvars`
- [ ] `[CORE]` DB role'lar, RLS (`ENABLE` + `FORCE`), RLS qamrovi testi
- [ ] `[CORE]` Tenant sozlamalari: valyuta, vaqt zonasi, soliq rejimi, chek formati

### Auth
- [ ] `[CORE]` Global `User` + `Membership`, telefon E.164
- [ ] `[CORE]` Parol hashing (Argon2), auth'ni **o'zingiz** qurasiz (tayyor kutubxonasiz)
- [ ] `[CORE]` API standartlari: yagona xato formati, `/api/v1/`, OpenAPI hujjatlari
- [ ] `[CORE]` JWT (rotation, reuse detection, tenant claim tekshiruvi), back-office uchun server tomonidagi sessiya (Redis)
- [ ] `[CORE]` CSRF himoyasi (cookie'li sessiya uchun o'zingiz qo'shasiz)
- [ ] `[CORE]` Telefon OTP (hash, TTL, urinishlar, cooldown, atomik tekshiruv, enumeration himoyasi)
- [ ] `[CORE]` TOTP 2FA (tenant egalari va menejerlar uchun; platforma xodimlari 2FA'si 15-bosqichda Django'da)
- [ ] `[CORE]` Rate limiting (sliding window)

### RBAC
- [ ] `[CORE]` **Permission kodlari kodda** qat'iy belgilangan: `sale.create`, `sale.refund`, `sale.void`, `sale.discount.manual`, `product.read`, `product.update_price`, `inventory.adjust`, `inventory.transfer`, `inventory.transfer.approve`, `purchase.create`, `purchase.approve`, `customer.credit.manage`, `finance.view`, `report.view`, `report.export`, `staff.manage`, `settings.manage`
- [ ] `[CORE]` **Rollar ma'lumot sifatida** (`Role` modeli, tenant'ga tegishli), permission'lar to'plami bilan
- [ ] `[CORE]` Standart rollar yangi tenant'ga seed qilinadi: Owner, Admin, Branch Manager, Cashier, Warehouse Manager, Accountant, Sales Manager
- [ ] `[CORE]` Filial darajasidagi ruxsat: `Membership` → ruxsat berilgan `Location` lar
- [ ] `[CORE]` Ruxsatlar **dependency injection** orqali (endpoint'da kerakli permission kodi), obyekt darajasida filial tekshiruvi, boshqa tenant/filial uchun `404`
- [ ] `[EXT]` Tenant o'z rollarini yaratadi. **Privilege escalation himoyasi:** foydalanuvchi faqat o'zida bor permission'larni boshqaga bera oladi
- [ ] `[CORE]` Rol × permission × endpoint matritsa testi

### Platforma operatsiyalari (15-bosqichgacha vaqtinchalik)
- [ ] `[CORE]` Tenant yaratish: UI'siz, ichki CLI buyrug'i va faqat ichki tarmoqdan ochiq endpoint orqali
- [ ] `[CORE]` Tenant yaratish **idempotent buyruq** sifatida loyihalanadi: 15-bosqichda u Platform servisidan kelgan event'ni qayta ishlovchi handler'ga aylanadi
- [ ] `[CORE]` Ichki operatsiyalar uchun RLS'ni chetlab o'tuvchi alohida DB role va alohida process
- [ ] `[CORE]` Invite, audit log (append-only)

**Tugash mezoni:** tenant izolyatsiyasi, RLS, OTP va RBAC testlari yashil.

---

## 2-bosqich: Katalog
**Qayerda:** `modules/catalog` · **Oldingi shart:** 1

### Mahsulot modeli
- [ ] `[CORE]` `Category` daraxti (ADR: adjacency list, materialized path, `ltree`), `Brand`
- [ ] `[CORE]` `Product` va `ProductVariant`: variant sotiladigan birlik (SKU). Atributlar (rang, o'lcham) uchun ADR: EAV, JSONB yoki alohida jadvallar
- [ ] `[CORE]` **Bir variantga bir nechta barcode:** alohida `Barcode` jadvali, tenant ichida unikal, turi (EAN-13, UPC, QR, ichki)
- [ ] `[CORE]` O'lchov birliklari; **tortiladigan mahsulotlar:** miqdor `Decimal(12, 3)`
- [ ] `[CORE]` Tarozi barcode'larini parse qilish (prefiksli EAN-13 ichidagi vazn yoki narx), check digit tekshiruvi
- [ ] `[CORE]` Arxivlash (soft delete): sotilgan mahsulotni butunlay o'chirib bo'lmaydi
- [ ] `[EXT]` **Bundle:** birga sotiladigan to'plam, sotilganda komponentlar stock'dan ayriladi
- [ ] `[EXT]` **Kit:** oldindan yig'iladigan mahsulot, o'z stock'i bor, "yig'ish" operatsiyasi komponentlarni kamaytirib kit'ni ko'paytiradi. Bundle bilan farqini ADR'da yozing
- [ ] `[EXT]` **Seriya raqami** bilan kuzatiladigan mahsulotlar: har birlik alohida (`in_stock`, `sold`, `returned`)
- [ ] `[EXT]` **Partiya (batch/lot) va yaroqlilik muddati:** `tracking = none | serial | batch`

### Narxlar (asos)
- [ ] `[CORE]` `PriceList` va `PriceListItem`: chakana (standart), ulgurji
- [ ] `[CORE]` Filialga xos narx (price list filialga bog'lanadi)
- [ ] `[CORE]` Narxlar tarixi
- [ ] `[CORE]` Narxni o'zgartirish `product.update_price` bilan va audit'ga yoziladi

### Qidiruv
- [ ] `[CORE]` Yagona qidiruv endpoint'i, ustuvorlik bilan: barcode (aniq) → SKU (aniq) → nom (`pg_trgm`)
- [ ] `[CORE]` **QR kod orqali qidirish:** QR ichida oddiy kod yoki havola bo'lishi mumkin; skaner natijasidan mahsulot identifikatorini ajratib olish va barcode qidiruviga yo'naltirish
- [ ] `[CORE]` Barcode va SKU bo'yicha qidiruv 10 ms dan tez (index bilan tasdiqlang)

**Tushunchalar:** polimorf mahsulot modeli, EAV va JSONB, constraint'lar, trigram index, check digit.
**Tugash mezoni:** kassir barcode, tarozi barcode'i, SKU yoki nom bo'yicha mahsulotni topadi; filial va ulgurji narxlar to'g'ri aniqlanadi.

---

## 3-bosqich: Ombor va warehouse'lar
**Qayerda:** `modules/inventory` · **Oldingi shart:** 2

### Stock asoslari
- [ ] `[CORE]` `StockMovement` ledger (o'zgarmas): `receive`, `sale`, `return`, `transfer_out`, `transfer_in`, `adjustment`, `count`, `assembly`
- [ ] `[CORE]` `StockLevel` (lokatsiya × variant): `on_hand`, `reserved`, `available = on_hand − reserved`; `CHECK` constraint'lar
- [ ] `[CORE]` Minimal qoldiq va reorder level; ulardan tushganda low-stock hodisasi
- [ ] `[CORE]` Reconciliation: `on_hand` == movement'lar yig'indisi
- [ ] `[CORE]` Movement tarixi: filtrlar, cursor pagination
- [ ] `[EXT]` Partiya va seriya bo'yicha movement'lar; **FEFO** (muddati birinchi tugaydigan birinchi chiqadi)

### Adjustment va inventarizatsiya
- [ ] `[CORE]` Adjustment sabablari bilan: `damaged`, `expired`, `lost`, `found`, `correction`
- [ ] `[CORE]` Belgilangan summadan katta adjustment tasdiqlashni talab qiladi
- [ ] `[CORE]` Inventarizatsiya sessiyasi: to'liq va qisman (cycle count); sanash davomida sotuvlar davom etsa, boshlang'ich snapshot va delta bilan hisoblash
- [ ] `[CORE]` Farqlar hisoboti → tasdiqlash → avtomatik adjustment'lar
- [ ] `[EXT]` Muddati o'tgan partiyalarni avtomatik aniqlash (Celery beat, 9-bosqichdan keyin)

### Transfer va rezervatsiya
- [ ] `[CORE]` Transfer so'rovi → tasdiqlash → yig'ish → jo'natildi (**yo'ldagi stock**) → qabul qilindi
- [ ] `[CORE]` Ombor → filial va filial → filial transferlari
- [ ] `[CORE]` Qisman qabul va tafovutlar (kam kelgan, shikastlangan)
- [ ] `[CORE]` Rezervatsiya: muddati bilan (hold qilingan sotuv, e-commerce buyurtmasi, transfer); muddati o'tgani avtomatik bo'shatiladi
- [ ] `[CORE]` Rezervatsiyada concurrency: ikki parallel rezervatsiya `available` dan oshib ketmasligi

### Warehouse operatsiyalari
- [ ] `[EXT]` Ombor ichida zona va yacheyka (bin)
- [ ] `[EXT]` Qabul → put-away (yacheykaga joylash)
- [ ] `[EXT]` **Ichki transfer (internal transfer):** bir lokatsiya ichida yacheykadan yacheykaga ko'chirish; umumiy `on_hand` o'zgarmaydi, faqat joylashuv o'zgaradi, lekin movement baribir yoziladi
- [ ] `[EXT]` Picking list (transfer va buyurtmalar uchun), yig'ish marshruti

**Tushunchalar:** ledger, available-to-promise, yo'ldagi stock, holat mashinalari, rezervatsiya concurrency'si.
**Tugash mezoni:** har qanday operatsiyalardan keyin reconciliation mos keladi; parallel rezervatsiyalar testi yashil.

---

## 4-bosqich: Xarid (procurement)
**Qayerda:** `modules/procurement` · **Oldingi shart:** 3

- [ ] `[CORE]` `Supplier`: kontaktlar, to'lov shartlari
- [ ] `[EXT]` Xarid so'rovi: filialdan yoki reorder level'dan avtomatik
- [ ] `[CORE]` Purchase order holatlari: `draft → pending_approval → approved → sent → partially_received → received → closed / cancelled`
- [ ] `[CORE]` Summaga qarab tasdiqlash qoidasi (`purchase.approve`)
- [ ] `[CORE]` Tovar qabul qilish: qisman qabul, kam yoki ortiq kelgan tovar, partiya va muddatlarni kiritish, stock movement'lar
- [ ] `[CORE]` **Tannarx hisobi:** qabulda o'rtacha tortilgan tannarx (WAC) qayta hisoblanadi. Parallel qabullarda lock kerak. ADR: WAC va FIFO
- [ ] `[CORE]` Yetkazib beruvchiga qaytarish
- [ ] `[CORE]` Yetkazib beruvchi qarzi (kreditorlik): qabuldan invoice, qisman to'lovlar, balans ledger'dan
- [ ] `[CORE]` Xaridlar tarixi
- [ ] `[EXT]` Yetkazib beruvchi samaradorligi (yetkazish muddati, tafovutlar ulushi)
- [ ] `[OPT]` Landed cost: transport xarajatlarini tannarxga taqsimlash

**Tushunchalar:** hujjat workflow'i, tasdiqlash oqimi, tannarx usullari, kreditorlik ledger'i.
**Tugash mezoni:** qisman qabul, qaytarish va to'lovdan keyin stock, tannarx va qarz to'g'ri.

---

## 5-bosqich: POS sotuvlar (eng muhim bosqich)
**Qayerda:** `modules/sales` · **Oldingi shart:** 4

### Savat (cart)
- [ ] `[CORE]` ADR: savat serverda (`Sale`, `draft` holatida) yoki klientda. Tavsiya: serverda, chunki hold va tiklash uchun kerak
- [ ] `[CORE]` Barcode, SKU yoki qidiruv orqali qo'shish; miqdorni o'zgartirish; tortiladigan mahsulotlar
- [ ] `[CORE]` Qo'lda kiritilgan (manual) mahsulot: katalogsiz, alohida permission, stock'ga ta'sir qilmaydi
- [ ] `[CORE]` Qo'lda chegirma (qator va chek darajasida): permission va maksimal foiz; limitdan oshsa, menejer tasdig'i
- [ ] `[CORE]` **Soliq (QQS):** narx ichida yoki ustiga, mahsulotga xos stavka, yaxlitlash qoidasi (qator yoki chek darajasida, ADR), qatorda snapshot
- [ ] `[CORE]` Sotuvni hold qilish va keyin davom ettirish; hold muddati; ADR: hold stock'ni rezerv qiladimi

### To'lov
- [ ] `[CORE]` Naqd (berilgan summa, qaytim), karta (terminal referensi)
- [ ] `[CORE]` **Aralash to'lov** (masalan, 100 000 naqd + 200 000 karta); yakunlashda `sum(to'lovlar) == jami`
- [ ] `[CORE]` Mijoz balansi va nasiya to'lov usuli sifatida (7-bosqichda ulanadi)

### Yakunlash
- [ ] `[CORE]` Bitta tranzaksiya: validatsiya → stock lock (`variant_id` bo'yicha tartiblangan) → kamaytirish → movement'lar → to'lovlar → snapshot'lar (narx, tannarx, soliq, chegirma) → `completed`
- [ ] `[CORE]` `Idempotency-Key`
- [ ] `[CORE]` **Uzluksiz chek raqamlari** filial bo'yicha: Postgres sequence'larida bo'shliqlar bo'ladi, shuning uchun hisoblagich qatori row lock (`with_for_update`) bilan. Narxini o'lchang

### Chek
- [ ] `[CORE]` Chek chiqarish (printer uchun matn yoki PDF)
- [ ] `[CORE]` Elektron chek: havola va QR kod (SMS/Telegram orqali yuborish 14-bosqichda)
- [ ] `[CORE]` Chek dublikati: "DUBLIKAT" belgisi bilan, audit'ga yoziladi

### Sotuvdan keyingi operatsiyalar
- [ ] `[CORE]` **Void:** yakunlanmagan sotuvni bekor qilish; yakunlanganini shu smena ichida to'liq storno qilish (`sale.void`, menejer tasdig'i)
- [ ] `[CORE]` **Qaytarish (refund):** asl chek bo'yicha; qisman (qatorlar va miqdorlar); sotilgandan va avval qaytarilgandan ko'p qaytarib bo'lmaydi (parallel qaytarishlarda concurrency); to'lov usuliga qaytarish qoidalari; stock'ga qaytarish yoki shikastlangan deb yozish
- [ ] `[CORE]` **Almashtirish (exchange):** qaytarish + yangi sotuv, bog'langan; farq to'lanadi yoki qaytariladi
- [ ] `[EXT]` Cheksiz qaytarish (siyosat bilan)

### Menejer tasdig'i (step-up authorization)
- [ ] `[CORE]` Oqim: kassir so'rov yuboradi → menejer shu terminalda PIN kiritadi → operatsiya bajariladi
- [ ] `[CORE]` PIN hash qilingan, urinishlar limiti bilan
- [ ] `[CORE]` Tasdiq tokeni: bir martalik, aniq operatsiya va summaga bog'langan, 2 daqiqa amal qiladi
- [ ] `[CORE]` Audit: kim so'radi, kim tasdiqladi, nima uchun
- [ ] `[EXT]` Masofadan tasdiqlash: menejer telefoniga so'rov keladi (WebSocket, 9-bosqichdan keyin)

### Smena va kassa
- [ ] `[CORE]` Smena ochish/yopish; boshlang'ich naqd; kassaga kirim va chiqim
- [ ] `[CORE]` Kutilgan va sanalgan naqd farqi; X va Z hisobotlar

### Concurrency va yuklama
- [ ] `[CORE]` Deadlock'ni ataylab chiqarish va tuzatish; retry
- [ ] `[CORE]` Optimistic locking bilan solishtirish; isolation level tajribasi
- [ ] `[CORE]` Locust: 50 parallel kassir; natijalar README'da

**Tushunchalar:** ACID, lock'lar, deadlock, isolation anomaliyalari, idempotency, gapless sequence, step-up authorization, soliq va yaxlitlash.
**Tugash mezoni:** yuklama testida stock minusga tushmaydi, sotuv ikki marta yozilmaydi; qisman qaytarish, almashtirish va void to'g'ri ishlaydi.

> **Ish qidirish belgisi:** 9 va 10-bosqichlar bilan birga 1-daraja MVP tugaydi. Rezyumeni yangilab, ariza bering.

---

## 6-bosqich: Narxlar va aksiyalar engine'i
**Qayerda:** `modules/pricing` · **Oldingi shart:** 5

- [ ] `[CORE]` Narx aniqlash tartibi (ADR): mijozga xos narx → filial narxi → mijoz guruhi (ulgurji) → asosiy chakana
- [ ] `[CORE]` `Promotion` modeli: **shartlar** (mahsulotlar, kategoriya, brend, filial, mijoz guruhi, minimal miqdor yoki summa, sana oralig'i, hafta kunlari, soat oralig'i) va **foyda** (foiz, qat'iy summa, qat'iy narx, bepul mahsulot)
- [ ] `[CORE]` Foiz, qat'iy summa, kategoriya va brend chegirmalari
- [ ] `[CORE]` **Buy X Get Y** (2+1 va boshqalar): qaysi mahsulot bepul (odatda eng arzoni), bir chekda takroriy qo'llanish
- [ ] `[CORE]` Vaqtga bog'liq aksiyalar va **happy hour**: tenant vaqt zonasi bo'yicha
- [ ] `[CORE]` Birlashtirish qoidalari: ustuvorlik, eksklyuziv aksiyalar, bir qatorga nechta aksiya; natija **deterministik**
- [ ] `[CORE]` **Kupon** (bir martalik unikal kodlar) va **promo-kod** (umumiy kod, jami va har mijoz uchun limit)
- [ ] `[CORE]` Promo-kod limiti concurrency'si: atomik `UPDATE ... WHERE used < limit`; yakunlashda ishlatiladi, void'da qaytariladi
- [ ] `[CORE]` Qo'llangan aksiyalar sotuv qatorlarida snapshot sifatida
- [ ] `[CORE]` **Chek chegirmasini qatorlarga taqsimlash** (largest remainder), shunda qisman qaytarishda summa to'g'ri chiqadi
- [ ] `[CORE]` Engine **sof funksiya** (ichida DB so'rovi yo'q): kirish savat va qoidalar, chiqish narxlar
- [ ] `[CORE]` Property-based testlar (`hypothesis`): jami hech qachon manfiy emas, qatorlar yig'indisi jamiga teng
- [ ] `[EXT]` Aksiyani oldindan ko'rish (simulation) endpoint'i

**Tushunchalar:** strategy pattern, rules engine, sof funksiyalar, property-based testing, pul taqsimlashda yaxlitlash.
**Tugash mezoni:** har qanday savat uchun natija deterministik va property testlari yashil.

---

## 7-bosqich: Mijozlar va loyalty
**Qayerda:** `modules/customers` · **Oldingi shart:** 6

- [ ] `[CORE]` `Customer` (telefon tenant ichida unikal), guruhlar (chakana, ulgurji, VIP), xaridlar tarixi
- [ ] `[CORE]` Sotuvga mijozni biriktirish
- [ ] `[CORE]` **Loyalty ballari** ledger'da: yig'ish, sarflash, muddati tugashi, qaytarishda bekor qilish
- [ ] `[CORE]` Ball yig'ish qoidalari; ballarni to'lov yoki chegirma sifatida ishlatish
- [ ] `[CORE]` **Mijoz balansi (store credit):** ledger, to'ldirish, POS'da to'lov usuli, qaytarishni balansga o'tkazish
- [ ] `[CORE]` **Nasiya (mijoz qarzi)** kredit limiti bilan: ikki terminalda bir vaqtda sotuv limitdan oshmasligi uchun mijoz hisobi qatori lock qilinadi
- [ ] `[CORE]` Qarzni to'lash, mijoz uchun hisob-kitob varaqasi
- [ ] `[EXT]` Keshbek balansga
- [ ] `[EXT]` Tug'ilgan kun aksiyalari (Celery beat, tenant vaqt zonasi)
- [ ] `[EXT]` Ballar muddatini avtomatik tugatish

**Tushunchalar:** ledger, balans izchilligi, hisob darajasidagi lock'lar.
**Tugash mezoni:** parallel sotuvlar kredit limitini buzmaydi; qaytarishdan keyin ballar va balans to'g'ri.

---

## 8-bosqich: Moliya
**Qayerda:** `modules/finance` · **Oldingi shart:** 7

- [ ] `[CORE]` To'lov tranzaksiyalari ledger'i: sotuvlar, qaytarishlar, yetkazib beruvchi to'lovlari, mijoz to'lovlari, xarajatlar
- [ ] `[CORE]` Filial va smena bo'yicha kassa qoldig'i
- [ ] `[CORE]` Xarajatlar kategoriyalari bilan
- [ ] `[CORE]` Hisobotlar: tushum, tannarx (COGS, sotuvdagi snapshot'dan), yalpi foyda (davr va filial bo'yicha)
- [ ] `[CORE]` Debitorlik (mijozlar qarzi) va kreditorlik (yetkazib beruvchilar qarzi), muddat bo'yicha tahlil (0–30, 31–60, 61–90, 90+ kun)
- [ ] `[EXT]` Pul oqimi (cash flow) hisoboti
- [ ] `[EXT]` **Soddalashtirilgan double-entry:** `JournalEntry` va qatorlar; debet = kredit bazada kafolatlangan (deferred constraint trigger); har biznes hujjati o'z yozuvlarini hosil qiladi; xato storno yozuvi bilan tuzatiladi
- [ ] `[EXT]` Davrni yopish: yopilgan davrga yozish taqiqlanadi

**Tushunchalar:** double-entry, o'zgarmaslik, storno, davr yopish.
**Tugash mezoni:** yalpi foyda hisoboti tannarx snapshot'lari bilan qo'lda hisoblangan natijaga mos keladi.

---

## 9-bosqich: Async ishlar, cache va ommaviy operatsiyalar
**Qayerda:** `worker/`, modullarning `tasks.py` fayllari · **Oldingi shart:** 5 (6–8 bilan parallel bo'lishi mumkin)

- [ ] `[CORE]` RabbitMQ broker, Celery; task'lar `tenant_id` bilan; task'lar faqat **commit'dan keyin** yuboriladi (Unit of Work commit'dan keyin navbatdagi task'larni jo'natadi)
- [ ] `[CORE]` Worker'lar uchun sinxron SQLAlchemy sessiyasi (Celery sinxron). ADR: Celery yoki async alternativalar (arq, taskiq)
- [ ] `[CORE]` Retry, backoff, `acks_late`, idempotent task'lar, alohida navbatlar, Celery beat, Flower
- [ ] `[CORE]` OTP va invite yuborishni Celery'ga o'tkazish
- [ ] `[CORE]` Redis cache (katalog, narxlar, domenlar), tenant prefiksi, invalidation, stampede himoyasi
- [ ] `[CORE]` **Distributed lock** (Redis, TTL va token bilan): masalan, tungi job faqat bitta nusxada ishlashi uchun. ADR: nima uchun stock uchun Redis lock emas, DB lock ishlatiladi; Redlock atrofidagi bahslar
- [ ] `[CORE]` **Import/export:** katta CSV/Excel mahsulot importi asinxron, progress, xatolar hisoboti, qayta yuklashda dublikat yo'q
- [ ] `[CORE]` **Ommaviy operatsiyalar:** narxlarni ommaviy yangilash, `bulk_create` va RLS
- [ ] `[EXT]` FastAPI WebSocket: masofadan tasdiqlash va jonli dashboard; bir nechta instans uchun Redis pub/sub

**Tushunchalar:** navbat va cache, at-least-once, distributed lock'larning cheklovlari, cache invalidation.
**Tugash mezoni:** worker o'chirib yoqilganda task'lar yo'qolmaydi; 100 000 qatorli import xotira muammosisiz o'tadi.

---

## 10-bosqich: Hajm, performance va qidiruv
**Oldingi shart:** 9

- [ ] `[CORE]` Seed: 10M+ sotuv qatori, bir juda katta tenant
- [ ] `[CORE]` `EXPLAIN (ANALYZE, BUFFERS)`; composite, partial, covering, BRIN, GIN index'lar; `pg_stat_statements`
- [ ] `[CORE]` N+1: so'rovlar sonini hisoblovchi test yordamchisi; eager loading strategiyalari (`selectinload`, `joinedload`); async'da lazy loading'ni butunlay o'chirish (`raise` strategiyasi)
- [ ] `[CORE]` Filtrlash va saralash faqat ruxsat etilgan maydonlar bo'yicha (whitelist), cursor pagination
- [ ] `[CORE]` Soft delete va `WHERE deleted_at IS NULL` partial index'lari
- [ ] `[CORE]` Sotuvlar jadvalini oy bo'yicha partitioning
- [ ] `[CORE]` Yig'indi jadvallari yoki materialized view
- [ ] `[CORE]` **Full-text qidiruv:** `tsvector` + `pg_trgm`; o'zbek (lotin va kirill) va rus tillari; lotin-kirill transliteratsiyasi
- [ ] `[CORE]` PgBouncer: transaction pooling va `SET LOCAL`; asyncpg prepared statement'lari bilan muammo va uning yechimi
- [ ] `[CORE]` SQLAlchemy connection pool sozlamalari: hajm, overflow, timeout; pool tugab qolganda nima bo'lishini o'lchash
- [ ] `[OPT]` OpenSearch: event'lar orqali sinxronlanadigan indeks; ADR: Postgres qachon yetmaydi

**Tushunchalar:** B-tree, query planner, partition pruning, FTS, connection pooling.
**Tugash mezoni:** har hisobot uchun oldin/keyin natijalar README'da.

---

## 11-bosqich: HR (minimal)
**Qayerda:** `modules/hr` · **Oldingi shart:** 10

- [ ] `[CORE]` `Employee` (User va Membership bilan bog'liq), lavozim, lokatsiya
- [ ] `[CORE]` Ishga olish: `candidate → interview → offer → hired`; `hired` bo'lganda Membership va rol yaratiladi
- [ ] `[EXT]` Ish jadvali, davomat
- [ ] `[EXT]` Kassir KPI
- [ ] `[OPT]` Ikkinchi Django tajribasi sifatida HR'ni alohida Django servisiga chiqarish (faqat Platform servisi tugagandan keyin; a'zoliklar monolith'da qolgani uchun bog'liqlikni event'lar orqali hal qilish kerak bo'ladi)

**Tugash mezoni:** asosiy oqim ishlaydi. Kengaytirmang.

---

## 12-bosqich: Offline POS
**Qayerda:** `pos-terminal/` (React + TypeScript PWA), `modules/sync` · **Oldingi shart:** 7 va 9

### Terminal
- [ ] `[CORE]` ADR: PWA + IndexedDB yoki kichik desktop ilova (SQLite)
- [ ] `[CORE]` Qurilmani ro'yxatdan o'tkazish: har terminal filialga bog'langan, alohida device credential'lari
- [ ] `[CORE]` Katalog, narxlar, aksiyalar va mijozlar snapshot'ini yuklab olish
- [ ] `[CORE]` Inkremental sinxronizatsiya: `updated_since` kursori, o'chirilganlar uchun tombstone'lar

### Offline sotuv
- [ ] `[CORE]` Sotuv klientda yaratilgan UUID bilan
- [ ] `[CORE]` Offline chek raqamlari: qurilma prefiksi bilan (global uzluksiz raqam offline'da imkonsiz)
- [ ] `[CORE]` **Narxlash muammosi:** aksiyalar engine'i klientda ham kerak. ADR: qoidalarni ma'lumot sifatida ulashish; server qayta hisoblaydimi yoki klient narxini siyosat doirasida qabul qiladimi
- [ ] `[CORE]` Offline siyosati: maksimal offline davomiylik va summa; offline'da qaytarish va nasiya mumkinmi

### Sinxronizatsiya
- [ ] `[CORE]` Klient outbox'i, batch yuklash, backoff bilan retry
- [ ] `[CORE]` Serverda idempotency (UUID unikal), tartibsiz kelgan batch'lar
- [ ] `[CORE]` **Konfliktlar:** stock minusga ketdi (sotuv jismonan bo'lgan: qabul qilinadi, belgilanadi, ogohlantirish), narx o'zgargan (klient narxi saqlanadi, audit), promo-kod limiti oshgan, kredit limiti oshgan, mahsulot o'chirilgan
- [ ] `[CORE]` Soat farqi: qurilma vaqti va server vaqti alohida saqlanadi
- [ ] `[CORE]` Testlar: tarmoq uzilishi, takroriy yuklash, tartibsiz kelish

**Tushunchalar:** local-first, eventual consistency, sinxronizatsiya protokoli, idempotency, konflikt hal qilish.
**Tugash mezoni:** terminal 1 soat offline ishlab, qayta ulanganda barcha sotuvlar dublikatsiz va konfliktlar hisoboti bilan sinxronlanadi.

---

## 13-bosqich: Event'lar va ajratishga tayyorgarlik
**Oldingi shart:** 12

- [ ] `[CORE]` `import-linter` bilan modul chegaralari
- [ ] `[CORE]` Ajraladigan qismlar bilan modullararo JOIN va FK'larni olib tashlash
- [ ] `[CORE]` Domain event'lar: `sale.completed.v1`, `sale.refunded.v1`, `stock.changed.v1`, `stock.low.v1`, `order.ready_for_delivery.v1`, `customer.created.v1`
- [ ] `[CORE]` Event konverti, sxemalar, versiyalash
- [ ] `[CORE]` **Sinxron va asinxron chegarasi** (ADR). `SaleCompleted` dan keyin:

```
Sotuv tranzaksiyasi ichida (sinxron):   stock, to'lovlar, promo-kod, kredit limiti
Outbox → Kafka orqali (asinxron):        elektron chek, bildirishnomalar, analitika,
                                         moliyaviy yozuvlar [EXT], loyalty (ADR)
```

- [ ] `[CORE]` Transactional outbox, relay (`FOR UPDATE SKIP LOCKED`)
- [ ] `[CORE]` Kafka (KRaft), `tenant_id` bo'yicha partitioning
- [ ] `[CORE]` Correlation ID, structlog
- [ ] `[CORE]` CI bir nechta image build qiladi

**Tugash mezoni:** "Ajratish shartlari" to'liq bajarilgan.

---

## 14-bosqich: Notification servisi
**Qayerda:** `services/notification` · **Oldingi shart:** 13

- [ ] `[CORE]` RabbitMQ consumer: SMS, Telegram, email buyruqlari
- [ ] `[CORE]` Elektron chekni yuborish
- [ ] `[CORE]` Platform servisidan keladigan xabarlar: tenant egasiga taklif, to'lov eslatmalari
- [ ] `[CORE]` Idempotent consumer, DLQ, kechikishli retry
- [ ] `[CORE]` Monolith'dagi eski kodni o'chirish
- [ ] `[EXT]` Tenant egasi uchun Telegram bot: kunlik hisobot

---

## 15-bosqich: Platform va Billing servisi (Django + DRF)
**Qayerda:** `services/platform` · **Oldingi shart:** 14

**Nima uchun Django (ADR):** bu servis SaaS'ning control plane'i. U asosan CRUD va xodimlar jarayonlaridan iborat, yuklama sinxron, va Django admin, auth, ORM hamda migratsiyalar bu yerda eng ko'p vaqt tejaydi. Bundan tashqari, bitta loyihada ikkala framework'ni real vazifada solishtirasiz.

### Asos
- [ ] `[CORE]` Django loyihasi, alohida PostgreSQL bazasi, DRF, settings bo'linishi; Docker va CI standartlari monolith bilan bir xil
- [ ] `[CORE]` Django tuzilmasi: app'lar, har birida service layer (biznes logika view va serializer'da emas)
- [ ] `[CORE]` pytest-django, factory_boy, Testcontainers
- [ ] `[CORE]` Celery Django integratsiyasi bilan (RabbitMQ broker)

### Django admin va platforma xodimlari
- [ ] `[CORE]` Platforma xodimlari uchun Django admin: custom AdminSite, faqat alohida host'da
- [ ] `[CORE]` Ruxsatlar Django'ning o'rnatilgan **Group va Permission** tizimi bilan. Monolith'dagi RBAC bilan farqini ADR'da yozing: bu yerda xodimlar global, tenant'larga bo'linmagan, shuning uchun o'rnatilgan tizim aynan mos
- [ ] `[CORE]` Platforma xodimlari uchun majburiy TOTP 2FA
- [ ] `[CORE]` Admin'dagi custom action'lar va view'lar: tenant'ni suspend qilish, tarifni o'zgartirish, MRR dashboard'i
- [ ] `[CORE]` Audit log: Django admin log'i va o'z audit jadvalingiz

### Tenant reyestriga egalikni ko'chirish
- [ ] `[CORE]` Tenant, Domain va tariflar endi **shu servisga tegishli** (ADR, strangler fig). Monolith ulardan faqat o'qiladigan replikani saqlaydi
- [ ] `[CORE]` Event'lar: `tenant.created.v1`, `tenant.updated.v1`, `tenant.status_changed.v1`, `domain.changed.v1`, `entitlements.changed.v1`
- [ ] `[CORE]` Monolith'da replikani yangilovchi idempotent consumer; tartibsiz kelgan event'lar uchun versiya tekshiruvi
- [ ] `[CORE]` Eventual consistency oqibati: yangi tenant subdomain'i event qayta ishlangandan keyin ishlaydi; oraliq `provisioning` holati uchun sahifa
- [ ] `[CORE]` Mavjud tenant'larni ko'chirish: bir martalik migratsiya, keyin ikki tomon natijalarini solishtirish

### Tenant provisioning saga (orchestration)
- [ ] `[CORE]` Oqim: admin tenant yaratadi → Platform `provisioning` holatida saqlaydi → event → monolith standart lokatsiya, rollar, owner va a'zolikni yaratadi → `tenant.provisioned.v1` yoki `tenant.provisioning_failed.v1` → Platform tenant'ni faollashtiradi va Notification orqali taklif yuboradi
- [ ] `[CORE]` Timeout'lar, retry va compensating qadamlar
- [ ] `[CORE]` ADR: bu yerda **orchestration** (Platform boshqaradi), Delivery'da esa **choreography**. Ikkalasini solishtiring
- [ ] `[CORE]` Monolith provisioning paytida ishlamay qolsa, saga u tiklangandan keyin o'zi yakunlanadi

### Billing
- [ ] `[CORE]` `Plan`, `Subscription`, `Invoice`, `Payment`: modellar, DRF API va admin
- [ ] `[CORE]` Tenant holat mashinasi (`trial → active → past_due → suspended → cancelled`); har o'tish event chiqaradi, monolith replika orqali `suspended` sahifasini ko'rsatadi
- [ ] `[CORE]` **Entitlement'lar:** tarif limitlari (lokatsiyalar, xodimlar, terminallar) va feature flag'lar event orqali monolith'ga uzatiladi, monolith ularni lokal tekshiradi. ADR: nima uchun har so'rovda Platform'ga sinxron murojaat qilinmaydi
- [ ] `[CORE]` Payme/Click webhook'lari DRF'da: imzo, idempotency, summa tiyinlarda
- [ ] `[CORE]` Celery beat: invoice yaratish, eslatmalar, grace period, avtomatik suspend
- [ ] `[CORE]` To'lovlar reconciliation'i

### Impersonation va servislararo auth
- [ ] `[CORE]` Impersonation: Platform qisqa muddatli, asimmetrik kalit bilan imzolangan token beradi; monolith uni JWKS orqali tekshiradi va sessiyani "impersonated" deb belgilaydi; audit ikkala tomonda
- [ ] `[CORE]` Platform ↔ monolith ichki API'si uchun servis token'lari
- [ ] `[EXT]` Servislararo mTLS

### DRF tushunchalari
- [ ] `[CORE]` ViewSet va router'lar, serializer'lar, permission class'lari, throttling, django-filter, drf-spectacular
- [ ] `[CORE]` ADR: DRF serializer va Pydantic, DRF permission class va FastAPI dependency'lari, Django ORM va SQLAlchemy. Ikkala tomonda ham real tajriba bilan solishtirish
- [ ] `[EXT]` **Self-service ro'yxatdan o'tish:** ochiq DRF endpoint → trial tenant; telefon OTP, rate limiting, suiiste'moldan himoya

**Tushunchalar:** control plane va data plane, ma'lumotga egalikni ko'chirish, event orqali replika, orchestration saga, entitlement'lar, Django va FastAPI'ni solishtirish.
**Tugash mezoni:** Django admin'da yaratilgan tenant hech qanday qo'lda qadamsiz o'z subdomain'ida ishlay boshlaydi; to'lamagan tenant event'lar orqali monolith'da avtomatik suspend bo'ladi; provisioning paytida monolith o'chirilsa, saga tiklangandan keyin yakunlanadi.

---

## 16-bosqich: Analytics servisi (FastAPI)
**Qayerda:** `services/analytics` · **Oldingi shart:** 15

### Infratuzilma
- [ ] `[CORE]` FastAPI, async SQLAlchemy, Alembic, alohida baza
- [ ] `[CORE]` Kafka consumer, offset'ni yozishdan keyin commit, replay
- [ ] `[CORE]` Strangler fig: monolith hisobotlari bilan parallel, solishtirish, o'tkazish
- [ ] `[CORE]` JWKS orqali JWT (RS256), Pact contract testlar
- [ ] `[OPT]` **ClickHouse:** MergeTree, materialized view'lar; Postgres bilan solishtirish (ADR)

### Dashboard
- [ ] `[CORE]` Bugungi tushum, foyda, cheklar soni, o'rtacha chek, sotilgan mahsulotlar, qaytarishlar ulushi (event'lardan deyarli real-time)

### Chuqur tahlil
- [ ] `[CORE]` Sotuvlar: filial, kassir, kategoriya, mahsulot, soat, hafta kuni bo'yicha
- [ ] `[CORE]` Mahsulot bo'yicha foyda, top mijozlar
- [ ] `[CORE]` Sekin sotiladigan va "o'lik" stock
- [ ] `[CORE]` Stock aylanmasi (inventory turnover)
- [ ] `[CORE]` ABC tahlil
- [ ] `[EXT]` Low-stock prognozi (sirpanuvchi o'rtacha yoki exponential smoothing), reorder tavsiyasi

**Tugash mezoni:** baza noldan event'lardan tiklanadi va natijalar monolith bilan mos keladi.

---

## 17-bosqich: E-commerce kanali
**Qayerda:** `modules/orders` (monolith) · **Oldingi shart:** 16

- [ ] `[EXT]` Online buyurtma: umumiy stock'dan rezervatsiya (TTL bilan), to'lov, bajarish
- [ ] `[EXT]` Qaysi lokatsiyadan bajarish (ombor yoki eng yaqin filial), picking
- [ ] `[EXT]` Oversell'ning oldini olish: POS va online bir vaqtda oxirgi mahsulotni sotmoqchi
- [ ] `[EXT]` Online to'lov (Payme/Click), to'lanmagan buyurtmaning rezervi avtomatik bo'shatiladi
- [ ] `[EXT]` Tayyor buyurtma `order.ready_for_delivery.v1` event'ini chiqaradi

---

## 18-bosqich: Delivery servisi (FastAPI)
**Qayerda:** `services/delivery` · **Oldingi shart:** 17

- [ ] `[CORE]` PostGIS, zonalar, yetkazish narxi
- [ ] `[CORE]` Eng yaqin kuryer, atomik qabul qilish
- [ ] `[CORE]` Holat mashinasi, WebSocket kuzatish, Redis pub/sub va GEO
- [ ] `[CORE]` OTP bilan topshirishni tasdiqlash
- [ ] `[CORE]` Saga: muvaffaqiyatsiz yetkazish → refund va stock qaytarish
- [ ] `[CORE]` Playwright e2e: buyurtma → yetkazish → tasdiqlash

---

## 19-bosqich: Integratsiyalar
**Qayerda:** `modules/integrations` · **Oldingi shart:** 18 (bir qismini oldinroq qilish mumkin)

- [ ] `[CORE]` Adapter pattern: `PaymentProvider`, `FiscalProvider`, `SmsProvider`, `ReceiptPrinter` interfeyslari; testlar uchun fake'lar
- [ ] `[CORE]` Timeout, retry, circuit breaker
- [ ] `[CORE]` **Outbound webhook'lar** tenant tizimlariga: imzo, retry, yetkazish log'i
- [ ] `[EXT]` POS'da karta va QR to'lov provayderlari
- [ ] `[EXT]` Fiskal integratsiya: O'zbekistondagi amaldagi talablarni tekshiring, adapter va mock bilan
- [ ] `[EXT]` Chek printeri (ESC/POS), barcode skaner (klaviatura rejimi), elektron tarozi
- [ ] `[EXT]` Buxgalteriya tizimlariga eksport (masalan, 1C uchun fayl formatlari)

**Tushunchalar:** anti-corruption layer, circuit breaker, tashqi tizimlar ishonchsizligi.

---

## 20-bosqich: Observability
**Oldingi shart:** 19

- [ ] `[CORE]` Correlation ID: HTTP, Kafka, Celery
- [ ] `[CORE]` OpenTelemetry tracing: FastAPI, SQLAlchemy, Celery, Kafka
- [ ] `[CORE]` Prometheus: RED metrikalari, biznes metrikalar, consumer lag, navbat uzunligi, offline terminallar sinxronizatsiya kechikishi
- [ ] `[CORE]` **Loki** bilan markazlashgan log'lar
- [ ] `[CORE]` Grafana dashboard'lari va alert'lar, Sentry, SLI/SLO
- [ ] `[CORE]` Chaos tajribalari va postmortem'lar

---

## 21-bosqich: Kubernetes va CD
**Oldingi shart:** 20

- [ ] `[CORE]` k3d/kind, Helm chart'lar
- [ ] `[CORE]` Wildcard ingress, cert-manager (DNS-01)
- [ ] `[CORE]` Secret'lar, resource limitlar, probe'lar, migratsiya Job'i
- [ ] `[CORE]` Expand/contract bilan zero-downtime migratsiya
- [ ] `[CORE]` HPA va KEDA (navbat uzunligi bo'yicha)
- [ ] `[CORE]` CD: staging → tasdiqlash → production
- [ ] `[CORE]` Backup va restore'ni haqiqatan sinash
- [ ] `[CORE]` Haqiqiy VPS yoki cloud'ga deploy
- [ ] `[OPT]` ArgoCD bilan GitOps

---

# Microservice'ga ajratish shartlari

Biror modulni ajratishdan oldin **hammasi** bajarilgan bo'lishi kerak:

- [ ] Ma'lumotga egalik aniq: modul jadvallariga boshqa modullar to'g'ridan-to'g'ri murojaat qilmaydi, JOIN yo'q
- [ ] Aloqa faqat interfeys yoki event'lar orqali, `import-linter` buni majburlaydi
- [ ] Outbox ishlaydi, event'lar versiyalangan
- [ ] Correlation ID barcha log'larda bor
- [ ] CI bir nechta image'ni build qila oladi
- [ ] Ajratishning aniq sababi ADR'da yozilgan

---

# Nazariya yo'nalishlari (bosqichlar bilan parallel)

## Python ichki tuzilishi
**Qachon:** 1–9-bosqichlar davomida. **Manba:** *Fluent Python* (Luciano Ramalho)

- [ ] Decorator'lar va closure'lar
- [ ] Context manager'lar va `contextvars`
- [ ] Generator'lar va iterator protokoli
- [ ] Descriptor'lar (SQLAlchemy ustunlari va Pydantic maydonlari qanday ishlaydi)
- [ ] Metaclass'lar va `__init_subclass__` (SQLAlchemy declarative va Pydantic modellari qanday yaratiladi)
- [ ] GIL: thread, process va async qachon mos keladi
- [ ] asyncio: event loop, coroutine, task, blocking chaqiruvlar, `run_in_executor` (**0-bosqichdan boshlab**, loyiha async)
- [ ] Xotira boshqaruvi: reference counting, garbage collector
- [ ] Typing: generics, Protocol

## PostgreSQL ichki tuzilishi
**Qachon:** 3–10-bosqichlar davomida

- [ ] MVCC: qator versiyalari, snapshot'lar
- [ ] Lock turlari: row, table, advisory; `pg_locks`, `pg_stat_activity`
- [ ] VACUUM, autovacuum, bloat
- [ ] WAL va checkpoint
- [ ] Replikatsiya: streaming va logical

## Katta masshtabdagi system design
**Qachon:** 10-bosqichdan boshlab. **Manba:** *Designing Data-Intensive Applications* (Martin Kleppmann)

- [ ] Storage engine'lar (B-tree va LSM-tree)
- [ ] Replikatsiya va consistency modellari
- [ ] Sharding va consistent hashing
- [ ] CAP va PACELC
- [ ] Stream processing
- [ ] CDN va multi-region arxitektura
- [ ] Qog'ozda loyihalash mashqlari: URL shortener, chat, taksi servisi
- [ ] Design doc: "Mening loyiham 100 baravar ko'p tenant bilan qanday ishlaydi?"

## Tarmoq va Linux
**Qachon:** butun loyiha davomida, ayniqsa 0-, 12-, 18- va 21-bosqichlarda

- [ ] TCP: handshake, retransmission, keep-alive
- [ ] DNS qanday ishlaydi
- [ ] TLS handshake va sertifikatlar
- [ ] HTTP/1.1, HTTP/2, HTTP/3 farqlari; WebSocket protokoli
- [ ] Process, thread, signal'lar
- [ ] Konteynerlar ichidan: namespaces, cgroups
- [ ] Debugging: `ps`, `top`, `ss`, `lsof`, `strace`, `tcpdump`, `curl -v`

## Algoritmlar
**Qachon:** boshidan, muntazam. **Daraja:** medium

- [ ] Array, hash map, two pointers, sliding window
- [ ] Stack, queue, heap
- [ ] Binary search
- [ ] Daraxtlar, BFS va DFS
- [ ] Graflar asoslari
- [ ] Dynamic programming asoslari

---

# Jamoa va production tajribasi

- [ ] 1-daraja MVP'dan keyin (0, 1, 2, 3, 5, 9, 10): rezyume, ishga ariza
- [ ] Open source'ga kamida 3 ta PR
- [ ] Har chaos tajribasi uchun postmortem
- [ ] Har texnologiya uchun "qaror hikoyasi": nima uchun, alternativasi, narxi
- [ ] Mock intervyular: coding va system design
- [ ] 3–5 ta texnik maqola: deadlock, RLS bilan multi-tenancy, aksiyalar engine'i, offline sinxronizatsiya, outbox pattern

---

# Shablonlar

## ADR shabloni (`docs/adr/NNNN-nomi.md`)

```markdown
# NNNN. Qaror nomi

**Holat:** taklif / qabul qilingan / bekor qilingan
**Sana:** YYYY-MM-DD

## Kontekst
Qanday muammo bor? Qanday cheklovlar mavjud?

## Qaror
Nima qilishga qaror qildik?

## Ko'rib chiqilgan alternativalar
Har biri va nima uchun tanlanmagani.

## Oqibatlar
Nima yaxshilanadi, nima qimmatga tushadi, nimani kuzatish kerak?
```

## Postmortem shabloni (`docs/postmortems/YYYY-MM-DD-nomi.md`)

```markdown
# Postmortem: qisqa nom

## Qisqacha
Nima bo'ldi va ta'siri qanday bo'ldi?

## Xronologiya
Qachon boshlandi, qachon aniqlandi, qachon tuzatildi.

## Asosiy sabab
"5 ta nima uchun" usuli bilan.

## Qanday aniqlandi
Qaysi alert, log yoki trace yordam berdi? Nima yetishmadi?

## Tuzatish
Vaqtinchalik va doimiy yechimlar.

## Harakatlar
- [ ] Takrorlanmasligi uchun nima qilinadi
```
