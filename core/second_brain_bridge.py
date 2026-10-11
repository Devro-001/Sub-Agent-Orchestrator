"""Second Brain Bridge: Integration Engine between Sub-Agents and Obsidian Second Brain."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from contracts.types import TroubleshootingCase


class SecondBrainBridge:
    """Interaces sub-agents with Second Brain as their persistent central memory."""

    DEFAULT_SECOND_BRAIN_PATH = "/home/rerei/Documents/SecondBrain"
    MAX_FILE_BYTES = 45 * 1024  # 45 KB hard guardrail

    def __init__(self, second_brain_path: Optional[str] = None):
        self.sb_path = Path(second_brain_path or self.DEFAULT_SECOND_BRAIN_PATH).resolve()
        if not self.sb_path.exists():
            raise FileNotFoundError(f"Second Brain directory not found at {self.sb_path}")

    def get_user_profile(self) -> str:
        profile_file = self.sb_path / "01_PROFILE" / "User_Profile.md"
        if profile_file.exists():
            return profile_file.read_text(encoding="utf-8")
        return ""

    def get_base_guidelines(self) -> str:
        guideline_file = self.sb_path / "02_RULES_GUIDELINES" / "Base_Agent_AI_Guidelines.md"
        if guideline_file.exists():
            return guideline_file.read_text(encoding="utf-8")
        return ""

    def get_troubleshooting_kb(self) -> str:
        """Reads troubleshooting knowledge base."""
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
        target_file = (
            self.sb_path
            / "05_PROJECTS"
            / "Project_Changelog_and_Troubleshooting_Log_Modules"
            / "Project_Changelog_and_Troubleshooting_Log_Part01_1__Database_Penanganan_Bug___Solusi__T.md"
        )
        if not target_file.exists():
            target_file = self.sb_path / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log.md"

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
        """Saves a modular research note to 06_DATA_SEARCH/<topic_folder>/."""
        target_dir = self.sb_path / "06_DATA_SEARCH" / topic_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = target_dir / filename
        content_bytes = len(content.encode("utf-8"))
        if content_bytes > self.MAX_FILE_BYTES:
            raise ValueError(
                f"Content size ({content_bytes} bytes) exceeds Second Brain 45 KB limit ({self.MAX_FILE_BYTES} bytes)"
            )

        target_file.write_text(content, encoding="utf-8")
        return target_file
