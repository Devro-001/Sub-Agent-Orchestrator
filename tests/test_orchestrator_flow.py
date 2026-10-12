"""Integration test for full 6-SubAgent Orchestration workflow."""

import tempfile
import unittest
from pathlib import Path

from contracts.types import AgentRole, Task, TaskStatus
from core.orchestrator import Orchestrator
from agents.manager_agent import ManagerAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.qa_agent import QAAgent
from agents.researcher_agent import ResearcherAgent
from agents.trainer_agent import TrainerAgent


class TestOrchestratorFlow(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name) / "test_app"
        self.project_path.mkdir(parents=True)

        self.temp_sb = tempfile.TemporaryDirectory()
        self.sb_path = Path(self.temp_sb.name)
        (self.sb_path / "01_PROFILE").mkdir(parents=True)
        (self.sb_path / "02_RULES_GUIDELINES").mkdir(parents=True)
        (self.sb_path / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log_Modules").mkdir(parents=True)
        (self.sb_path / "06_DATA_SEARCH").mkdir(parents=True)

        (self.sb_path / "01_PROFILE" / "User_Profile.md").write_text("# User Profile\nUsername: test_user", encoding="utf-8")
        (self.sb_path / "02_RULES_GUIDELINES" / "Base_Agent_AI_Guidelines.md").write_text("# Rules", encoding="utf-8")
        self.kb_file = (
            self.sb_path
            / "05_PROJECTS"
            / "Project_Changelog_and_Troubleshooting_Log_Modules"
            / "Project_Changelog_and_Troubleshooting_Log_Part01_1__Database_Penanganan_Bug___Solusi__T.md"
        )
        self.kb_file.write_text("# Troubleshooting KB\n\n🧭 **Navigasi Induk**\n", encoding="utf-8")

        self.orchestrator = Orchestrator(str(self.project_path), str(self.sb_path))
        self.manager = ManagerAgent(self.orchestrator)
        self.backend = BackendAgent(self.orchestrator)
        self.frontend = FrontendAgent(self.orchestrator)
        self.qa = QAAgent(self.orchestrator)
        self.researcher = ResearcherAgent(self.orchestrator)
        self.trainer = TrainerAgent(self.orchestrator)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass
        try:
            self.temp_sb.cleanup()
        except Exception:
            pass

    def test_full_multiagent_lifecycle(self):
        # 1. Manager initializes project
        self.orchestrator.init_project("app-01", "Demo App", "Integration Test App")

        # 2. Data Researcher saves an initial benchmark note
        research_file = self.researcher.save_research_findings(
            "Demo_App_Research", "01_architecture_benchmark.md", "# Benchmark Architecture\nValidated from 5 sources"
        )
        self.assertTrue(research_file.exists())

        # 3. Manager freezes contract
        self.orchestrator.freeze_contract("api.json", '{"version": "1.0.0", "endpoints": ["/api/users"]}')

        # 4. Manager decomposes tasks
        plan_spec = {
            "tasks": [
                {
                    "id": "T-BE-01",
                    "title": "Build Users API Endpoint",
                    "assigned_role": AgentRole.BACKEND.value,
                    "file_boundaries": ["backend/**", "api/**"],
                    "dependencies": [],
                },
                {
                    "id": "T-FE-01",
                    "title": "Build Users List Component",
                    "assigned_role": AgentRole.FRONTEND.value,
                    "file_boundaries": ["frontend/**", "src/components/**"],
                    "dependencies": ["T-BE-01"],
                },
            ]
        }
        tasks = self.manager.decompose_project("app-01", plan_spec)
        self.assertEqual(len(tasks), 2)

        # 5. Dispatch Backend task into its worktree
        be_task, be_wt_path = self.orchestrator.dispatch_task("T-BE-01")
        self.assertTrue(Path(be_wt_path).exists())

        # Backend writes a violating file (touches frontend)
        violating_file = Path(be_wt_path) / "frontend" / "bad.js"
        violating_file.parent.mkdir(parents=True, exist_ok=True)
        violating_file.write_text("console.log('intruder')", encoding="utf-8")

        # 6. QA Audits -> Should FAIL due to boundary violation
        audit_fail = self.qa.audit_task("T-BE-01")
        self.assertEqual(audit_fail.verdict, "FAIL")
        self.assertIn("File boundary violation", audit_fail.test_output)

        # 7. Trainer intervenes: coaches, logs to Second Brain
        self.trainer.handle_incident(
            task_id="T-BE-01",
            symptom="Unauthorized write to frontend/bad.js by Backend worker",
            root_cause="Backend agent strayed outside permitted file boundaries",
            resolution="Removed violating file and restricted write to backend/",
            preventive_rule="Enforce strict role boundary check before committing",
        )
        # Check Second Brain KB updated
        kb_text = self.kb_file.read_text(encoding="utf-8")
        self.assertIn("T-BE-01", kb_text)
        self.assertIn("Unauthorized write to frontend", kb_text)

        # Backend removes violating file and writes proper backend file
        violating_file.unlink()
        backend_file = Path(be_wt_path) / "backend" / "api.py"
        backend_file.parent.mkdir(parents=True, exist_ok=True)
        backend_file.write_text("def get_users(): return []", encoding="utf-8")

        # 8. QA re-audits -> Should PASS
        audit_pass = self.qa.audit_task("T-BE-01")
        self.assertEqual(audit_pass.verdict, "PASS")

        # Commit backend file in worktree
        import subprocess
        subprocess.run(["git", "add", "."], cwd=be_wt_path, check=True)
        subprocess.run(["git", "commit", "-m", "feat(backend): implement users api"], cwd=be_wt_path, check=True)

        # 9. Manager merges to main
        self.orchestrator.merge_to_main("T-BE-01")
        t_be_final = self.orchestrator.task_engine.get_task("T-BE-01")
        self.assertEqual(t_be_final.status, TaskStatus.MERGED)
        self.assertFalse(Path(be_wt_path).exists())  # Worktree torn down cleanly

        # 10. Frontend task is now claimable!
        fe_claimed = self.orchestrator.task_engine.claim_next_task(AgentRole.FRONTEND, "app-01")
        self.assertIsNotNone(fe_claimed)
        self.assertEqual(fe_claimed.id, "T-FE-01")

    def test_autonomous_auto_revision_loop(self):
        """Tests that orchestrator automatically revises rejected code without human intervention."""
        self.orchestrator.init_project("app-auto", "Auto App", "Testing Auto Loop")
        
        task = Task(
            id="T-AUTO-01",
            project_id="app-auto",
            title="Auto Revision Task",
            assigned_role=AgentRole.BACKEND,
            file_boundaries=["backend/**"],
        )
        self.orchestrator.task_engine.add_task(task)

        attempt_counter = [0]

        def simulated_worker(task_obj, worktree_path, coaching_guidance):
            attempt_counter[0] += 1
            wt = Path(worktree_path)
            if attempt_counter[0] == 1:
                # First attempt: makes mistake (writes to frontend)
                bad_dir = wt / "frontend"
                bad_dir.mkdir(parents=True, exist_ok=True)
                (bad_dir / "err.js").write_text("console.log('error')", encoding="utf-8")
            else:
                # Subsequent attempt: follows Trainer coaching, cleans up and writes proper file
                bad_file = wt / "frontend" / "err.js"
                if bad_file.exists():
                    bad_file.unlink()
                good_dir = wt / "backend"
                good_dir.mkdir(parents=True, exist_ok=True)
                (good_dir / "service.py").write_text("def run(): return True", encoding="utf-8")

        # Run fully automated lifecycle
        success, message = self.orchestrator.auto_execute_lifecycle(
            task_id="T-AUTO-01",
            worker_fn=simulated_worker,
            max_retries=3,
        )

        self.assertTrue(success)
        self.assertIn("PASSED QA and was MERGED", message)
        self.assertEqual(attempt_counter[0], 2)  # Proved that it automatically revised on attempt 2!

        # Verify Second Brain received the troubleshooting log
        kb_text = self.kb_file.read_text(encoding="utf-8")
        self.assertIn("T-AUTO-01", kb_text)
        self.assertIn("QA Rejected on attempt 1", kb_text)

    def test_auto_initialization_on_instantiation(self):
        """Tests that a fresh uninitialized project directory is automatically initialized on instantiation."""
        uninit_dir = Path(self.temp_dir.name) / "brand_new_project"
        uninit_dir.mkdir(parents=True)

        # Instantiating Orchestrator should auto-bootstrap the project
        orch = Orchestrator(str(uninit_dir), str(self.sb_path))
        proj = orch.task_engine.get_project("brand-new-project")
        self.assertIsNotNone(proj)
        self.assertEqual(proj.name, "brand_new_project")
        self.assertTrue((uninit_dir / "contracts").exists())
        self.assertTrue((uninit_dir / ".specify" / "memory" / "task_ledger.db").exists())


if __name__ == "__main__":
    unittest.main()

