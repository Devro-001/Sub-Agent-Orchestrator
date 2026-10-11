"""Second Brain Bridge: Integration Engine between Sub-Agents and Obsidian Second Brain."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from contracts.types import TroubleshootingCase


class SecondBrainBridge:
    """Interfaces sub-agents with Second Brain as their persistent central memory."""

    DEFAULT_SECOND_BRAIN_PATH = str(Path.home() / "Documents" / "SecondBrain")
    MAX_FILE_BYTES = 45 * 1024  # 45 KB hard guardrail

    def __init__(
        self,
        second_brain_path: Optional[str] = None,
        workspace_root: Optional[Any] = None,
        auto_bootstrap: bool = False,
        standalone: bool = False,
        **kwargs,
    ):
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else Path.cwd()
        env_path = os.environ.get("SECOND_BRAIN_PATH")

        if second_brain_path:
            self.sb_path = Path(second_brain_path).resolve()
            self.is_standalone = standalone
            if not self.sb_path.exists():
                if auto_bootstrap:
                    self.bootstrap()
                    self.is_active = True
                else:
                    self.is_active = False
                    raise FileNotFoundError(f"Second Brain directory not found at {self.sb_path}")
            else:
                self.is_active = True
        elif env_path:
            self.sb_path = Path(env_path).resolve()
            self.is_standalone = standalone
            if not self.sb_path.exists():
                if auto_bootstrap:
                    self.bootstrap()
                    self.is_active = True
                else:
                    self.is_active = False
                    raise FileNotFoundError(f"Second Brain directory not found at {self.sb_path}")
            else:
                self.is_active = True
        elif standalone:
            self.sb_path = (self.workspace_root / ".second_brain").resolve()
            self.is_standalone = True
            if auto_bootstrap:
                self.bootstrap()
                self.is_active = True
            elif self.sb_path.exists():
                self.is_active = True
            else:
                self.is_active = False
        else:
            default_candidate = Path(self.DEFAULT_SECOND_BRAIN_PATH).resolve()
            if default_candidate.exists():
                self.sb_path = default_candidate
                self.is_active = True
                self.is_standalone = False
            else:
                if auto_bootstrap:
                    self.sb_path = (self.workspace_root / ".second_brain").resolve()
                    self.bootstrap()
                    self.is_active = True
                    self.is_standalone = True
                else:
                    self.sb_path = default_candidate
                    self.is_active = False
                    self.is_standalone = True

    def bootstrap(self) -> None:
        """Auto-bootstraps a minimal Second Brain structure with template files."""
        self.sb_path.mkdir(parents=True, exist_ok=True)

        # Ensure directory hierarchy exists
        (self.sb_path / "01_PROFILE").mkdir(parents=True, exist_ok=True)
        (self.sb_path / "02_RULES_GUIDELINES").mkdir(parents=True, exist_ok=True)
        modules_dir = (
            self.sb_path
            / "05_PROJECTS"
            / "Project_Changelog_and_Troubleshooting_Log_Modules"
        )
        modules_dir.mkdir(parents=True, exist_ok=True)
        (self.sb_path / "06_DATA_SEARCH").mkdir(parents=True, exist_ok=True)

        # 01_PROFILE/User_Profile.md
        profile_file = self.sb_path / "01_PROFILE" / "User_Profile.md"
        if not profile_file.exists():
            profile_file.write_text(
                "# User Profile\n\n- Role: Autonomous Sub-Agent Orchestrator\n- Mode: Standalone\n- Status: Active\n",
                encoding="utf-8",
            )

        # 02_RULES_GUIDELINES/Base_Agent_AI_Guidelines.md
        guidelines_file = self.sb_path / "02_RULES_GUIDELINES" / "Base_Agent_AI_Guidelines.md"
        if not guidelines_file.exists():
            guidelines_file.write_text(
                "# Base Agent AI Guidelines\n\n"
                "## Core Directives\n"
                "- Verification: Iron Law of Verification (No completion claims without fresh verification)\n"
                "- Quality: Anti-Slop & Ponytail Principle\n",
                encoding="utf-8",
            )

        # 05_PROJECTS Troubleshooting KB module & main file
        kb_part1 = (
            modules_dir
            / "Project_Changelog_and_Troubleshooting_Log_Part01_1__Database_Penanganan_Bug___Solusi__T.md"
        )
        if not kb_part1.exists():
            kb_part1.write_text(
                "# Database Penanganan Bug & Solusi (Troubleshooting KB)\n\n🧭 **Navigasi Induk**\n",
                encoding="utf-8",
            )

        main_kb = self.sb_path / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log.md"
        if not main_kb.exists():
            main_kb.write_text(
                "# Project Changelog & Troubleshooting Log\n\n🧭 **Navigasi Induk**\n",
                encoding="utf-8",
            )

        # Second_Brain_Index.md
        index_file = self.sb_path / "Second_Brain_Index.md"
        if not index_file.exists():
            index_file.write_text(
                "# Second Brain Index (MOC)\n\n"
                "- [[01_PROFILE/User_Profile|User Profile]]\n"
                "- [[02_RULES_GUIDELINES/Base_Agent_AI_Guidelines|Guidelines]]\n"
                "- [[05_PROJECTS/Project_Changelog_and_Troubleshooting_Log|Troubleshooting KB]]\n",
                encoding="utf-8",
            )

        self.is_active = True

    def get_user_profile(self) -> str:
        if not self.is_active:
            return ""
        profile_file = self.sb_path / "01_PROFILE" / "User_Profile.md"
        if profile_file.exists():
            return profile_file.read_text(encoding="utf-8")
        return ""

    def get_base_guidelines(self) -> str:
        if not self.is_active:
            return ""
        guideline_file = self.sb_path / "02_RULES_GUIDELINES" / "Base_Agent_AI_Guidelines.md"
        if guideline_file.exists():
            return guideline_file.read_text(encoding="utf-8")
        return ""

    def get_troubleshooting_kb(self) -> str:
        """Reads troubleshooting knowledge base."""
        if not self.is_active:
            return ""
        kb_part1 = (
            self.sb_path
            / "05_PROJECTS"
            / "Project_Changelog_and_Troubleshooting_Log_Modules"
            / "Project_Changelog_and_Troubleshooting_Log_Part01_1__Database_Penanganan_Bug___Solusi__T.md"
        )
        if kb_part1.exists():
            return kb_part1.read_text(encoding="utf-8")

        # Fallback to main file if modules don't exist
        main_kb = self.sb_path / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log.md"
        if main_kb.exists():
            return main_kb.read_text(encoding="utf-8")
        return ""

    def sync_troubleshooting_case(self, case: TroubleshootingCase) -> bool:
        """Appends a new bug and resolution into the Troubleshooting KB."""
        if not self.is_active:
            return False

        target_file = (
            self.sb_path
            / "05_PROJECTS"
            / "Project_Changelog_and_Troubleshooting_Log_Modules"
            / "Project_Changelog_and_Troubleshooting_Log_Part01_1__Database_Penanganan_Bug___Solusi__T.md"
        )
        if not target_file.exists():
            target_file = self.sb_path / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log.md"

        if not target_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(
                "# Database Penanganan Bug & Solusi\n\n🧭 **Navigasi Induk**\n",
                encoding="utf-8",
            )

        content = target_file.read_text(encoding="utf-8")

        today = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"""
### 📌 Kasus: {case.task_id} — {case.symptom[:80]}
- **Tanggal**: {today}
- **Gejala (Symptom)**: {case.symptom}
- **Akar Masalah (Root Cause)**: {case.root_cause}
- **Solusi (Resolution)**: {case.resolution}
- **Pelajaran untuk Masa Depan (Preventive Rule)**: {case.preventive_rule}

---
"""
        # Append before the last navigation link
        if "🧭 **Navigasi Induk**" in content:
            updated_content = content.replace("🧭 **Navigasi Induk**", new_entry + "\n🧭 **Navigasi Induk**")
        else:
            updated_content = content + "\n" + new_entry

        # Size check
        if len(updated_content.encode("utf-8")) > self.MAX_FILE_BYTES:
            # Must not exceed 45 KB
            return False

        target_file.write_text(updated_content, encoding="utf-8")
        case.synced_to_second_brain = True
        return True

    def save_research_note(self, topic_folder: str, filename: str, content: str) -> Path:
        """Saves a modular research note maintaining <= 45 KB limit."""
        if self.is_active:
            target_dir = self.sb_path / "06_DATA_SEARCH" / topic_folder
        else:
            target_dir = self.workspace_root / "research" / topic_folder
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / filename
        content_bytes = len(content.encode("utf-8"))
        if content_bytes > self.MAX_FILE_BYTES:
            raise ValueError(
                f"Content size ({content_bytes} bytes) exceeds Second Brain 45 KB limit ({self.MAX_FILE_BYTES} bytes)"
            )

        target_file.write_text(content, encoding="utf-8")
        return target_file
