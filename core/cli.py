"""Command Line Interface for Sub-Agent Orchestrator."""

import argparse
import sys
from pathlib import Path

# Ensure project root is in sys.path when invoked directly
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from typing import List, Optional
from contracts.types import AgentRole, TaskStatus
from core.orchestrator import Orchestrator


def find_project_root(explicit_root: Optional[str] = None) -> Path:
    """Finds project root by explicit path, search upwards for marker files, or current directory."""
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()

    current = Path.cwd().resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists() or (parent / ".specify").exists() or (parent / "pyproject.toml").exists():
            return parent
    return current


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sub-agent-orchestrator",
        description="Autonomous 6-SubAgent Orchestrator CLI with Second Brain Integration",
    )
    parser.add_argument(
        "--project-root",
        "--root",
        dest="project_root",
        default=None,
        help="Target project root directory (defaults to auto-detected project root or current working directory)",
    )
    parser.add_argument(
        "--second-brain-path",
        "--sb-path",
        dest="second_brain_path",
        default=None,
        help="Custom path to Second Brain directory (defaults to SECOND_BRAIN_PATH env or ~/Documents/SecondBrain)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="sub-agent-orchestrator 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init
    init_parser = subparsers.add_parser("init", help="Initialize orchestrator for a project")
    init_parser.add_argument("--id", default="proj-001", help="Project identifier")
    init_parser.add_argument("--name", required=True, help="Project name")
    init_parser.add_argument("--desc", default="", help="Project description")

    # Tasks
    tasks_parser = subparsers.add_parser("tasks", help="List all tasks and their status")
    tasks_parser.add_argument("--project-id", default=None, help="Filter by project ID")

    # Freeze Contract
    contract_parser = subparsers.add_parser("freeze-contract", help="Freeze an API contract")
    contract_parser.add_argument("file", help="Contract filename")
    contract_parser.add_argument("content", help="Contract content")

    # Dispatch
    dispatch_parser = subparsers.add_parser("dispatch", help="Dispatch task into isolated worktree")
    dispatch_parser.add_argument("task_id", help="Task ID")

    # QA
    qa_parser = subparsers.add_parser("qa", help="Run QA & security audit on a task worktree")
    qa_parser.add_argument("task_id", help="Task ID")

    # Merge
    merge_parser = subparsers.add_parser("merge", help="Merge an approved task worktree to main")
    merge_parser.add_argument("task_id", help="Task ID")

    # Run Auto (Autonomous Self-Healing Loop)
    auto_parser = subparsers.add_parser("run-auto", help="Run autonomous execution with QA auto-remediation loop")
    auto_parser.add_argument("task_id", help="Task ID")
    auto_parser.add_argument("--retries", type=int, default=3, help="Max retry attempts before escalation")

    # Antigravity Manifest
    ag_parser = subparsers.add_parser(
        "antigravity-manifest", help="Export Antigravity SDK & IDE subagent configuration manifest"
    )
    ag_parser.add_argument("--json", action="store_true", help="Print as raw JSON")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_root = find_project_root(args.project_root)
    orchestrator = Orchestrator(str(project_root), second_brain_path=args.second_brain_path)

    if args.command == "init":
        p = orchestrator.init_project(args.id, args.name, args.desc)
        print(f"✅ Initialized project '{p.name}' ({p.id}) at {p.root_path}")
        return 0

    elif args.command == "tasks":
        tasks = orchestrator.task_engine.list_tasks(args.project_id)
        if not tasks:
            print("No tasks found.")
            return 0
        print(f"{'ID':<12} {'ROLE':<25} {'STATUS':<15} {'TITLE'}")
        print("-" * 75)
        for t in tasks:
            print(f"{t.id:<12} {t.assigned_role.value:<25} {t.status.value:<15} {t.title}")
        return 0

    elif args.command == "freeze-contract":
        cf = orchestrator.freeze_contract(args.file, args.content)
        print(f"🔒 Contract frozen: {cf}")
        return 0

    elif args.command == "dispatch":
        task, wt = orchestrator.dispatch_task(args.task_id)
        print(f"🚀 Task {task.id} dispatched to worktree: {wt}")
        return 0

    elif args.command == "qa":
        audit = orchestrator.run_qa_gate(args.task_id)
        status_icon = "✅" if audit.verdict == "PASS" else "❌"
        print(f"{status_icon} QA Verdict: {audit.verdict} (Exit code: {audit.exit_code})")
        if audit.findings:
            print("Findings:")
            for f in audit.findings:
                print(f"  - {f}")
        return 0 if audit.verdict == "PASS" else 1

    elif args.command == "merge":
        orchestrator.merge_to_main(args.task_id)
        print(f"🎉 Merged task {args.task_id} to main and pruned worktree.")
        return 0

    elif args.command == "run-auto":
        print(f"🤖 Starting autonomous self-healing execution loop for {args.task_id} (Max retries: {args.retries})...")

        def default_worker_noop(task_obj, worktree_path, coaching_guidance):
            if coaching_guidance:
                print(f"  🧑‍🏫 [Trainer Coaching Received]: {coaching_guidance.splitlines()[0]}")

        success, msg = orchestrator.auto_execute_lifecycle(
            task_id=args.task_id,
            worker_fn=default_worker_noop,
            max_retries=args.retries,
        )
        if success:
            print(f"✅ {msg}")
            return 0
        else:
            print(f"⚠️ {msg}")
            return 1

    elif args.command == "antigravity-manifest":
        import json
        from core.antigravity_bridge import AntigravityBridge

        bridge = AntigravityBridge()
        manifest = bridge.export_ide_manifest()
        if args.json:
            print(json.dumps(manifest, indent=2))
        else:
            print("🚀 Antigravity Multi-Agent & Skill Clustering Manifest")
            print(f"Skills Root: {manifest['skills_root']}")
            print("-" * 65)
            for role_name, config in manifest["subagents"].items():
                print(f"[{role_name}] - {config['role_title']}")
                print(f"  Model: {config['model']} | Compaction: {config['compaction_threshold']} tokens")
                print(f"  Skills ({len(config['specialized_skills'])}): {', '.join(config['specialized_skills'])}")
                print(f"  Tools: {', '.join(config['enabled_tools'])}")
                print()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
