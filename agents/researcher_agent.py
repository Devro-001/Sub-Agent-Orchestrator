"""Data Researcher Agent (Agent 5): Multi-Source Online Intelligence & Knowledge Routing."""

from pathlib import Path
from typing import Dict, List, Any
from contracts.types import AgentRole
from core.orchestrator import Orchestrator


class ResearcherAgent:
    """Data Researcher subagent implementation."""

    ROLE = AgentRole.RESEARCHER

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def save_research_findings(self, topic_folder: str, filename: str, content: str) -> Path:
        """Saves verified multi-source research into Second Brain 06_DATA_SEARCH/ maintaining <= 45 KB limit."""
        return self.orchestrator.sb_bridge.save_research_note(topic_folder, filename, content)
