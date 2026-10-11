# Implementation Plan: Autonomous 6-SubAgent Orchestrator System

**Branch**: `001-six-subagents-orchestrator` | **Date**: 2026-10-11 | **Spec**: [`spec.md`](./spec.md)

**Input**: Feature specification from `/specs/001-six-subagents-orchestrator/spec.md`

---

## 📌 Summary

Membangun sistem orkestrasi 6 sub-agent otonom pada Google Antigravity berbasis Python stdlib-first (tanpa daemon, 0 MB idle RAM) yang mengoordinasikan Manager, Backend, Frontend, QA, Data Researcher, dan Trainer secara paralel. Sistem menjamin **zero code collision** via Git Worktrees, pembekuan kontrak `/contracts/`, penguncian tugas atomik SQLite WAL, dan audit gerbang QA veto, dengan **Second Brain sebagai otak utama**.

---

## 🛠️ Technical Context

- **Language/Version**: Python 3.12 (Standard Library: `sqlite3`, `subprocess`, `dataclasses`, `json`, `pathlib`, `typing`)
- **Primary Dependencies**: Standard Library first (Zero external heavy dependencies), Antigravity Agent Tooling
- **Storage**: SQLite WAL mode (`.specify/memory/task_ledger.db`) untuk konkurensi non-blocking
- **Testing**: `unittest` / `pytest` untuk test suite mandiri
- **Target Platform**: Linux Mint 22.3 / Ubuntu 24.04 LTS x86_64
- **Project Type**: CLI Toolkit & Orchestration Framework
- **Performance Goals**: Eksekusi instan (<100ms per command CLI), 0 MB idle memory overhead
- **Constraints**: 0 background daemon, pemisahan ketat file proyek di `~/Documents/Projects/` dan catatan di `~/Documents/SecondBrain/`, ukuran file $\le$ 45 KB.

---

## 🏛️ Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Pemisahan Source Code**: Seluruh kode berada di `~/Documents/Projects/sub-agent orchestrator/`. Second Brain murni untuk catatan/metadata.
- [x] **Ponytail Efficiency**: Menggunakan Python stdlib bawaan (`sqlite3`, `subprocess`) daripada framework berat.
- [x] **Anti-Slop Craftsmanship**: Kontrak dan arsitektur modular, rapi, terdokumentasi, dan bebas boilerplate generik.
- [x] **Superpowers Discipline**: Menegakkan *Hukum Besi Verifikasi* (QA pass evidence) dan TDD.
- [x] **Max File Size Guardrail**: Setiap file berukuran $\le$ 45 KB.

---

## 📁 Project Structure

### Documentation (this feature)

```text
specs/001-six-subagents-orchestrator/
├── spec.md              # Spesifikasi kebutuhan & user stories
├── plan.md              # Technical blueprint (dokumen ini)
├── research.md          # Riset konkurensi, worktree & Second Brain
├── data-model.md        # Skema SQLite WAL & typed dataclasses
├── quickstart.md        # Panduan penggunaan CLI
├── contracts/           # Kontrak batas file sub-agent
│   └── role_boundaries.json
└── tasks.md             # Checklist subtugas atomik implementasi
```

### Source Code (repository layout)

```text
sub-agent orchestrator/
├── contracts/                     # Kontrak API & tipe data proyek
│   ├── types.py                   # Model data terpusat
│   └── role_contracts.json        # Aturan batasan file per sub-agent
├── core/                          # Inti engine orkestrasi
│   ├── __init__.py
│   ├── orchestrator.py            # State machine & DAG task scheduler
│   ├── task_engine.py             # Engine klaim & kunci tugas (SQLite WAL)
│   ├── worktree_manager.py        # Pengelola Git worktree worker
│   └── second_brain_bridge.py     # Jembatan baca/tulis Second Brain
├── agents/                        # Konfigurasi & template prompt sub-agent
│   ├── __init__.py
│   ├── manager_agent.py           # Eksekutor orchestrator-manager
│   ├── backend_agent.py           # Eksekutor backend-engineer
│   ├── frontend_agent.py          # Eksekutor frontend-engineer
│   ├── qa_agent.py                # Eksekutor qa-security-auditor
│   ├── researcher_agent.py        # Eksekutor data-researcher
│   └── trainer_agent.py           # Eksekutor trainer-continuous-learning
├── tests/                         # Test suites deterministik
│   ├── test_task_engine.py
│   ├── test_worktree_manager.py
│   ├── test_second_brain_bridge.py
│   └── test_orchestrator_flow.py
├── bin/                           # Executable CLI
│   └── sub-agent-orchestrator
└── README.md
```

**Structure Decision**: Menggunakan arsitektur modular terpisah (`core/`, `agents/`, `contracts/`, `tests/`) agar setiap modul mandiri, mudah diuji secara terisolasi, dan bebas circular dependency.

---

## ⚖️ Complexity Tracking

| Keputusan | Mengapa Dibutuhkan | Alternatif Lebih Sederhana yang Ditolak |
|---|---|---|
| SQLite WAL Ledger | Menjamin konkurensi atomic task claiming tanpa race condition antar agen. | File JSON mentah ditolak karena rawan corrupt jika diakses simultan oleh 2 proses. |
| Git Worktrees | Mengisolasi filesystem kerja Backend & Frontend secara fisik. | Shared working directory ditolak karena menyebabkan Git lock conflict dan overwrite file. |
| Dedicated Trainer Agent | Mengabadikan pelajaran dari bug ke Second Brain agar tidak terulang. | Menyerahkan debugging ke agen pembuat kode ditolak karena rawan terjebak dalam bias lokal. |
