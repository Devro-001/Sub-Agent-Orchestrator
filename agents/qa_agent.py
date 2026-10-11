"""Fullstack QA, UI/UX & Security Auditor Agent (Agent 4):
Performs Backend Verification, Security Vulnerability Scans, and Frontend UI/UX & Anti-Slop Audits.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from contracts.types import AgentRole, Task, AuditResult
from core.orchestrator import Orchestrator


class QAAgent:
    """QA, UI/UX and Security Auditor subagent with absolute veto power."""

    ROLE = AgentRole.QA
    DEFAULT_BOUNDARIES = ["tests/**", "e2e/**", "security/**", "audit-report.md"]

    # Anti-Slop & UI/UX Audit Rules
    FORBIDDEN_GENERIC_CTAS = [
        r"\bget started\b",
        r"\blearn more\b",
        r"\bclick here\b",
        r"\bdiscover more\b",
    ]
    AI_BUZZWORDS = [
        r"\brevolutionary\b",
        r"\bseamless\b",
        r"\bnext-gen\b",
        r"\bunleash\b",
        r"\belevate\b",
        r"\bgame-changer\b",
    ]

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def audit_task(self, task_id: str, test_command: Optional[List[str]] = None) -> AuditResult:
        """Runs automated verification, security audit, and frontend UI/UX inspection."""
        task = self.orchestrator.task_engine.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # If this is a Frontend task, run deep UI/UX & Accessibility inspection first
        if task.assigned_role == AgentRole.FRONTEND and task.worktree_path:
            ui_passed, ui_findings = self.audit_frontend_ui_ux(task.worktree_path)
            if not ui_passed:
                audit = AuditResult(
                    task_id=task_id,
                    reviewer_role=AgentRole.QA,
                    verdict="FAIL",
                    exit_code=1,
                    test_output=f"UI/UX & Anti-Slop Quality Gate Failed: {len(ui_findings)} issues found.",
                    findings=ui_findings,
                    coaching_guidance="Revise frontend UI/UX: fix accessibility, eliminate AI-slop copy/gradients, and ensure interactive states.",
                )
                self.orchestrator.task_engine.record_audit(audit)
                return audit

        return self.orchestrator.run_qa_gate(task_id, test_command)

    def audit_frontend_ui_ux(self, worktree_path: str) -> Tuple[bool, List[str]]:
        """Audits UI/UX craft, WCAG accessibility, and Anti-Slop compliance."""
        wt = Path(worktree_path)
        findings: List[str] = []

        ui_files = list(wt.rglob("*.html")) + list(wt.rglob("*.jsx")) + list(wt.rglob("*.tsx")) + list(wt.rglob("*.vue")) + list(wt.rglob("*.css"))

        if not ui_files:
            return True, []

        for f in ui_files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = f.relative_to(wt)

            # 1. Check A11y: Images without alt attribute
            if f.suffix in [".html", ".jsx", ".tsx", ".vue"]:
                img_tags = re.findall(r"<img\b([^>]*)>", content, re.IGNORECASE)
                for img in img_tags:
                    if not re.search(r'\balt\s*=\s*["\']', img, re.IGNORECASE):
                        findings.append(f"[A11y WCAG] {rel_path}: <img> tag missing required 'alt' attribute.")

                # 2. Check Copywriting: Generic AI-slop CTAs
                for cta_pattern in self.FORBIDDEN_GENERIC_CTAS:
                    if re.search(cta_pattern, content, re.IGNORECASE):
                        match = re.search(cta_pattern, content, re.IGNORECASE).group(0)
                        findings.append(f"[Anti-Slop Copy] {rel_path}: Generic CTA detected ('{match}'). Use specific action verbs (Rule R-15).")

                # 3. Check Copywriting: AI Marketing Buzzwords
                for buzz in self.AI_BUZZWORDS:
                    if re.search(buzz, content, re.IGNORECASE):
                        match = re.search(buzz, content, re.IGNORECASE).group(0)
                        findings.append(f"[Anti-Slop Copy] {rel_path}: Empty AI marketing buzzword detected ('{match}') (Rule R-16).")

                # 4. Check Visual: Generic purple-to-blue gradient slop
                if re.search(r"from-purple-\d+\s+to-blue-\d+", content, re.IGNORECASE) or re.search(r"linear-gradient\(.*#8[a-f0-9]{5}.*#3[a-f0-9]{5}\)", content, re.IGNORECASE):
                    findings.append(f"[Anti-Slop Visual] {rel_path}: Generic purple-to-blue neon gradient detected without brand identity (Rule R-01).")

                # 5. Check Tap Target & Buttons: Empty buttons without accessible label
                empty_buttons = re.findall(r"<button\b[^>]*>\s*</button>", content, re.IGNORECASE)
                if empty_buttons:
                    findings.append(f"[A11y UX] {rel_path}: Empty <button> found without text or aria-label (WCAG AA).")

        passed = len(findings) == 0
        return passed, findings
