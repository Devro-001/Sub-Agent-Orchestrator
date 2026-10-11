# Technical Research: Autonomous 6-SubAgent Orchestration System

**Feature**: `001-six-subagents-orchestrator`  
**Date**: 2026-10-11  
**Status**: Completed  

---

## 🔬 1. Research Objectives & Problem Analysis

Tujuan riset ini adalah mengidentifikasi dan memvalidasi fondasi teknologi untuk menjalankan 6 sub-agent di Antigravity:
1. **Manager (Orchestrator)**
2. **Backend Specialist**
3. **Frontend Specialist**
4. **QA & Security Auditor**
5. **Data Researcher**
6. **Trainer & Reflexion Agent**

### Problem 1: Concurrency & Code Overwrite (Race Conditions)
Jika dua LLM agen mengedit direktori file sistem yang sama secara bersamaan:
- Git lockfile (`.git/index.lock`) saling menabrak.
- Konflik baris kode menyebabkan merge conflicts tak terduga.
- Dependensi bersama (`node_modules`, `venv`) mengalami modifikasi paralel.

**Solusi Terverifikasi**:
- **Git Worktrees (`git worktree add -b <branch> <path> <commit>`)**: Setiap worker subagent menerima working directory terpisah yang menunjuk ke `.git` repository yang sama.
- **Contract-First Architecture**: Pembekuan skema di `contracts/` sebelum pengerjaan.
- **Single-Writer File Boundaries**: Kepemilikan folder yang eksklusif (Backend memiliki `backend/**`, Frontend memiliki `frontend/**`).

---

## 🔬 2. Task Ledger & Lock Engine Architecture

### SQLite WAL Mode vs File Locks
- **Pilihan**: SQLite dengan Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).
- **Alasan**:
  - Konkurensi pembacaan tinggi (multiple subagents membaca status secara non-blocking).
  - atomic transaction (`BEGIN IMMEDIATE`) untuk proses klaim tugas (`CLAIMED`).
  - Standar library Python (`import sqlite3`), 0 MB idle RAM, 0 background daemon (mematuhi prinsip Ponytail).

### Skema Task State Machine:
```text
[IDLE] 
  │
  ▼ (Manager dispatch)
[CLAIMED] (Lock acquired by Agent ID)
  │
  ▼ (Worker executes)
[IN_PROGRESS]
  │
  ▼ (Worker completes unit tests)
[READY_FOR_REVIEW] (PR to staging worktree)
  │
  ▼ (QA Audit: Unit + Sec scan)
┌───────────────────────┴───────────────────────┐
▼ (QA Veto: FAIL)                               ▼ (QA Stamp: PASS)
[REJECTED]                                      [APPROVED]
  │                                               │
  ▼ (Trainer investigates)                        ▼ (Manager merges)
[COACHING]                                      [MERGED]
  │ (Remediation guidance)
  ▼
[IN_PROGRESS] (Retry round)
```

---

## 🔬 3. Second Brain Integration Protocol

### Integrasi Pembacaan (Ingestion):
- Setiap agen membaca konteks sebelum beroperasi:
  - `01_PROFILE/User_Profile.md` (identitas, batasan kode di `~/Documents/Projects/`).
  - `02_RULES_GUIDELINES/Base_Agent_AI_Guidelines.md` (Ponytail, Anti-Slop, Superpowers).
  - `05_PROJECTS/Project_Changelog_and_Troubleshooting_Log.md` (database solusi bug).

### Integrasi Pencatatan (Syncing):
- **Trainer Agent**:
  - Mencatat setiap insiden bug yang diselesaikan ke Troubleshooting Knowledge Base.
  - Memperbarui `Project_Changelog_and_Troubleshooting_Log.md` (Gejala, Akar Masalah, Solusi, Pelajaran).
- **Data Researcher Agent**:
  - Menyimpan wawasan teknis baru ke `06_DATA_SEARCH/<folder_topik>/` (Modular $\le$ 45 KB).

---

## 🔬 4. Evaluasi Beban Komputasi Laptop (Resource Guardrails)

- **Target OS**: Linux Mint 22.3 / Ubuntu 24.04 LTS (Intel Celeron N4000, RAM 3.7 GiB).
- **Karakteristik Orkestrator**:
  - Pure CLI on-demand (bukan background service atau web server monolitik).
  - 0 MB konsumsi RAM saat idle.
  - Runtime Python standard library tanpa dependencies berat.
  - Sesuai dengan batasan performa laptop pengguna.
