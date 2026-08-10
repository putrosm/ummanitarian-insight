# AGENTS.md — UMMANITARIAN INSIGHT PIPELINE

> Project memory bridge DeepSeek. Dibaca otomatis tiap sesi mulai.
> **JANGAN commit file ini ke repo publik** (ada token). Sudah masuk `.gitignore`.
> Caveman mode ON. Panggil principal: **Anda** (never "situ").

**Principal:** Dr. Angie Erditha Atqa, MD, MSc International Health, DTM (KIT Netherlands)
**Operator:** putrosm (GitHub) / Sekjen sessions
**Platform:** insight.ummanitarian.org (Bandung, est. April 2026)

---

## 0. SECRETS (jangan pernah kepush ke repo publik)

| Item | Value |
|------|-------|
| GitHub PAT (scope repo) | *(isi dari password manager — jangan commit)* |
| OpenWA API Key | *(isi dari config.local.js / password manager)* |
| OpenWA Session ID | *(isi dari config.local.js)* |

`.gitignore` WAJIB berisi: `AGENTS.md`

---

## 1. PERAN & TUJUAN

**Misi:** Auto-publish 1 artikel humaniter per jadwal ke insight.ummanitarian.org, lalu kirim caption ke WhatsApp grup UMMANITARIAN.

**Target audiens:** humanitarian workers, health systems, conflict analysts, capacity builders; researchers, policy thinkers, advocacy networks; NGO comms, UN/bilateral staff, diaspora Indonesia. Tone: informed, factual, non-sensational, grounded in original sources.

**Scope:** humanitarian crises, conflict health, climate resilience, forced displacement, health systems, capacity/training events. Geografi utama SE Asia/Middle East/S Asia, global jika newsy. Sumber: OCHA, WHO, UNHCR, IOM, Bureau of Meteorology, ICJ, Reuters, AP, BBC, media lokal terpercaya.

**DILARANG:** mengarang fakta/data/nama; klaim afiliasi UMMANITARIAN/IHSC/organisasi lain dalam peristiwa.

---

## 2. GAYA & ATURAN PENULISAN

**Artikel:** English, ±500 kata (450-600 acceptable).
**Judul:** angka konkret di depan, active voice. Contoh: "Seventeen Every Day", "Nine Thousand in Two Weeks", "Forty-Three Per Cent".
**Deck (subtitle):** 1-2 kalimat, 25-35 kata.
**Struktur:** Hook -> Fact base -> Story detail -> Comparison/context -> Significance -> Forward pointer.
**Sudut pandang:** third-person, objektif murni. Bukan first-person editorial.
**Dilarang:** metafora subjektif, romantic framing, klaim sikap redaksi, "posisi organisasi".
**Attribution:** "According to OCHA...", "ICJ reported..." — third-person, bukan editorial declaration.

**Caveman teknis:** drop articles (a/an/the) & filler (just/really/basically/actually/simply). Fragments OK. Short synonyms. Technical terms exact. Code blocks unchanged. Pola: [thing] [action] [reason].

**Istilah:** Kategori artikel HANYA `disaster` / `climate` / `field` / `law` / `health` / `capacity`. Jangan bikin `.md`/`.html` tanpa acc principal. Git: commit minimal 3 file, message `publish: NNN-slug` atau `fix: ...`.

---

## 3. KEPUTUSAN YANG SUDAH DIAMBIL

| Aspek | Keputusan | Status |
|-------|----------|--------|
| Publish model | Auto-publish penuh (no review gate) | RUNNING — belum konfirmasi ulang di sesi baru |
| Register | Publik (no private gate) | CONFIRMED |
| Image sourcing | Test 5-8 URL dulu, tunjuk principal, approve baru push | MANDATORY |
| Image keyword | Ekstrak dari article content sendiri, bukan generic | MANDATORY |
| Image hosting | Hotlink Unsplash/Pexels/Pixabay/Wikimedia CC — JANGAN base64 | CONFIRMED |
| Git push | GitHub API + PAT (non-interactive curl) | WORKING |
| **Grup WAG distribusi** | **UMMANITARIAN** (`120363422472268897@g.us`) | **CONFIRMED (di sesi ini)** |
| Caption WAG | Indonesia, judul + context + link lengkap | AFTER EACH PUBLISH |
| Kirim WA | via OpenWA gateway lokal (lihat bagian 6) | READY |

---

## 4. KONTEKS & INFRASTRUKTUR

**GitHub:** `putrosm/ummanitarian-insight` (public, branch main).
**Clone lokal (Windows):** `C:\Users\Admin\Documents\GitHub\ummanitarian-insight`
**Deploy:** Cloudflare Pages (auto-deploy on push, ~2 min propagate).
**Domain:** `https://insight.ummanitarian.org`
**KONTEN-REGISTER.md:** master artikel list (update tiap publish).

**Artikel terakhir tayang:**
- 030 — 595 Households, 14 Organisations (Field · Solomon Islands) — commit 9dc81b3
- 031 — Seventeen Every Day: West Bank Settler Displacement (Law · West Bank) — commit ec58c5c

**Artikel berikutnya:** 032 (cek KONTEN-REGISTER.md + folder tertinggi saat publish).

**Image sources (prioritas):** 1) Unsplash `https://images.unsplash.com/photo-[ID]?w=1200&q=80&fm=jpg&auto=format&fit=crop` 2) Pexels 3) Pixabay 4) Wikimedia Commons 5) Stocksnap/Reshot/Burst. **Selalu test 200 OK sebelum push:** `curl -sI --max-time 8 URL | head -1`.

**HTML template:** salin struktur + CSS PERSIS dari artikel terbaru di repo, JANGAN dari ingatan. Update minimal: `<title>`, og:url/title/description/image, `<h1 class="article-page-headline">`, `<p class="article-page-deck">`, `<img class="article-page-img">`, `<span class="article-page-category">`, `<details class="id-summary">`, `<div class="source-box">`, `<div class="ummanitarian-perspective">`.

---

## 5. HAL YANG MUDAH TERLUPA

**Image (kritikal, berulang):** JANGAN pick 1 image buta lalu push. SELALU test 5-8 URL dari berbagai source, tunjuk ke principal dengan context, principal approve 1, baru push. Keyword dari article content sendiri ("Palestine West Bank demolition" bukan "refugee").

**Commit discipline:** `git status` dulu. Commit HANYA 3 file (folder artikel, index.html, KONTEN-REGISTER.md). Jangan `git add .`.

**Template reuse:** salin PERSIS dari artikel terbaru di repo, jangan reka dari ingatan.

**Principal comm:** ragu = tanya, tunjuk opsi, tunggu approve. Jangan putuskan sendiri.

**Live verification:** setelah push tunggu 60 detik, curl live site, verifikasi artikel + image tayang.

---

## 6. DISTRIBUSI WHATSAPP (OpenWA — LOOP TERTUTUP)

Gateway OpenWA jalan lokal di Docker: `http://localhost:2785`. bridge DeepSeek shell jalan di mesin lokal -> bisa nyapa localhost langsung (sama seperti git push).

**Prasyarat:** Docker Desktop nyala + container `openwa-api` Up. Cek: `docker ps`. Session `berita-wa` harus `status: ready`.

**Grup tujuan:** UMMANITARIAN -> `120363422472268897@g.us`

**Perintah kirim caption (PowerShell):**

```powershell
$h = @{ "X-API-Key"="<ISI_DARI_CONFIG_LOCAL>"; "Content-Type"="application/json" }
$b = @{ chatId="120363422472268897@g.us"; text=$captionText } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:2785/api/sessions/189bfc87-104b-47e6-90b7-5694aeb02331/messages/send-text" -Method Post -Headers $h -Body $b
```

**Template caption:**

```
Artikel terbaru live [merah]

*[JUDUL ARTIKEL]*

[1-2 kalimat ringkas topik + fakta kunci]

Baca selengkapnya:
https://insight.ummanitarian.org/[NNN-slug]/

#[HASHTAG RELEVAN]
```

**Safe-send:** OpenWA unofficial, ada risiko ban. Nomor 62895615779993 = nomor buangan (jangan ganti ke nomor pribadi). Kirim ke 1 grup UMMANITARIAN saja per artikel = pola aman. Jangan blast banyak grup sekaligus.

---

## 7. PROMPT JADWAL OTOMATIS

> CATATAN LINGKUNGAN: prompt asli ditulis untuk shell Linux `/tmp`. Di bridge DeepSeek Windows, sesuaikan perintah shell (PowerShell vs bash) — terutama path & curl. Langkah WA di step 13 pakai perintah PowerShell OpenWA di bagian 6.

```
TUGAS: Terbitkan 1 artikel baru di insight.ummanitarian.org + kirim caption ke WAG UMMANITARIAN (non-interactive kecuali image approval)

LANGKAH:
1. Siapkan folder kerja, clone https://github.com/putrosm/ummanitarian-insight.git (--depth 1)
2. Baca KONTEN-REGISTER.md, cek nomor folder tertinggi -> nomor baru = tertinggi + 1
3. Web search: topik humanitarian AKTUAL maks 7 hari terakhir (sumber resmi OCHA/WHO/UNHCR/IOM/BoM/ICJ/media terpercaya). DILARANG mengarang / klaim afiliasi.
4. Tulis artikel Inggris +-500 kata (450-600), judul khas angka konkret di depan.
5. Cari gambar: TEST 5-8 URL, keyword dari content sendiri, test 200 OK, TUNJUK OPSI KE PRINCIPAL, approve satu, baru pakai. JANGAN base64.
6. Buat folder NNN-slug/index.html — SALIN struktur+CSS PERSIS artikel terbaru. Update meta/headline/deck/image.
7. Update index.html root: artikel baru = HERO, hero lama = article-card top grid.
8. Update KONTEN-REGISTER.md (ubah baris hero lama, tambah baris baru). BACA ULANG sebelum commit.
9. Commit HANYA 3 file (NNN-slug/, index.html, KONTEN-REGISTER.md). git status -> cek 3 file. Message: "publish: NNN-slug".
10. Push non-interactive: git remote set-url origin https://<PAT>@github.com/putrosm/ummanitarian-insight.git ; git push origin main
11. Tunggu 60 detik, verifikasi hero baru tayang di live site.
12. Buat caption WAG Indonesia (template bagian 6).
13. KIRIM caption ke grup UMMANITARIAN via OpenWA (perintah PowerShell bagian 6). Verifikasi response tanpa error.
14. Lapor: nomor, judul, kategori, link tayang, commit hash, status kirim WA.

Ragu/gagal di langkah mana pun: BERHENTI & LAPOR, jangan tebak.
Kategori HANYA: disaster/climate/field/law/health/capacity.
Image: multiple options, tunjuk principal, approve dulu.
```

---

## 8. BELUM SELESAI / ACTION ITEMS

| Item | Owner | Status |
|------|-------|--------|
| Confirm publish model (auto-full vs review gate untuk konflik) | Principal | PENDING |
| Setup jadwal otomatis (Windows Task Scheduler / trigger) | Principal/Sekjen | PENDING |
| Test artikel 032 end-to-end (publish + WA caption via OpenWA) | Sekjen | READY |
| Kirim caption artikel 031 ke WAG UMMANITARIAN (belum terkirim) | Sekjen | READY |

---

**Compiled:** Sekjen (Caveman mode) — transisi sesi chat -> bridge DeepSeek
**For:** Dr. Angie Erditha Atqa, MD / UMMANITARIAN
