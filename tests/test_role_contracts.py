"""Tests for Sub-Agent Role Contracts and Boundary Invariants."""

import json
import unittest
from pathlib import Path

from contracts.types import AgentRole
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.qa_agent import QAAgent
from agents.manager_agent import ManagerAgent
from agents.researcher_agent import ResearcherAgent
from agents.trainer_agent import TrainerAgent


class TestRoleContracts(unittest.TestCase):
    """Validates the architectural contract and file boundary invariants of the 6 sub-agents."""

    def setUp(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.contract_file = self.project_root / "contracts" / "role_contracts.json"

    def test_role_contracts_json_schema_and_roles(self):
        self.assertTrue(self.contract_file.exists(), "role_contracts.json must exist")
        data = json.loads(self.contract_file.read_text(encoding="utf-8"))
        
        self.assertIn("roles", data)
        roles = data["roles"]

        # Ensure all 6 AgentRole enum values exist in JSON contract
        for role_enum in AgentRole:
            role_key = role_enum.value
            self.assertIn(role_key, roles, f"Role {role_key} missing from role_contracts.json")
            role_def = roles[role_key]
            self.assertIn("writable_paths", role_def)
            self.assertIn("read_only_paths", role_def)
            self.assertIn("forbidden_write_paths", role_def)

    def test_backend_and_frontend_boundaries_disjoint(self):
        data = json.loads(self.contract_file.read_text(encoding="utf-8"))
        be_writable = set(data["roles"][AgentRole.BACKEND.value]["writable_paths"])
        fe_writable = set(data["roles"][AgentRole.FRONTEND.value]["writable_paths"])

        # Intersection between Backend and Frontend writable paths MUST be empty
        intersection = be_writable.intersection(fe_writable)
        self.assertEqual(
            len(intersection),
            0,
            f"Zero-collision violation: Backend and Frontend overlap on {intersection}",
        )

        # Backend forbidden paths must include client/frontend
        be_forbidden = data["roles"][AgentRole.BACKEND.value]["forbidden_write_paths"]
        self.assertTrue(any("client" in p or "frontend" in p for p in be_forbidden))

        # Frontend forbidden paths must include server/backend
        fe_forbidden = data["roles"][AgentRole.FRONTEND.value]["forbidden_write_paths"]
        self.assertTrue(any("server" in p or "backend" in p for p in fe_forbidden))

    def test_agent_classes_match_role_constants(self):
        self.assertEqual(ManagerAgent.ROLE, AgentRole.MANAGER)
        self.assertEqual(BackendAgent.ROLE, AgentRole.BACKEND)
        self.assertEqual(FrontendAgent.ROLE, AgentRole.FRONTEND)
        self.assertEqual(QAAgent.ROLE, AgentRole.QA)
        self.assertEqual(ResearcherAgent.ROLE, AgentRole.RESEARCHER)
        self.assertEqual(TrainerAgent.ROLE, AgentRole.TRAINER)

    def test_qa_veto_and_read_only_production(self):
        data = json.loads(self.contract_file.read_text(encoding="utf-8"))
        qa_def = data["roles"][AgentRole.QA.value]
        
        # QA cannot write to server, client, or src
        qa_forbidden = qa_def["forbidden_write_paths"]
        self.assertTrue(any("server" in p for p in qa_forbidden))
        self.assertTrue(any("client" in p for p in qa_forbidden))
        self.assertTrue(any("src" in p for p in qa_forbidden))


if __name__ == "__main__":
    unittest.main()
