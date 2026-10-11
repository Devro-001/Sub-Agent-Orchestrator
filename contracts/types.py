"""Central Type Definitions and Contracts for the 6-SubAgent Orchestrator."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


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
class ProjectMeta:
    id: str
    name: str
    root_path: str
    description: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Task:
    id: str
    project_id: str
    title: str
    assigned_role: AgentRole
    status: TaskStatus = TaskStatus.IDLE
    file_boundaries: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    branch_name: Optional[str] = None
    worktree_path: Optional[str] = None
    retry_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "assigned_role": self.assigned_role.value if isinstance(self.assigned_role, AgentRole) else self.assigned_role,
            "status": self.status.value if isinstance(self.status, TaskStatus) else self.status,
            "file_boundaries": self.file_boundaries,
            "dependencies": self.dependencies,
            "branch_name": self.branch_name,
            "worktree_path": self.worktree_path,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class AuditResult:
    task_id: str
    reviewer_role: AgentRole
    verdict: str  # "PASS" or "FAIL"
    exit_code: int
    test_output: str
    findings: List[str] = field(default_factory=list)
    coaching_guidance: Optional[str] = None


@dataclass
class TroubleshootingCase:
    task_id: str
    symptom: str
    root_cause: str
    resolution: str
    preventive_rule: str
    synced_to_second_brain: bool = False
