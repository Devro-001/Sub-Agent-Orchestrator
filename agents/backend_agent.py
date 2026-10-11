"""Backend Specialist Agent (Agent 2): Core Logic, API, Database & Backend Tests."""

from pathlib import Path
from typing import Dict, List, Any
from contracts.types import AgentRole, Task
from core.orchestrator import Orchestrator


class BackendAgent:
    """Backend Engineer subagent implementation."""

    ROLE = AgentRole.BACKEND
    DEFAULT_BOUNDARIES = ["server/**", "backend/**", "api/**", "database/**", "lib/core/**", "tests/backend/**"]

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def build_prompt_context(self, task: Task) -> str:
        """Constructs prompt for the backend agent with frozen contracts and Ponytail rules."""
        contracts_content = ""
        for contract_file in self.orchestrator.contracts_dir.glob("*.*"):
            contracts_content += f"\n--- {contract_file.name} ---\n{contract_file.read_text(encoding='utf-8')[:1000]}"

        return f"""
ROLE: Backend Specialist ({self.ROLE.value})
TASK: {task.title} (ID: {task.id})
PERMITTED PATHS: {task.file_boundaries}

MANDATORY RULES:
1. Ponytail Efficiency: YAGNI -> Reuse -> Stdlib -> Native -> Minimal code.
2. Dilarang mengedit file di luar batas (dilarang menyentuh frontend/client).
3. Patuhi kontrak berikut secara presisi:
{contracts_content}
"""
