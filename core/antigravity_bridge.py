"""Antigravity Bridge: Native Integration between Sub-Agent Orchestrator and Google Antigravity SDK & IDE."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from contracts.types import AgentRole


class AntigravityBridge:
    """Bridges Sub-Agent Orchestrator role boundaries, models, and skill clusters

    into Google Antigravity SDK LocalAgentConfig and Antigravity IDE subagents.
    """

    DEFAULT_SKILLS_ROOT = "/home/rerei/.agents"

    def __init__(
        self,
        contracts_file: Optional[str] = None,
        skills_root: Optional[str] = None,
    ):
        if contracts_file:
            self.contracts_file = Path(contracts_file).resolve()
        else:
            self.contracts_file = (
                Path(__file__).resolve().parent.parent / "contracts" / "role_contracts.json"
            )

        self.skills_root = Path(
            skills_root or os.getenv("AGENTS_SKILLS_PATH", self.DEFAULT_SKILLS_ROOT)
        ).resolve()

        self._contract_data = self._load_contracts()

    def _load_contracts(self) -> Dict[str, Any]:
        if not self.contracts_file.exists():
            raise FileNotFoundError(f"Role contracts file not found: {self.contracts_file}")
        return json.loads(self.contracts_file.read_text(encoding="utf-8"))

    def get_role_metadata(self, role: AgentRole) -> Dict[str, Any]:
        """Returns the complete contract and Antigravity metadata for a role."""
        role_key = role.value if isinstance(role, AgentRole) else role
        roles_dict = self._contract_data.get("roles", {})
        if role_key not in roles_dict:
            raise KeyError(f"Role '{role_key}' not found in role contracts.")
        return roles_dict[role_key]

    def get_antigravity_config(self, role: AgentRole) -> Dict[str, Any]:
        """Returns the Antigravity-specific configuration (model, tools, skills, budget) for a role."""
        role_meta = self.get_role_metadata(role)
        return role_meta.get("antigravity", {})

    def resolve_skill_paths(self, role: AgentRole) -> List[str]:
        """Resolves existing on-disk paths for specialized skills associated with a role."""
        ag_config = self.get_antigravity_config(role)
        skill_names = ag_config.get("specialized_skills", [])
        
        resolved_paths: List[str] = []
        for name in skill_names:
            skill_dir = self.skills_root / name
            if skill_dir.exists():
                resolved_paths.append(str(skill_dir))
            else:
                # Fallback check if it's within a subdirectory
                found = list(self.skills_root.glob(f"**/{name}/SKILL.md"))
                if found:
                    resolved_paths.append(str(found[0].parent))
        return resolved_paths

    def export_ide_manifest(self) -> Dict[str, Any]:
        """Exports a ready-to-use manifest for Antigravity IDE (define_subagent and invoke_subagent)."""
        manifest: Dict[str, Any] = {
            "version": "1.0.0",
            "orchestrator": "Sub-Agent Orchestrator",
            "skills_root": str(self.skills_root),
            "subagents": {},
        }

        roles_dict = self._contract_data.get("roles", {})
        for role_key, role_meta in roles_dict.items():
            ag_config = role_meta.get("antigravity", {})
            skill_paths = []
            for name in ag_config.get("specialized_skills", []):
                p = self.skills_root / name
                if p.exists():
                    skill_paths.append(str(p))

            manifest["subagents"][role_key] = {
                "name": role_key,
                "role_title": ag_config.get("role_title", role_key),
                "model": ag_config.get("model", "gemini-3.8-flash"),
                "compaction_threshold": ag_config.get("compaction_threshold", 35000),
                "enabled_tools": ag_config.get("enabled_tools", []),
                "specialized_skills": ag_config.get("specialized_skills", []),
                "skill_paths": skill_paths,
                "writable_paths": role_meta.get("writable_paths", []),
                "forbidden_write_paths": role_meta.get("forbidden_write_paths", []),
                "budget": ag_config.get("budget", {}),
            }

        return manifest

    def build_sdk_subagent_config(self, role: AgentRole) -> Any:
        """Constructs a types.SubagentConfig instance for Google Antigravity SDK.

        Falls back gracefully to a dictionary if google-antigravity is not installed.
        """
        role_meta = self.get_role_metadata(role)
        ag_config = role_meta.get("antigravity", {})

        try:
            from google.antigravity import types

            tool_map = {
                "view_file": types.BuiltinTools.VIEW_FILE,
                "create_file": types.BuiltinTools.CREATE_FILE,
                "edit_file": types.BuiltinTools.EDIT_FILE,
                "run_command": types.BuiltinTools.RUN_COMMAND,
                "search_dir": types.BuiltinTools.SEARCH_DIR,
                "list_dir": types.BuiltinTools.LIST_DIR,
                "start_subagent": types.BuiltinTools.START_SUBAGENT,
                "ask_question": types.BuiltinTools.ASK_QUESTION,
            }

            enabled_tools = []
            for t in ag_config.get("enabled_tools", []):
                t_lower = t.lower()
                if t_lower in tool_map:
                    enabled_tools.append(tool_map[t_lower])

            return types.SubagentConfig(
                name=role.value if isinstance(role, AgentRole) else role,
                description=f"{ag_config.get('role_title', role)}. Allowed: {role_meta.get('writable_paths')}",
                capabilities=types.SubagentCapabilities(
                    agent_behavior=types.AgentBehavior.AUTONOMOUS,
                    enabled_tools=enabled_tools,
                ),
            )
        except ImportError:
            # Fallback to pure dictionary representation for environments without SDK
            return {
                "name": role.value if isinstance(role, AgentRole) else role,
                "description": f"{ag_config.get('role_title', role)}. Allowed: {role_meta.get('writable_paths')}",
                "model": ag_config.get("model", "gemini-3.8-flash"),
                "enabled_tools": ag_config.get("enabled_tools", []),
                "skills_paths": self.resolve_skill_paths(role),
                "compaction_threshold": ag_config.get("compaction_threshold", 35000),
            }

    def build_sdk_orchestrator_config(self, repo_path: str) -> Any:
        """Constructs the root LocalAgentConfig for the Master Orchestrator."""
        manager_meta = self.get_role_metadata(AgentRole.MANAGER)
        ag_config = manager_meta.get("antigravity", {})
        subagent_roles = [
            AgentRole.BACKEND,
            AgentRole.FRONTEND,
            AgentRole.QA,
            AgentRole.RESEARCHER,
            AgentRole.TRAINER,
        ]

        subagents_configs = [self.build_sdk_subagent_config(r) for r in subagent_roles]

        try:
            from google.antigravity import LocalAgentConfig, types

            return LocalAgentConfig(
                model=ag_config.get("model", "gemini-2.5-pro"),
                system_instructions=(
                    f"Anda adalah Lead Architect & Orchestrator otonom untuk {repo_path}.\n"
                    "Ikuti alur deterministik:\n"
                    "1. Bekukan spesifikasi kontrak di contracts/types.ts sebelum koding.\n"
                    "2. Delegasikan pekerjaan ke sub-agent pada worktree terisolasi (.worktrees/).\n"
                    "3. Lakukan audit via QA dan Security Auditor sebelum merge ke main.\n"
                ),
                capabilities=types.CapabilitiesConfig(
                    enable_subagents=True,
                    max_subagent_depth=2,
                    allowed_subagents=[r.value for r in subagent_roles],
                    agent_behavior=types.AgentBehavior.AUTONOMOUS,
                ),
                subagents=subagents_configs,
                compaction_config=types.CompactionConfig(
                    token_threshold=ag_config.get("compaction_threshold", 65000)
                ),
                budget_config=types.BudgetConfig(
                    max_model_calls=ag_config.get("budget", {}).get("max_model_calls", 15),
                    max_tool_calls=ag_config.get("budget", {}).get("max_tool_calls", 40),
                    max_input_tokens=ag_config.get("budget", {}).get("max_input_tokens", 200000),
                    max_total_tokens=ag_config.get("budget", {}).get("max_total_tokens", 240000),
                ),
                skills_paths=self.resolve_skill_paths(AgentRole.MANAGER),
            )
        except ImportError:
            return {
                "model": ag_config.get("model", "gemini-2.5-pro"),
                "capabilities": {
                    "enable_subagents": True,
                    "max_subagent_depth": 2,
                    "allowed_subagents": [r.value for r in subagent_roles],
                },
                "subagents": subagents_configs,
                "skills_paths": self.resolve_skill_paths(AgentRole.MANAGER),
            }
