"""Task Engine: Atomic Task State Machine & Lock Management via SQLite WAL."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Dict, Any

from contracts.types import Task, TaskStatus, AgentRole, ProjectMeta, AuditResult, TroubleshootingCase


class TaskEngine:
    """Manages atomic task operations, role allocations, and state locks."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            default_dir = Path(__file__).resolve().parent.parent / ".specify" / "memory"
            default_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(default_dir / "task_ledger.db")
        else:
            self.db_path = db_path
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def close(self) -> None:
        """Closes any active database handles."""
        pass

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    root_path TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    assigned_role TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'IDLE',
                    dependencies_json TEXT DEFAULT '[]',
                    file_boundaries_json TEXT NOT NULL DEFAULT '[]',
                    branch_name TEXT,
                    worktree_path TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    reviewer_role TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    exit_code INTEGER,
                    findings_json TEXT DEFAULT '[]',
                    coaching_guidance TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS troubleshooting_sync (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    symptom TEXT NOT NULL,
                    root_cause TEXT NOT NULL,
                    resolution TEXT NOT NULL,
                    preventive_rule TEXT NOT NULL,
                    synced_to_second_brain INTEGER DEFAULT 0,
                    synced_at TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                );
            """)

    def register_project(self, project: ProjectMeta) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO projects (id, name, root_path, description)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    root_path = excluded.root_path,
                    description = excluded.description,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (project.id, project.name, project.root_path, project.description),
            )

    def add_task(self, task: Task) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, project_id, title, assigned_role, status,
                    dependencies_json, file_boundaries_json, branch_name, worktree_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    assigned_role = excluded.assigned_role,
                    dependencies_json = excluded.dependencies_json,
                    file_boundaries_json = excluded.file_boundaries_json,
                    branch_name = excluded.branch_name,
                    worktree_path = excluded.worktree_path,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    task.id,
                    task.project_id,
                    task.title,
                    task.assigned_role.value if isinstance(task.assigned_role, AgentRole) else task.assigned_role,
                    task.status.value if isinstance(task.status, TaskStatus) else task.status,
                    json.dumps(task.dependencies),
                    json.dumps(task.file_boundaries),
                    task.branch_name,
                    task.worktree_path,
                ),
            )

    def get_task(self, task_id: str) -> Optional[Task]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not row:
                return None
            return self._row_to_task(row)

    def list_tasks(self, project_id: Optional[str] = None) -> List[Task]:
        with self._get_connection() as conn:
            if project_id:
                rows = conn.execute("SELECT * FROM tasks WHERE project_id = ? ORDER BY id", (project_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
            return [self._row_to_task(r) for r in rows]

    def claim_next_task(self, role: AgentRole, project_id: Optional[str] = None) -> Optional[Task]:
        """Atomically find and claim the next ready task for a specific agent role."""
        role_val = role.value if isinstance(role, AgentRole) else role
        with self._get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            
            # Find all IDLE tasks for this role
            query = "SELECT * FROM tasks WHERE assigned_role = ? AND status = 'IDLE'"
            params = [role_val]
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            query += " ORDER BY id"

            candidates = conn.execute(query, params).fetchall()
            for cand in candidates:
                deps = json.loads(cand["dependencies_json"] or "[]")
                if not deps:
                    # No dependencies, claim immediately
                    return self._atomic_claim(conn, cand["id"])

                # Check if all dependencies are MERGED or APPROVED
                placeholders = ",".join("?" for _ in deps)
                dep_status_rows = conn.execute(
                    f"SELECT id, status FROM tasks WHERE id IN ({placeholders})", deps
                ).fetchall()
                
                status_map = {r["id"]: r["status"] for r in dep_status_rows}
                all_done = len(status_map) == len(deps) and all(
                    status_map.get(d) in ("APPROVED", "MERGED") for d in deps
                )

                if all_done:
                    return self._atomic_claim(conn, cand["id"])

        return None

    def _atomic_claim(self, conn: sqlite3.Connection, task_id: str) -> Task:
        conn.execute(
            """
            UPDATE tasks 
            SET status = 'CLAIMED', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (task_id,),
        )
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._row_to_task(row)

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> None:
        status_val = new_status.value if isinstance(new_status, TaskStatus) else new_status
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status_val, task_id),
            )

    def record_audit(self, audit: AuditResult) -> None:
        reviewer_val = audit.reviewer_role.value if isinstance(audit.reviewer_role, AgentRole) else audit.reviewer_role
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (
                    task_id, reviewer_role, verdict, exit_code, findings_json, coaching_guidance
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.task_id,
                    reviewer_val,
                    audit.verdict,
                    audit.exit_code,
                    json.dumps(audit.findings),
                    audit.coaching_guidance,
                ),
            )
            # If rejected, increment retry count
            if audit.verdict == "FAIL":
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = 'REJECTED', retry_count = retry_count + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (audit.task_id,),
                )
            elif audit.verdict == "PASS":
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = 'APPROVED', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (audit.task_id,),
                )

    def record_troubleshooting(self, case: TroubleshootingCase) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO troubleshooting_sync (
                    task_id, symptom, root_cause, resolution, preventive_rule, synced_to_second_brain
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    case.task_id,
                    case.symptom,
                    case.root_cause,
                    case.resolution,
                    case.preventive_rule,
                    1 if case.synced_to_second_brain else 0,
                ),
            )
            return cursor.lastrowid

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            project_id=row["project_id"],
            title=row["title"],
            assigned_role=AgentRole(row["assigned_role"]),
            status=TaskStatus(row["status"]),
            file_boundaries=json.loads(row["file_boundaries_json"] or "[]"),
            dependencies=json.loads(row["dependencies_json"] or "[]"),
            branch_name=row["branch_name"],
            worktree_path=row["worktree_path"],
            retry_count=row["retry_count"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
