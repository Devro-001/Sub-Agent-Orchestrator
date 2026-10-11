"""QA & Security Auditor Agent (Agent 4): Verification, Quality Gate & Security Hardening."""

from typing import Dict, List, Any, Optional
from contracts.types import AgentRole, Task, AuditResult
from core.orchestrator import Orchestrator


class QAAgent:
    """QA and Security Auditor subagent implementation with absolute veto power."""

    ROLE = AgentRole.QA
    DEFAULT_BOUNDARIES = ["tests/**", "e2e/**", "security/**", "audit-report.md"]

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def audit_task(self, task_id: str, test_command: Optional[List[str]] = None) -> AuditResult:
        """Runs automated verification and security audit on the task staging worktree."""
        return self.orchestrator.run_qa_gate(task_id, test_command)
