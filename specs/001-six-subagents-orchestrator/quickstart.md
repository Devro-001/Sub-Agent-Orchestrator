# Quickstart Guide: Autonomous 6-SubAgent Orchestrator

**Feature**: `001-six-subagents-orchestrator`  
**Date**: 2026-10-11  

---

## ⚡ 1. Prasyarat Lingkungan
- Linux Mint 22.3 / Ubuntu 24.04 LTS (x86_64)
- Python 3.12+ (Standard library: `sqlite3`, `subprocess`, `dataclasses`, `json`)
- Git terpasang (`/usr/bin/git`)
- Second Brain aktif di `/home/rerei/Documents/SecondBrain/`

---

## 🛠️ 2. Cara Kerja CLI Orchestrator

### Inisialisasi Proyek Baru
```bash
python3 -m core.orchestrator init --name "my-awesome-project" --path "/home/rerei/Documents/Projects/my-awesome-project"
```

### Menguraikan Tugas & Membekukan Kontrak (Manager)
```bash
python3 -m core.orchestrator plan-tasks --prompt "Buat web portal layanan dengan backend FastAPI dan frontend React"
```

### Memulai Eksekusi Paralel (Backend & Frontend)
```bash
python3 -m core.orchestrator run-workers
```

### Melakukan Audit Kualitas & Keamanan (QA)
```bash
python3 -m core.orchestrator audit-staging
```

### Memicu Evaluasi Pembelajaran (Trainer)
```bash
python3 -m core.orchestrator reflex-sync
```

---

## 🔍 3. Verifikasi Status Sub-Agent di Antigravity

Sub-agent telah terdaftar secara native di Antigravity:
1. `orchestrator-manager`
2. `backend-engineer`
3. `frontend-engineer`
4. `qa-security-auditor`
5. `data-researcher`
6. `trainer-continuous-learning`

Untuk memanggil salah satu sub-agent dalam percakapan:
```python
invoke_subagent(Subagents=[{
    "TypeName": "backend-engineer",
    "Role": "Backend Specialist",
    "Prompt": "Implementasikan skema user authentication di /backend/auth.py mengacu pada contracts/types.ts",
    "Workspace": "branch"
}])
```
