"""Unit tests for SecondBrainBridge."""

import tempfile
import unittest
from pathlib import Path

from contracts.types import TroubleshootingCase
from core.second_brain_bridge import SecondBrainBridge


class TestSecondBrainBridge(unittest.TestCase):

    def setUp(self):
        self.temp_sb = tempfile.TemporaryDirectory()
        self.sb_path = Path(self.temp_sb.name)

        # Mock folder structure
        (self.sb_path / "01_PROFILE").mkdir(parents=True)
        (self.sb_path / "02_RULES_GUIDELINES").mkdir(parents=True)
        (self.sb_path / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log_Modules").mkdir(parents=True)
        (self.sb_path / "06_DATA_SEARCH").mkdir(parents=True)

        # Write sample files
        (self.sb_path / "01_PROFILE" / "User_Profile.md").write_text("# User Profile\nUsername: test_user", encoding="utf-8")
        (self.sb_path / "02_RULES_GUIDELINES" / "Base_Agent_AI_Guidelines.md").write_text("# Base Guidelines\nPonytail & Anti-slop", encoding="utf-8")
        
        self.kb_file = (
            self.sb_path
            / "05_PROJECTS"
            / "Project_Changelog_and_Troubleshooting_Log_Modules"
            / "Project_Changelog_and_Troubleshooting_Log_Part01_1__Database_Penanganan_Bug___Solusi__T.md"
        )
        self.kb_file.write_text("# Troubleshooting KB\n\n🧭 **Navigasi Induk**\n", encoding="utf-8")

        self.bridge = SecondBrainBridge(str(self.sb_path))

    def tearDown(self):
        self.temp_sb.cleanup()

    def test_context_ingestion(self):
        profile = self.bridge.get_user_profile()
        self.assertIn("Username: test_user", profile)

        guidelines = self.bridge.get_base_guidelines()
        self.assertIn("Ponytail & Anti-slop", guidelines)

        kb = self.bridge.get_troubleshooting_kb()
        self.assertIn("# Troubleshooting KB", kb)

    def test_sync_troubleshooting_case(self):
        case = TroubleshootingCase(
            task_id="TASK-404",
            symptom="ImportError on core.module",
            root_cause="Missing __init__.py in package directory",
            resolution="Created empty __init__.py",
            preventive_rule="Always package Python modules with __init__.py",
        )
        success = self.bridge.sync_troubleshooting_case(case)
        self.assertTrue(success)
        self.assertTrue(case.synced_to_second_brain)

        # Verify file content
        content = self.kb_file.read_text(encoding="utf-8")
        self.assertIn("TASK-404", content)
        self.assertIn("Missing __init__.py", content)

    def test_save_research_note_size_guardrail(self):
        # Valid note <= 45 KB
        note_path = self.bridge.save_research_note(
            topic_folder="test_topic",
            filename="01_note.md",
            content="# Valid Research Note\nData from 5 sources...",
        )
        self.assertTrue(note_path.exists())

        # Exceeds 45 KB -> should raise ValueError
        oversized_content = "X" * (46 * 1024)
        with self.assertRaises(ValueError):
            self.bridge.save_research_note(
                topic_folder="test_topic",
                filename="02_oversized.md",
                content=oversized_content,
            )

    def test_standalone_mode_fallback(self):
        """When Second Brain path is not found and not explicitly given, bridge enters standalone mode."""
        import os
        from unittest.mock import patch

        # Temporarily mock non-existent path
        with patch.dict(os.environ, {"SECOND_BRAIN_PATH": ""}, clear=False):
            with patch.object(SecondBrainBridge, "DEFAULT_SECOND_BRAIN_PATH", "/non/existent/path/for/test"):
                standalone_bridge = SecondBrainBridge(second_brain_path=None)
                self.assertFalse(standalone_bridge.is_active)
                self.assertEqual(standalone_bridge.get_user_profile(), "")
                self.assertEqual(standalone_bridge.get_base_guidelines(), "")
                self.assertEqual(standalone_bridge.get_troubleshooting_kb(), "")
                
                # sync returns False without crashing
                case = TroubleshootingCase("T-1", "s", "rc", "res", "rule")
                self.assertFalse(standalone_bridge.sync_troubleshooting_case(case))


if __name__ == "__main__":
    unittest.main()
