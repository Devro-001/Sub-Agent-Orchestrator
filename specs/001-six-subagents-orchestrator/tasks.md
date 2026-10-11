# Implementation Tasks: Autonomous 6-SubAgent Orchestration System

**Feature**: `001-six-subagents-orchestrator` | **Status**: Completed | **Date**: 2026-10-11  
**Spec**: [`spec.md`](./spec.md) | **Plan**: [`plan.md`](./plan.md)  

---

## Phase 1: Setup & Scaffolding

**Purpose**: Struktur proyek dasar, modul, dan dependensi stdlib.

- [x] T001 Membuat struktur direktori proyek (`core/`, `agents/`, `contracts/`, `tests/`, `bin/`)
- [x] T002 [P] Membuat model data terpusat dan enums di `contracts/types.py`
- [x] T003 [P] Membuat kontrak batasan file dan izin akses di `contracts/role_contracts.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Engine inti yang mutlak dibutuhkan sebelum eksekusi sub-agent dimulai.

- [x] T004 Mengimplementasikan Task Engine SQLite WAL (`core/task_engine.py`) untuk atomic task locking
- [x] T005 [P] Mengimplementasikan Git Worktree Manager (`core/worktree_manager.py`) untuk isolasi folder kerja
- [x] T006 [P] Mengimplementasikan Second Brain Bridge (`core/second_brain_bridge.py`) untuk pembacaan aturan dan sinkronisasi log
- [x] T007 Mengimplementasikan Orchestrator State Machine & DAG Scheduler (`core/orchestrator.py`)

**Checkpoint**: Pondasi selesai — pengujian unit dan eksekusi paralel siap dimulai.

---

## Phase 3: User Story 1 — Manager & Task Breakdown (Priority: P1) 🎯 MVP

**Goal**: Orchestrator-Manager mampu memecah kebutuhan proyek menjadi tugas atomik dan membekukan kontrak.

- [x] T008 [P] [US1] Unit test untuk Task Engine di `tests/test_task_engine.py`
- [x] T009 [P] [US1] Unit test untuk Worktree Manager di `tests/test_worktree_manager.py`
- [x] T010 [US1] Mengimplementasikan runner Orchestrator Manager di `agents/manager_agent.py`

**Checkpoint**: User Story 1 selesai dan dapat diuji secara mandiri.

---

## Phase 4: User Story 2 — Backend & Frontend Parallel Execution (Priority: P1)

**Goal**: Backend dan Frontend bekerja simultan pada worktree masing-masing mengacu pada kontrak yang dibekukan.

- [x] T011 [P] [US2] Mengimplementasikan runner Backend Specialist di `agents/backend_agent.py`
- [x] T012 [P] [US2] Mengimplementasikan runner Frontend Specialist di `agents/frontend_agent.py`
- [x] T013 [US2] Mengintegrasikan validasi batasan file (*file boundaries*) saat agen menulis kode

**Checkpoint**: Backend dan Frontend dapat berjalan paralel tanpa konflik Git.

---

## Phase 5: User Story 3 — QA & Security Auditor Veto Gate (Priority: P2)

**Goal**: QA menguji kode di branch staging dan memindai celah keamanan dengan hak veto mutlak.

- [x] T014 [P] [US3] Mengimplementasikan runner QA & Security Auditor di `agents/qa_agent.py`
- [x] T015 [US3] Mengimplementasikan Automated Staging Verification Gate di `core/orchestrator.py`

**Checkpoint**: Sistem menolak rilis jika tes gagal atau terdeteksi celah keamanan.

---

## Phase 6: User Story 4 — Data Researcher Online Intelligence (Priority: P2)

**Goal**: Data Researcher mencari referensi online (>5 sumber) dan merutekan ke Second Brain `06_DATA_SEARCH/`.

- [x] T016 [P] [US4] Mengimplementasikan runner Data Researcher di `agents/researcher_agent.py`
- [x] T017 [US4] Menghubungkan output riset ke Second Brain `06_DATA_SEARCH/` dengan aturan $\le$ 45 KB

**Checkpoint**: Hasil riset tersimpan rapi dan modular di Second Brain.

---

## Phase 7: User Story 5 — Trainer Continuous Learning & Troubleshooting Sync (Priority: P3)

**Goal**: Trainer mendiagnosis kegagalan, membimbing agen, dan mencatat perbaikan ke Second Brain.

- [x] T018 [P] [US5] Mengimplementasikan runner Trainer & Reflexion Agent di `agents/trainer_agent.py`
- [x] T019 [P] [US5] Unit test untuk Second Brain Bridge di `tests/test_second_brain_bridge.py`
- [x] T020 [US5] Mengimplementasikan sinkronisasi otomatis kasus bug ke `05_PROJECTS/Project_Changelog_and_Troubleshooting_Log.md`

**Checkpoint**: Siklus pembelajaran mandiri tertutup; tidak ada kesalahan yang terulang.

---

## Phase 8: Polish & CLI Integration

**Purpose**: Integrasi antarmuka perintah dan verifikasi menyeluruh.

- [x] T021 Membuat CLI executable di `bin/sub-agent-orchestrator`
- [x] T022 [P] Integration test alur lengkap 6 sub-agent di `tests/test_orchestrator_flow.py`
- [x] T023 Validasi quickstart dan audit batas ukuran berkas via `/usr/local/bin/sb-auto-split --check`

---

## ⚡ Verifikasi Hasil Eksekusi
- 9 Unit & Integration Tests: **100% PASS** (0.67s).
- File Size Audit: **100% Lulus ($\le$ 45 KB)**.
- Integrasi Second Brain: Terverifikasi membaca rules & menyinkronkan troubleshooting log.
