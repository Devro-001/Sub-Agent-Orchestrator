# ⚡ Sub-Agent Orchestrator

<p align="center">
  <strong>Deterministic Multi-Agent Execution Engine with Isolated Git Worktrees & Self-Healing Loops</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/Tests-26%20Passed-success" alt="Tests">
  <img src="https://img.shields.io/badge/Architecture-Zero--Bloat%20Stdlib-orange" alt="Stdlib First">
  <img src="https://img.shields.io/badge/Integration-Antigravity%20%7C%20Obsidian-purple" alt="Antigravity & Obsidian">
</p>

---

**Sub-Agent Orchestrator** mengoordinasikan **6 sub-agent spesialis** untuk membangun aplikasi secara paralel tanpa risiko tabrakan kode, tanpa penyimpangan API (*contract drift*), dan dengan siklus revisi otomatis jika pengujian gagal.

### 🌟 4 Pilar Utama
- 🛡️ **Filesystem Isolation**: Setiap sub-agent bekerja di Git Worktree independen (`.worktrees/`). Tidak ada file yang saling tertimpa.
- 🔒 **Immutable Contract Freeze**: Skema API dan tipe data dibekukan di `contracts/` sebelum koding dimulai.
- ⚡ **Atomic Task Ledger**: Mesin SQLite WAL menjamin status tugas dan lock terkelola secara ACID.
- 🔁 **Autonomous Self-Healing**: Jika QA menolak kode, Trainer langsung menganalisis akar masalah dan membimbing worker untuk revisi otomatis.

---

## 🚀 Quickstart (3 Langkah Mudah)

```bash
# 1. Clone repository
git clone https://github.com/hans3-code/Sub-Agent-Orchestrator.git
cd Sub-Agent-Orchestrator

# 2. Buat virtual environment & install
python3 -m venv venv
source venv/bin/activate    # Di Windows: venv\Scripts\activate
pip install -e .

# 3. Jalankan CLI
sub-agent-orchestrator --help
```

---

## 🤖 6 Sub-Agent Spesialis

Setiap sub-agent memiliki batasan folder (*file boundaries*) ketat di [`contracts/role_contracts.json`](contracts/role_contracts.json):

| Sub-Agent | Role ID | Batasan Folder | Tugas Utama |
| :--- | :--- | :--- | :--- |
| **👔 Manager** | `orchestrator-manager` | `specs/**`, `contracts/**` | Pemecahan proyek menjadi DAG task & pembekuan kontrak |
| **⚙️ Backend** | `backend-engineer` | `server/**`, `api/**`, `database/**` | Logika API, database, & efisiensi backend |
| **🎨 Frontend** | `frontend-engineer` | `client/**`, `src/components/**` | UI/UX responsif, aksesibilitas WCAG AA, & Anti-Slop |
| **🛡️ QA Auditor** | `qa-security-auditor` | `tests/**`, `audit-report.md` | Hak veto mutlak, audit keamanan, boundary, & UI/UX |
| **🔍 Researcher** | `data-researcher` | `research/**` | Riset multi-sumber (>= 5 referensi terverifikasi) |
| **🧑‍🏫 Trainer** | `trainer-continuous-learning` | `coaching/**` | Analisis akar masalah (RCA) & pembimbingan revisi |

```
                       ┌────────────────────────┐
                       │  👔 Orchestrator Mgr   │
                       └───────────┬────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
    ┌─────────────────────────┐         ┌─────────────────────────┐
    │   ⚙️ Backend Engineer   │         │   🎨 Frontend Engineer  │
    └────────────┬────────────┘         └────────────┬────────────┘
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
                      ┌─────────────────────────┐
                      │  🛡️ QA Security Auditor │
                      └────────────┬────────────┘
                                   │ (Jika Ditolak)
                                   ▼
                      ┌─────────────────────────┐
                      │    🧑‍🏫 Trainer Agent     │ ◄─── 🔍 Researcher
                      └─────────────────────────┘
```

---

## 🛠️ Ringkasan Perintah CLI

| Perintah | Deskripsi | Contoh Penggunaan |
| :--- | :--- | :--- |
| `init` | Inisialisasi proyek baru | `sub-agent-orchestrator init --id api-1 --name "Billing API"` |
| `freeze-contract` | Kunci kontrak API | `sub-agent-orchestrator freeze-contract auth.json '{"endpoints": ["/login"]}'` |
| `tasks` | Lihat daftar tugas & status | `sub-agent-orchestrator tasks` |
| `dispatch` | Buka worktree terisolasi | `sub-agent-orchestrator dispatch T-BE-01` |
| `qa` | Jalankan audit gerbang QA | `sub-agent-orchestrator qa T-BE-01` |
| `merge` | Gabungkan ke branch `main` | `sub-agent-orchestrator merge T-BE-01` |
| `run-auto` | **Siklus Revisi Otonom** | `sub-agent-orchestrator run-auto T-BE-01 --retries 3` |

---

## 🔌 Konfigurasi dengan Google Antigravity

Sub-Agent Orchestrator terintegrasi secara alami dengan **Google Antigravity**:

### 1. Pemanggilan Sub-Agent via Chat Antigravity
Anda dapat memanggil sub-agent langsung di Antigravity menggunakan perintah `invoke_subagent`:

```json
{
  "Subagents": [
    {
      "TypeName": "self",
      "Role": "Backend Specialist",
      "Prompt": "Kerjakan task T-BE-01 di worktree terisolasi mengacu pada contracts/types.py",
      "Workspace": "inherit"
    },
    {
      "TypeName": "self",
      "Role": "Frontend Specialist",
      "Prompt": "Bangun UI form login dengan WCAG AA compliance tanpa AI-slop copy",
      "Workspace": "inherit"
    }
  ]
}
```

### 2. Menjalankan Self-Healing Loop di Terminal Antigravity
Buka terminal Antigravity dan jalankan:
```bash
sub-agent-orchestrator run-auto <task_id> --retries 3
```
*Jika kode ditolak oleh QA, Trainer otomatis memberikan instruksi revisi langsung ke worker tanpa intervensi manual.*

---

## 🧠 Konfigurasi dengan Obsidian (Second Brain)

Orchestrator menggunakan arsitektur adaptif:

### Opsi A: Standalone Mode (Tanpa Obsidian)
Jika Anda **tidak menggunakan Obsidian**, sistem langsung berjalan mandiri (*zero-config*) dan menyimpan memori internal di folder `.second_brain/` proyek.

### Opsi B: Sinkronisasi ke Obsidian Vault
Untuk menghubungkan agen ke vault Obsidian Second Brain Anda:

1. Buat file `.env` di root proyek:
   ```env
   SECOND_BRAIN_PATH=/path/ke/folder/ObsidianVault
   ```
   *(Atau lewat environment variable: `export SECOND_BRAIN_PATH="~/Documents/SecondBrain"`)*

2. **Struktur yang Otomatis Terhubung di Obsidian:**
   - 👤 `01_PROFILE/User_Profile.md`: Preferensi koding & profil Anda dibaca oleh sub-agent.
   - 📜 `02_RULES_GUIDELINES/Base_Agent_AI_Guidelines.md`: Pedoman Anti-Slop & Ponytail diserap agen.
   - 🛠️ `05_PROJECTS/Project_Changelog_and_Troubleshooting_Log.md`: Database penanganan error & solusi dicatat otomatis saat ada bug.
   - 🔍 `06_DATA_SEARCH/<topik>/`: Riset baru disimpan dengan batas aman **<= 45 KB** (bebas truncation).

---

## 🧪 Menjalankan Pengujian

Jalankan seluruh test suite (26 tes unit & integrasi):

```bash
python3 -m unittest discover -s tests -v
```

Output yang diharapkan:
```text
Ran 26 tests in 1.4s
OK
```

---

## 📂 Struktur Repositori

```text
├── agents/             # Implementasi 6 sub-agent (Manager, Backend, Frontend, QA, Researcher, Trainer)
├── contracts/          # Kontrak API terbekukan & role_contracts.json
├── core/               # Core engine: CLI, WorktreeManager, TaskEngine, SecondBrainBridge
├── tests/              # 26 Unit & integration tests
├── .env.example        # Template variabel lingkungan
├── ARCHITECTURE.md     # Cetak biru arsitektur lengkap
├── CONTRIBUTING.md     # Panduan kontribusi & aturan batas file
├── pyproject.toml      # Konfigurasi packaging Python standar
└── README.md           # Panduan visual ringkas & jelas
```

---

## 📄 Lisensi
[MIT License](LICENSE) © 2026 Sub-Agent Orchestrator Contributors.
