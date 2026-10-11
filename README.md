# ⚡ Sub-Agent Orchestrator

<p align="center">
  <strong>Deterministic Multi-Agent Engine dengan Git Worktrees & Self-Healing Loop</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Trigger-ORCA%20%7C%20orca-cyan" alt="Trigger ORCA">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/Tests-27%20Passed-success" alt="Tests">
  <img src="https://img.shields.io/badge/Integration-Antigravity%20%7C%20Obsidian-purple" alt="Antigravity & Obsidian">
</p>

---

## 💡 Cara Cepat Memanggil (AI Trigger Shortcut)

Cukup gunakan token pemicu **`orca`** atau **`ORCA`** di awal prompt Anda pada chat Antigravity / AI:

```text
orca buatkan modul autentikasi JWT dan UI login responsif
```
```text
ORCA: refactor endpoint database dan audit keamanan API
```

> **Sistem secara otomatis**:
> 1. Membaca awalan `orca` sebagai sinyal aktivasi 6 sub-agent spesialis.
> 2. Membagi task, membekukan kontrak skema (*Contract Freeze*), dan membuka worktree terisolasi.
> 3. Menjalankan audit QA gerbang mutlak sebelum menggabungkan kode ke branch utama.

---

## 🚀 Quickstart (3 Langkah Instalasi)

```bash
# 1. Clone repositori
git clone https://github.com/hans3-code/Sub-Agent-Orchestrator.git
cd Sub-Agent-Orchestrator

# 2. Buat virtual environment & install
python3 -m venv venv
source venv/bin/activate       # Di Windows: venv\Scripts\activate
pip install -e .

# 3. Jalankan CLI
sub-agent-orchestrator --help
```

---

## 🤖 6 Sub-Agent Spesialis

Setiap sub-agent bekerja pada ruang direktori terisolasi (*file boundaries*):

| Agen | Peran | Batasan Folder | Tanggung Jawab |
| :--- | :--- | :--- | :--- |
| **👔 Manager** | `orchestrator-manager` | `specs/**`, `contracts/**` | Memecah task menjadi DAG & membekukan kontrak |
| **⚙️ Backend** | `backend-engineer` | `server/**`, `api/**`, `database/**` | Logika API, database, & efisiensi backend |
| **🎨 Frontend** | `frontend-engineer` | `client/**`, `src/components/**` | UI/UX modern, aksesibilitas WCAG AA, & Anti-Slop |
| **🛡️ QA Auditor** | `qa-security-auditor` | `tests/**`, `audit-report.md` | **Hak Veto Mutlak**: Audit tes, keamanan, & UI |
| **🔍 Researcher** | `data-researcher` | `research/**` | Riset multi-sumber (>= 5 referensi terverifikasi) |
| **🧑‍🏫 Trainer** | `trainer-continuous-learning` | `coaching/**` | Analisis akar masalah (RCA) & bimbingan revisi |

### Alur Koordinasi:
```
                ┌────────────────────────┐
                │  👔 Orchestrator Mgr   │
                └───────────┬────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
┌───────────────────┐               ┌───────────────────┐
│ ⚙️ Backend (Git)  │               │ 🎨 Frontend (Git) │
└─────────┬─────────┘               └─────────┬─────────┘
          │                                   │
          └─────────────────┬─────────────────┘
                            ▼
                ┌───────────────────────┐
                │ 🛡️ QA Security Auditor │
                └───────────┬───────────┘
                            │ (Jika Ditolak)
                            ▼
                ┌───────────────────────┐
                │   🧑‍🏫 Trainer Agent    │ ◄─── 🔍 Researcher
                └───────────────────────┘
```

---

## 🛠️ Perintah CLI Utama

| Perintah | Fungsi | Contoh |
| :--- | :--- | :--- |
| `init` | Inisialisasi proyek | `sub-agent-orchestrator init --id app-1 --name "Demo"` |
| `freeze-contract` | Kunci kontrak API | `sub-agent-orchestrator freeze-contract auth.json '{"route": "/login"}'` |
| `tasks` | Daftar & status tugas | `sub-agent-orchestrator tasks` |
| `dispatch` | Buka worktree task | `sub-agent-orchestrator dispatch T-BE-01` |
| `qa` | Audit gerbang QA | `sub-agent-orchestrator qa T-BE-01` |
| `merge` | Gabung ke `main` | `sub-agent-orchestrator merge T-BE-01` |
| `run-auto` | **Siklus Revisi Otonom** | `sub-agent-orchestrator run-auto T-BE-01 --retries 3` |

---

## 🔌 Integrasi Lingkungan

### 1. Google Antigravity
- **Prompt Chat**: Cukup ketik `orca <instruksi>`.
- **Eksekusi Otomatis**: Jalankan `sub-agent-orchestrator run-auto <task_id>` di terminal Antigravity untuk menjalankan *self-healing loop* tanpa intervensi manusia jika ada penolakan QA.

### 2. Obsidian (Second Brain)
- **Standalone Mode (Default)**: Berjalan mandiri tanpa Obsidian, data tersimpan di `.second_brain/`.
- **Obsidian Vault**: Hubungkan dengan menambahkan file `.env`:
  ```env
  SECOND_BRAIN_PATH=/path/ke/folder/ObsidianVault
  ```
  Otomatis menyinkronkan profil (`01_PROFILE`), pedoman (`02_RULES`), dan log troubleshooting (`05_PROJECTS`).

---

## 🧪 Verifikasi Tes

Jalankan test suite (27 unit & integration tests):
```bash
python3 -m unittest discover -s tests -v
```
*(Seluruh 27 tes dipastikan lulus 100% di Linux, macOS, dan Windows).*

---

## 📄 Lisensi
[MIT License](LICENSE) © 2026 Sub-Agent Orchestrator Contributors.
