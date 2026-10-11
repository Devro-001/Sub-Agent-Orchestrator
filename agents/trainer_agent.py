"""Trainer & Reflexion Agent (Agent 6): Continuous Learning, Error Analysis & Second Brain KB Sync."""

from typing import Dict, List, Any
from contracts.types import AgentRole, TroubleshootingCase
from core.orchestrator import Orchestrator


class TrainerAgent:
    """Adaptive Trainer and Reflexion subagent implementation."""

    ROLE = AgentRole.TRAINER

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def handle_incident(
        self,
        task_id: str,
        symptom: str,
        root_cause: str,
        resolution: str,
        preventive_rule: str,
    ) -> TroubleshootingCase:
        """Analyzes incident and records new case in Second Brain Troubleshooting Knowledge Base."""
        return self.orchestrator.handle_trainer_remediation(
            task_id=task_id,
            symptom=symptom,
            root_cause=root_cause,
            resolution=resolution,
            preventive_rule=preventive_rule,
        )
