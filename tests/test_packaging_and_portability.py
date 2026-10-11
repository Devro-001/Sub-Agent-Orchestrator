"""Tests for packaging, portability, standalone auto-bootstrap, and CLI entry points."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from contracts.types import TroubleshootingCase
from core.cli import build_parser, main as cli_main
from core.second_brain_bridge import SecondBrainBridge

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPackagingAndPortability(unittest.TestCase):
    """Verifies packaging, standalone portability, environment overrides, and CLI invocation."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # =========================================================================
    # Group 1: Standalone Mode & Auto-Bootstrap
    # =========================================================================

    def test_standalone_auto_bootstrap_creates_required_structure(self):
        """Standalone bridge auto-bootstraps full directory structure and template files."""
        sb_target = self.temp_path / "standalone_sb"
        self.assertFalse(sb_target.exists())

        bridge = SecondBrainBridge(
            second_brain_path=str(sb_target),
            auto_bootstrap=True,
            standalone=True,
        )

        self.assertTrue(sb_target.exists())
        self.assertTrue(bridge.is_active)
        self.assertTrue(bridge.is_standalone)

        # Verify directory structure
        self.assertTrue((sb_target / "01_PROFILE").is_dir())
        self.assertTrue((sb_target / "02_RULES_GUIDELINES").is_dir())
        self.assertTrue((sb_target / "05_PROJECTS").is_dir())
        self.assertTrue((sb_target / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log_Modules").is_dir())
        self.assertTrue((sb_target / "06_DATA_SEARCH").is_dir())

        # Verify bootstrapped template files
        self.assertTrue((sb_target / "01_PROFILE" / "User_Profile.md").is_file())
        self.assertTrue((sb_target / "02_RULES_GUIDELINES" / "Base_Agent_AI_Guidelines.md").is_file())
        self.assertTrue((sb_target / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log.md").is_file())
        self.assertTrue((sb_target / "Second_Brain_Index.md").is_file())

        # Verify readability
        self.assertIn("User Profile", bridge.get_user_profile())
        self.assertIn("Base Agent AI Guidelines", bridge.get_base_guidelines())
        self.assertIn("Troubleshooting", bridge.get_troubleshooting_kb())

    def test_standalone_auto_bootstrap_allows_sync_and_research(self):
        """Auto-bootstrapped standalone bridge seamlessly handles KB sync and research notes."""
        sb_target = self.temp_path / "standalone_sb_ops"
        bridge = SecondBrainBridge(
            second_brain_path=str(sb_target),
            auto_bootstrap=True,
            standalone=True,
        )

        # 1. Sync a troubleshooting case
        case = TroubleshootingCase(
            task_id="T-BOOT-01",
            symptom="ModuleNotFoundError on missing package",
            root_cause="Virtual environment not activated",
            resolution="Activated venv and installed wheel",
            preventive_rule="Check sys.prefix before running entrypoint",
        )
        synced = bridge.sync_troubleshooting_case(case)
        self.assertTrue(synced)
        self.assertTrue(case.synced_to_second_brain)

        kb_content = bridge.get_troubleshooting_kb()
        self.assertIn("T-BOOT-01", kb_content)
        self.assertIn("Virtual environment not activated", kb_content)

        # 2. Save a modular research note
        note_file = bridge.save_research_note(
            topic_folder="portability_study",
            filename="01_standalone_bootstrap.md",
            content="# Portability Benchmark\nStandalone bootstrap completed without external dependencies.",
        )
        self.assertTrue(note_file.exists())
        self.assertIn("Portability Benchmark", note_file.read_text(encoding="utf-8"))

    def test_standalone_auto_bootstrap_without_external_folder(self):
        """When external Second Brain folder is missing, bridge auto-bootstraps in workspace root."""
        workspace = self.temp_path / "isolated_workspace"
        workspace.mkdir(parents=True)

        with patch.dict(os.environ, {"SECOND_BRAIN_PATH": ""}, clear=False):
            with patch.object(SecondBrainBridge, "DEFAULT_SECOND_BRAIN_PATH", "/tmp/non_existent_external_sb_dir"):
                bridge = SecondBrainBridge(
                    second_brain_path=None,
                    workspace_root=workspace,
                    auto_bootstrap=True,
                )

                self.assertTrue(bridge.is_active)
                self.assertTrue(bridge.is_standalone)
                expected_dot_sb = (workspace / ".second_brain").resolve()
                self.assertEqual(bridge.sb_path, expected_dot_sb)
                self.assertTrue(expected_dot_sb.exists())
                self.assertTrue((expected_dot_sb / "01_PROFILE" / "User_Profile.md").exists())

    # =========================================================================
    # Group 2: SECOND_BRAIN_PATH Environment Variable
    # =========================================================================

    def test_respects_second_brain_path_env_var(self):
        """SecondBrainBridge respects SECOND_BRAIN_PATH when second_brain_path is None."""
        env_sb = self.temp_path / "env_second_brain"
        env_sb.mkdir(parents=True)

        # Populate minimal files
        (env_sb / "01_PROFILE").mkdir()
        (env_sb / "01_PROFILE" / "User_Profile.md").write_text("# Env Profile\nUsername: env_user", encoding="utf-8")

        with patch.dict(os.environ, {"SECOND_BRAIN_PATH": str(env_sb)}, clear=False):
            bridge = SecondBrainBridge()
            self.assertEqual(bridge.sb_path, env_sb.resolve())
            self.assertTrue(bridge.is_active)
            self.assertIn("env_user", bridge.get_user_profile())

    def test_explicit_param_overrides_env_var(self):
        """Explicit second_brain_path parameter takes precedence over SECOND_BRAIN_PATH env var."""
        env_sb = self.temp_path / "env_sb"
        env_sb.mkdir(parents=True)
        (env_sb / "01_PROFILE").mkdir()
        (env_sb / "01_PROFILE" / "User_Profile.md").write_text("# Env Profile", encoding="utf-8")

        explicit_sb = self.temp_path / "explicit_sb"
        explicit_sb.mkdir(parents=True)
        (explicit_sb / "01_PROFILE").mkdir()
        (explicit_sb / "01_PROFILE" / "User_Profile.md").write_text("# Explicit Profile", encoding="utf-8")

        with patch.dict(os.environ, {"SECOND_BRAIN_PATH": str(env_sb)}, clear=False):
            bridge = SecondBrainBridge(second_brain_path=str(explicit_sb))
            self.assertEqual(bridge.sb_path, explicit_sb.resolve())
            self.assertIn("Explicit Profile", bridge.get_user_profile())

    def test_second_brain_path_env_var_with_auto_bootstrap(self):
        """SECOND_BRAIN_PATH pointing to non-existent directory auto-bootstraps when requested."""
        new_env_sb = self.temp_path / "new_env_sb"
        self.assertFalse(new_env_sb.exists())

        with patch.dict(os.environ, {"SECOND_BRAIN_PATH": str(new_env_sb)}, clear=False):
            bridge = SecondBrainBridge(auto_bootstrap=True)
            self.assertEqual(bridge.sb_path, new_env_sb.resolve())
            self.assertTrue(bridge.is_active)
            self.assertTrue(new_env_sb.exists())
            self.assertTrue((new_env_sb / "01_PROFILE" / "User_Profile.md").exists())

    # =========================================================================
    # Group 3: CLI Help and Entrypoint Invocation
    # =========================================================================

    def test_python_module_cli_help_invocation(self):
        """Runs 'python3 -m core.cli --help' and verifies exit code 0 and usage content."""
        result = subprocess.run(
            [sys.executable, "-m", "core.cli", "--help"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"CLI help failed with stderr: {result.stderr}")
        self.assertIn("Autonomous 6-SubAgent Orchestrator CLI", result.stdout)
        self.assertIn("init", result.stdout)
        self.assertIn("tasks", result.stdout)
        self.assertIn("freeze-contract", result.stdout)
        self.assertIn("dispatch", result.stdout)
        self.assertIn("qa", result.stdout)
        self.assertIn("merge", result.stdout)
        self.assertIn("run-auto", result.stdout)

    def test_bin_orchestrator_script_help_invocation(self):
        """Runs 'bin/sub-agent-orchestrator --help' and verifies exit code 0 and usage content."""
        script_path = PROJECT_ROOT / "bin" / "sub-agent-orchestrator"
        self.assertTrue(script_path.exists())

        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"bin script failed with stderr: {result.stderr}")
        self.assertIn("Autonomous 6-SubAgent Orchestrator CLI", result.stdout)
        self.assertIn("init", result.stdout)
        self.assertIn("tasks", result.stdout)
        self.assertIn("run-auto", result.stdout)

    def test_cli_parser_programmatic_structure(self):
        """Validates parser creation and argument structure programmatically."""
        parser = build_parser()
        args = parser.parse_args(["init", "--id", "P-TEST", "--name", "Test Project", "--desc", "Test Desc"])
        self.assertEqual(args.command, "init")
        self.assertEqual(args.id, "P-TEST")
        self.assertEqual(args.name, "Test Project")
        self.assertEqual(args.desc, "Test Desc")

        args_qa = parser.parse_args(["qa", "TASK-123"])
        self.assertEqual(args_qa.command, "qa")
        self.assertEqual(args_qa.task_id, "TASK-123")


if __name__ == "__main__":
    unittest.main()
