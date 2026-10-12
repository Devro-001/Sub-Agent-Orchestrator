"""Tests for Antigravity Bridge, Model Routing Triad, and Skill Clustering Integration."""

import unittest
from pathlib import Path
from contracts.types import AgentRole
from core.antigravity_bridge import AntigravityBridge


class TestAntigravityBridge(unittest.TestCase):
    """Verifies that the AntigravityBridge properly binds the 6 sub-agents

    to their specialized skills, model configurations, and runtime limits.
    """

    def setUp(self):
        self.bridge = AntigravityBridge()

    def test_all_six_roles_have_antigravity_config(self):
        for role in AgentRole:
            cfg = self.bridge.get_antigravity_config(role)
            self.assertIn("model", cfg, f"Role {role.value} missing model")
            self.assertIn("role_title", cfg, f"Role {role.value} missing role_title")
            self.assertIn("enabled_tools", cfg, f"Role {role.value} missing enabled_tools")
            self.assertIn("specialized_skills", cfg, f"Role {role.value} missing specialized_skills")
            self.assertIn("compaction_threshold", cfg, f"Role {role.value} missing compaction_threshold")
            self.assertIn("budget", cfg, f"Role {role.value} missing budget")

    def test_every_subagent_has_at_least_five_skills(self):
        for role in AgentRole:
            cfg = self.bridge.get_antigravity_config(role)
            skills = cfg.get("specialized_skills", [])
            self.assertGreaterEqual(
                len(skills),
                5,
                f"Role {role.value} must have at least 5 specialized skills, got {len(skills)}",
            )

    def test_model_routing_triad(self):
        # Manager and Trainer should use Pro reasoning model
        manager_cfg = self.bridge.get_antigravity_config(AgentRole.MANAGER)
        trainer_cfg = self.bridge.get_antigravity_config(AgentRole.TRAINER)
        self.assertIn("pro", manager_cfg["model"].lower())
        self.assertIn("pro", trainer_cfg["model"].lower())

        # Workers should use Flash models for high performance & token efficiency
        backend_cfg = self.bridge.get_antigravity_config(AgentRole.BACKEND)
        frontend_cfg = self.bridge.get_antigravity_config(AgentRole.FRONTEND)
        qa_cfg = self.bridge.get_antigravity_config(AgentRole.QA)
        self.assertIn("flash", backend_cfg["model"].lower())
        self.assertIn("flash", frontend_cfg["model"].lower())
        self.assertIn("flash", qa_cfg["model"].lower())

    def test_export_ide_manifest_completeness(self):
        manifest = self.bridge.export_ide_manifest()
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertIn("subagents", manifest)
        self.assertEqual(len(manifest["subagents"]), len(AgentRole))

        for role in AgentRole:
            self.assertIn(role.value, manifest["subagents"])
            subagent = manifest["subagents"][role.value]
            self.assertTrue(len(subagent["specialized_skills"]) >= 5)
            self.assertIsInstance(subagent["skill_paths"], list)

    def test_sdk_subagent_config_generation(self):
        config = self.bridge.build_sdk_subagent_config(AgentRole.BACKEND)
        self.assertIsNotNone(config)
        # Should either be a types.SubagentConfig instance or dictionary with name
        if isinstance(config, dict):
            self.assertEqual(config["name"], AgentRole.BACKEND.value)
        else:
            self.assertEqual(config.name, AgentRole.BACKEND.value)


if __name__ == "__main__":
    unittest.main()
