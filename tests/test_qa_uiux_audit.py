"""Unit test for QA Agent's UI/UX, Accessibility (WCAG AA), and Anti-Slop auditing."""

import tempfile
import unittest
from pathlib import Path

from contracts.types import AgentRole, Task, TaskStatus
from core.orchestrator import Orchestrator
from agents.qa_agent import QAAgent


class TestQAUIUXAudit(unittest.TestCase):

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

        (self.sb_path / "01_PROFILE" / "User_Profile.md").write_text("# User Profile\nUsername: rerei", encoding="utf-8")
        (self.sb_path / "02_RULES_GUIDELINES" / "Base_Agent_AI_Guidelines.md").write_text("# Rules", encoding="utf-8")
        (self.sb_path / "05_PROJECTS" / "Project_Changelog_and_Troubleshooting_Log_Modules" / "Project_Changelog_and_Troubleshooting_Log_Part01_1__Database_Penanganan_Bug___Solusi__T.md").write_text("# KB\n🧭 **Navigasi Induk**\n", encoding="utf-8")

        self.orchestrator = Orchestrator(str(self.project_path), str(self.sb_path))
        self.qa = QAAgent(self.orchestrator)

    def tearDown(self):
        self.temp_dir.cleanup()
        self.temp_sb.cleanup()

    def test_qa_rejects_slop_ui(self):
        """QA should reject frontend code with generic CTAs, AI buzzwords, and missing alt attributes."""
        self.orchestrator.init_project("app-ui", "UI App")
        task = Task(
            id="T-UI-01",
            project_id="app-ui",
            title="Build Hero Landing Page",
            assigned_role=AgentRole.FRONTEND,
            file_boundaries=["frontend/**"],
        )
        self.orchestrator.task_engine.add_task(task)
        t, wt_path = self.orchestrator.dispatch_task("T-UI-01")
        wt = Path(wt_path)

        # Write UI with Anti-Slop & A11y defects:
        # 1. Generic CTA 'Get Started'
        # 2. AI Buzzword 'seamless'
        # 3. <img> without alt attribute
        # 4. Generic purple-to-blue gradient
        hero_file = wt / "frontend" / "Hero.jsx"
        hero_file.parent.mkdir(parents=True, exist_ok=True)
        hero_file.write_text("""
        export default function Hero() {
            return (
                <div className="bg-gradient-to-r from-purple-600 to-blue-600">
                    <h1>Experience our seamless platform</h1>
                    <img src="/hero.png" />
                    <button>Get Started</button>
                </div>
            );
        }
        """, encoding="utf-8")

        # Run QA audit on frontend task
        audit = self.qa.audit_task("T-UI-01")

        self.assertEqual(audit.verdict, "FAIL")
        self.assertIn("UI/UX & Anti-Slop", audit.test_output)
        
        # Check specific findings detected by QA
        findings_str = " ".join(audit.findings)
        self.assertIn("missing required 'alt' attribute", findings_str)
        self.assertIn("Generic CTA detected ('Get Started')", findings_str)
        self.assertIn("Empty AI marketing buzzword detected ('seamless')", findings_str)
        self.assertIn("Generic purple-to-blue neon gradient", findings_str)

    def test_qa_approves_crafted_ui(self):
        """QA should approve high-craft frontend code adhering to Anti-Slop and A11y."""
        self.orchestrator.init_project("app-ui-craft", "UI Craft App")
        task = Task(
            id="T-UI-02",
            project_id="app-ui-craft",
            title="Build Crafted Hero Page",
            assigned_role=AgentRole.FRONTEND,
            file_boundaries=["frontend/**"],
        )
        self.orchestrator.task_engine.add_task(task)
        t, wt_path = self.orchestrator.dispatch_task("T-UI-02")
        wt = Path(wt_path)

        # Write clean, accessible, crafted UI
        hero_file = wt / "frontend" / "Hero.jsx"
        hero_file.parent.mkdir(parents=True, exist_ok=True)
        hero_file.write_text("""
        export default function Hero() {
            return (
                <div className="bg-zinc-950 text-zinc-100 p-8">
                    <h1 className="text-3xl font-bold tracking-tight">Manajemen Kas Kelas Terbuka</h1>
                    <img src="/hero.webp" alt="Tangkapan layar dasbor kas kelas" className="rounded-lg border border-zinc-800" />
                    <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-md font-medium">Buka Catatan Transaksi</button>
                </div>
            );
        }
        """, encoding="utf-8")

        audit = self.qa.audit_task("T-UI-02")
        self.assertEqual(audit.verdict, "PASS")
        self.assertEqual(len(audit.findings), 0)


if __name__ == "__main__":
    unittest.main()
