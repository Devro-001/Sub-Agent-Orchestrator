"""Manager Agent (Agent 1): Orchestrator, Task Decomposer & Coordinator."""

from typing import Dict, List, Any
from contracts.types import Task, AgentRole, TaskStatus
from core.orchestrator import Orchestrator


class ManagerAgent:
    """Orchestrator Manager subagent implementation."""

    ROLE = AgentRole.MANAGER

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def build_system_context(self) -> Dict[str, str]:
        """Loads required guidelines from Second Brain."""
        return {
            "profile": self.orchestrator.sb_bridge.get_user_profile(),
            "guidelines": self.orchestrator.sb_bridge.get_base_guidelines(),
        }

    def decompose_project(self, project_id: str, plan_spec: Dict[str, Any]) -> List[Task]:
        """Decomposes project specifications into atomic DAG tasks with strict file boundaries."""
        tasks: List[Task] = []
        for raw_task in plan_spec.get("tasks", []):
            task = Task(
                id=raw_task["id"],
                project_id=project_id,
                title=raw_task["title"],
                assigned_role=AgentRole(raw_task["assigned_role"]),
                status=TaskStatus.IDLE,
                file_boundaries=raw_task.get("file_boundaries", []),
                dependencies=raw_task.get("dependencies", []),
            )
            self.orchestrator.task_engine.add_task(task)
            tasks.append(task)
        return tasks
