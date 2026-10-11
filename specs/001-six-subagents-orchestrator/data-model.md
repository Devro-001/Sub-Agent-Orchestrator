# Data Model: Autonomous 6-SubAgent Orchestration System

**Feature**: `001-six-subagents-orchestrator`  
**Date**: 2026-10-11  
**Status**: Completed  

---

## 🗄️ 1. Entitas & Struktur Data SQLite WAL (`task_ledger.db`)

### 1.1. Tabel `projects`
Menyimpan metadata proyek yang dikelola oleh Orchestrator.

```sql
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    root_path TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.2. Tabel `tasks`
Menyimpan unit kerja atomik yang dialokasikan ke sub-agent.

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT NOT NULL,
    assigned_role TEXT NOT NULL, -- 'backend', 'frontend', 'qa', 'researcher', 'trainer'
    status TEXT NOT NULL DEFAULT 'IDLE', -- 'IDLE', 'CLAIMED', 'IN_PROGRESS', 'READY_FOR_REVIEW', 'APPROVED', 'REJECTED', 'MERGED'
    dependencies_json TEXT DEFAULT '[]', -- List of task_ids that must complete first
    file_boundaries_json TEXT NOT NULL, -- List of permitted directory prefixes
    branch_name TEXT,
    worktree_path TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

### 1.3. Tabel `audit_logs`
Menyimpan riwayat evaluasi QA dan umpan balik Trainer.

```sql
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    reviewer_role TEXT NOT NULL, -- 'qa' or 'trainer'
    verdict TEXT NOT NULL, -- 'PASS', 'FAIL', 'COACH'
    exit_code INTEGER,
    findings_json TEXT, -- List of findings / vulnerabilities / failing assertions
    coaching_guidance TEXT, -- Actionable fix steps from Trainer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

### 1.4. Tabel `troubleshooting_sync`
Menyimpan sinkronisasi kasus bug ke Second Brain.

```sql
CREATE TABLE IF NOT EXISTS troubleshooting_sync (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    symptom TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    resolution TEXT NOT NULL,
    preventive_rule TEXT NOT NULL,
    synced_to_second_brain INTEGER DEFAULT 0,
    synced_at TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

---

## 📑 2. Python Data Classes (Type Contracts)

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

class TaskStatus(str, Enum):
    IDLE = "IDLE"
    CLAIMED = "CLAIMED"
    IN_PROGRESS = "IN_PROGRESS"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MERGED = "MERGED"

class AgentRole(str, Enum):
    MANAGER = "orchestrator-manager"
    BACKEND = "backend-engineer"
    FRONTEND = "frontend-engineer"
    QA = "qa-security-auditor"
    RESEARCHER = "data-researcher"
    TRAINER = "trainer-continuous-learning"

@dataclass
class Task:
    id: str
    project_id: str
    title: str
    assigned_role: AgentRole
    status: TaskStatus
    file_boundaries: List[str]
    dependencies: List[str] = field(default_factory=list)
    branch_name: Optional[str] = None
    worktree_path: Optional[str] = None
    retry_count: int = 0

@dataclass
class AuditResult:
    task_id: str
    verdict: str  # PASS / FAIL
    exit_code: int
    test_output: str
    security_findings: List[str] = field(default_factory=list)

@dataclass
class TroubleshootingCase:
    task_id: str
    symptom: str
    root_cause: str
    resolution: str
    preventive_rule: str
```
