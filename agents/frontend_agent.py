"""Frontend Specialist Agent (Agent 3): UI/UX, Accessibility, Responsive Components & Anti-Slop."""

from typing import Dict, List, Any
from contracts.types import AgentRole, Task
from core.orchestrator import Orchestrator


class FrontendAgent:
    """Frontend Engineer subagent implementation."""

    ROLE = AgentRole.FRONTEND
    DEFAULT_BOUNDARIES = ["client/**", "frontend/**", "src/components/**", "styles/**", "public/**", "tests/frontend/**"]

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def build_prompt_context(self, task: Task) -> str:
        """Constructs prompt for the frontend agent with Anti-Slop and 3 Dials directives."""
        return f"""
ROLE: Frontend Specialist ({self.ROLE.value})
TASK: {task.title} (ID: {task.id})
PERMITTED PATHS: {task.file_boundaries}

MANDATORY RULES:
1. Anti-Slop: Tidak menggunakan gradien generik AI slop atau layout template murahan.
2. 3 Dials Protocol: Deklarasikan Context, Energy (1-3), Rhythm (1-3), Motion (1-3) di awal.
3. Aksesibilitas WCAG AA: Kontras teks >= 4.5:1, target sentuh >= 44x44px.
4. Konsumsi kontrak API terbekukan tanpa mengubahnya.
"""
