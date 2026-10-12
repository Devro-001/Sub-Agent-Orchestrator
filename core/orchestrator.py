"""Orchestrator Core: Multi-Agent Lifecycle Coordinator and Deterministic Gatekeeper."""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from contracts.types import (
    Task,
    TaskStatus,
    AgentRole,
    ProjectMeta,
    AuditResult,
    TroubleshootingCase,
)
from core.task_engine import TaskEngine
from core.worktree_manager import WorktreeManager
from core.second_brain_bridge import SecondBrainBridge


class Orchestrator:
    """Master orchestrator governing the 6 sub-agents, worktrees, contracts, and Second Brain."""

    def __init__(self, project_root: str, second_brain_path: Optional[str] = None):
        self.project_root = Path(project_root).resolve()
        self.task_engine = TaskEngine(
            str(self.project_root / ".specify" / "memory" / "task_ledger.db")
        )
        self.worktree_manager = WorktreeManager(str(self.project_root))
        self.sb_bridge = SecondBrainBridge(
            second_brain_path, workspace_root=self.project_root, auto_bootstrap=True
        )
        self.contracts_dir = self.project_root / "contracts"
        self.contracts_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_auto_initialized()

    def _ensure_auto_initialized(self) -> None:
        """Automatically registers the current project in TaskEngine if not already registered."""
        proj_name = self.project_root.name
        proj_id = "".join(c if c.isalnum() else "-" for c in proj_name).lower().strip("-")
        while "--" in proj_id:
            proj_id = proj_id.replace("--", "-")
        if not proj_id:
            proj_id = "default-project"


        existing = self.task_engine.get_project(proj_id)
        if not existing:
            self.init_project(
                project_id=proj_id,
                name=proj_name,
                description=f"Auto-initialized orchestrator workspace for {proj_name}",
            )


    def init_project(self, project_id: str, name: str, description: str = "") -> ProjectMeta:
        project = ProjectMeta(
            id=project_id,
            name=name,
            root_path=str(self.project_root),
            description=description,
        )
        self.task_engine.register_project(project)
        return project

    def freeze_contract(self, filename: str, contract_content: str) -> Path:
        """Freezes an API or type contract before worker agents begin coding."""
        contract_file = self.contracts_dir / filename
        contract_file.write_text(contract_content, encoding="utf-8")
        
        # Git commit frozen contract
        subprocess.run(
            ["git", "add", str(contract_file)],
            cwd=self.project_root,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"chore(contracts): freeze contract {filename}"],
            cwd=self.project_root,
            capture_output=True,
        )
        return contract_file

    def dispatch_task(self, task_id: str) -> Tuple[Task, str]:
        """Claims a task, provisions an isolated git worktree, and returns (task, worktree_path)."""
        task = self.task_engine.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Provision worktree
        branch_name, wt_path = self.worktree_manager.create_worktree(
            task.assigned_role, task.id
        )
        task.branch_name = branch_name
        task.worktree_path = wt_path
        task.status = TaskStatus.IN_PROGRESS
        self.task_engine.add_task(task)

        return task, wt_path

    def run_qa_gate(self, task_id: str, test_cmd: Optional[List[str]] = None) -> AuditResult:
        """Executes automated quality & security verification gate with absolute veto power."""
        task = self.task_engine.get_task(task_id)
        if not task or not task.worktree_path:
            raise ValueError(f"Task {task_id} has no active worktree to audit")

        # 1. Verify file boundaries
        is_valid, violations = self.worktree_manager.validate_file_boundaries(
            task.worktree_path, task.file_boundaries
        )
        if not is_valid:
            audit = AuditResult(
                task_id=task_id,
                reviewer_role=AgentRole.QA,
                verdict="FAIL",
                exit_code=1,
                test_output="File boundary violation detected",
                findings=[f"Unauthorized modified file: {f}" for f in violations],
                coaching_guidance="Do not modify files outside your allocated boundaries.",
            )
            self.task_engine.record_audit(audit)
            return audit

        # 2. If task is Frontend, run UI/UX, A11y, and Anti-Slop audit
        if task.assigned_role == AgentRole.FRONTEND:
            from agents.qa_agent import QAAgent
            qa_inspector = QAAgent(self)
            ui_passed, ui_findings = qa_inspector.audit_frontend_ui_ux(task.worktree_path)
            if not ui_passed:
                audit = AuditResult(
                    task_id=task_id,
                    reviewer_role=AgentRole.QA,
                    verdict="FAIL",
                    exit_code=1,
                    test_output=f"UI/UX & Anti-Slop Audit Failed: {len(ui_findings)} design/accessibility issues detected.",
                    findings=ui_findings,
                    coaching_guidance="Fix UI/UX defects: replace generic CTA/buzzwords, ensure WCAG alt attributes, and remove clichéd gradients.",
                )
                self.task_engine.record_audit(audit)
                return audit

        # 3. Run automated test command if provided
        exit_code = 0
        output = "No external tests specified; boundaries and UI/UX verified."
        if test_cmd:
            res = subprocess.run(
                test_cmd,
                cwd=task.worktree_path,
                capture_output=True,
                text=True,
            )
            exit_code = res.returncode
            output = f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"

        verdict = "PASS" if exit_code == 0 else "FAIL"
        findings = [] if exit_code == 0 else ["Test execution failed with non-zero exit code."]

        audit = AuditResult(
            task_id=task_id,
            reviewer_role=AgentRole.QA,
            verdict=verdict,
            exit_code=exit_code,
            test_output=output,
            findings=findings,
        )
        self.task_engine.record_audit(audit)
        return audit

    def handle_trainer_remediation(
        self,
        task_id: str,
        symptom: str,
        root_cause: str,
        resolution: str,
        preventive_rule: str,
    ) -> TroubleshootingCase:
        """Trainer analyzes root cause, records to Second Brain KB, and prepares remediation."""
        case = TroubleshootingCase(
            task_id=task_id,
            symptom=symptom,
            root_cause=root_cause,
            resolution=resolution,
            preventive_rule=preventive_rule,
        )
        self.task_engine.record_troubleshooting(case)
        self.sb_bridge.sync_troubleshooting_case(case)
        
        # Reset task to IN_PROGRESS for worker to retry
        self.task_engine.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        return case

    def merge_to_main(self, task_id: str) -> None:
        """Merges an APPROVED task branch into main and tears down the worktree."""
        task = self.task_engine.get_task(task_id)
        if not task or task.status != TaskStatus.APPROVED:
            raise RuntimeError(f"Task {task_id} is not APPROVED for merge (current: {task.status if task else 'None'})")

        # Merge branch into main
        subprocess.run(
            ["git", "merge", "--no-ff", task.branch_name, "-m", f"feat({task.assigned_role.value}): merge {task.id} - {task.title}"],
            cwd=self.project_root,
            capture_output=True,
            check=True,
        )

        # Remove worktree
        if task.worktree_path:
            self.worktree_manager.remove_worktree(
                task.worktree_path, delete_branch=True, branch_name=task.branch_name
            )

        self.task_engine.update_task_status(task_id, TaskStatus.MERGED)

    def auto_execute_lifecycle(
        self,
        task_id: str,
        worker_fn,
        test_cmd: Optional[List[str]] = None,
        max_retries: int = 3,
    ) -> Tuple[bool, str]:
        """Automatically executes task, runs QA gate, triggers Trainer on rejection,
        re-dispatches revisions, and merges on approval without human intervention."""
        task, wt_path = self.dispatch_task(task_id)
        coaching = None

        while task.retry_count < max_retries:
            # 1. Worker executes code (with coaching guidance if this is a revision)
            worker_fn(task, wt_path, coaching)

            # 2. QA runs quality & security gate
            audit = self.run_qa_gate(task_id, test_cmd)

            if audit.verdict == "PASS":
                # Commit any changes in worktree
                subprocess.run(["git", "add", "."], cwd=wt_path, check=False)
                subprocess.run(
                    ["git", "commit", "-m", f"feat({task.assigned_role.value}): complete {task_id}"],
                    cwd=wt_path,
                    check=False,
                )
                self.merge_to_main(task_id)
                return True, f"Task {task_id} PASSED QA and was MERGED to main."

            # 3. QA Rejected -> Automatic Trainer intervention!
            task = self.task_engine.get_task(task_id)  # refreshed retry_count
            findings_str = "; ".join(audit.findings) or "Test assertions failed."
            self.handle_trainer_remediation(
                task_id=task_id,
                symptom=f"QA Rejected on attempt {task.retry_count}: {findings_str}",
                root_cause=f"Failure in execution: {audit.test_output[:200]}",
                resolution="Automatic coaching dispatched to worker for instant revision.",
                preventive_rule="Check and fix failing assertions and boundaries before submission.",
            )
            coaching = f"Trainer Coaching (Attempt {task.retry_count}/{max_retries}): Fix issues: {findings_str}\nDetail: {audit.test_output[:300]}"

        return False, f"Task {task_id} FAILED after {max_retries} attempts. Escalating to architecture review (Aturan 3 Kali Gagal)."
