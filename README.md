# Sub-Agent Orchestrator

A deterministic multi-agent execution engine for software engineering workflows. Coordinates six specialized sub-agents through isolated Git worktrees, immutable contract freezes, an atomic SQLite WAL task ledger, and an autonomous self-healing revision loop.

---

## Architectural Guarantees

Traditional multi-agent frameworks often suffer from race conditions in shared directories, contract drift between frontend and backend models, and brittle review steps that demand constant human triage. 

Sub-Agent Orchestrator eliminates these failure modes using four core mechanisms:

1. **Filesystem Isolation via Git Worktrees**  
   Every task executes within an independent Git worktree (`.worktrees/<role>-<task-id>`) checked out to a dedicated branch (`worker/<role>/<task-id>`). Concurrent agents cannot overwrite each other's files.
2. **Immutable Contract Freeze**  
   Type definitions, API payloads, and database schemas are finalized and committed to `contracts/` before workers begin development. Workers consume contracts; they cannot alter them.
3. **Atomic Task Ledger (SQLite WAL)**  
   Task states, role allocations, dependencies, and audit outcomes are persisted in SQLite with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`). Operations are ACID-compliant and support concurrent multi-process access.
4. **Autonomous Self-Healing Loop**  
   When a task fails QA verification, the Trainer agent analyzes the failure output, records root causes and preventive rules, issues structured coaching guidance, and redispatches the task to the worker without human bottlenecking.

---

## The 6 Sub-Agents

Each sub-agent operates within strict filesystem boundaries defined in [`contracts/role_contracts.json`](contracts/role_contracts.json):

```
                                  ┌────────────────────────┐
                                  │  Orchestrator Manager  │
                                  │   (Task Decomposition) │
                                  └───────────┬────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         ┌─────────────────────────┐                     ┌─────────────────────────┐
         │     Backend Engineer    │                     │    Frontend Engineer    │
         │  (Core API / Database)  │                     │  (UI / UX / A11y Craft) │
         └────────────┬────────────┘                     └────────────┬────────────┘
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              ▼
                                 ┌─────────────────────────┐
                                 │   QA & Security Auditor │
                                 │   (Absolute Veto Gate)  │
                                 └────────────┬────────────┘
                                              │ (On Rejection)
                                              ▼
                                 ┌─────────────────────────┐
                                 │     Trainer Agent       │
                                 │ (Self-Healing / KB Sync)│
                                 └─────────────────────────┘
                                              ▲
                                              │
                                 ┌────────────┴────────────┐
                                 │     Data Researcher     │
                                 │ (Multi-Source Context)  │
                                 └─────────────────────────┘
```

### 1. Orchestrator Manager (`orchestrator-manager`)
- **Mission**: Ingests high-level project goals, breaks them down into an atomic Directed Acyclic Graph (DAG) of tasks, freezes API contracts, and merges approved branches into `main`.
- **Permitted Paths**: `specs/**`, `.specify/**`, `plans/**`, `contracts/**`, `tasks.md`.
- **Forbidden Paths**: Application source code (`server/**`, `client/**`, `src/**`).

### 2. Backend Specialist (`backend-engineer`)
- **Mission**: Implements business logic, API routes, database schemas, and unit tests adhering strictly to the Ponytail principle (standard library and native platform features first).
- **Permitted Paths**: `server/**`, `backend/**`, `api/**`, `database/**`, `lib/core/**`, `tests/backend/**`.
- **Forbidden Paths**: Client assets, frontend components, styles, contracts.

### 3. Frontend Specialist (`frontend-engineer`)
- **Mission**: Constructs responsive web components and application views adhering to WCAG AA accessibility standards and high-craft UI design. Eliminates generic AI templates, placeholder copy, and clichéd styling.
- **Permitted Paths**: `client/**`, `frontend/**`, `src/components/**`, `styles/**`, `public/**`, `tests/frontend/**`.
- **Forbidden Paths**: Backend services, database schemas, contracts.

### 4. QA & Security Auditor (`qa-security-auditor`)
- **Mission**: Holds absolute veto power over branch merges. Validates strict file boundary compliance, executes test suites, inspects accessibility (`alt` attributes, keyboard accessibility, accessible labels), and verifies absence of generic AI copy.
- **Permitted Paths**: `tests/**`, `e2e/**`, `security/**`, `audit-report.md`.
- **Forbidden Paths**: Application source directories (`server/**`, `client/**`, `src/**`).

### 5. Data Researcher (`data-researcher`)
- **Mission**: Performs multi-source information gathering, validates technical references, and produces structured research documentation adhering to the 45 KB atomic note size guardrail.
- **Permitted Paths**: `research/**`.
- **Forbidden Paths**: Production application and test code.

### 6. Trainer & Reflexion Agent (`trainer-continuous-learning`)
- **Mission**: Investigates audit failures, extracts root causes, formulates corrective guidance for workers, and synchronizes incident entries into persistent troubleshooting knowledge bases.
- **Permitted Paths**: `coaching/**`.
- **Forbidden Paths**: Direct modifications to production code or test files.

---

## Prerequisites

- **Python**: Version 3.10 or higher.
- **Git**: Version 2.30 or higher (available on system `$PATH`).
- **Operating System**: Linux (tested on Ubuntu 22.04/24.04 and Linux Mint) or macOS.
- **Zero External Dependencies**: The core engine uses exclusively Python's standard library (`sqlite3`, `subprocess`, `dataclasses`, `argparse`, `pathlib`).

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/hans3-code/Sub-Agent-Orchestrator.git
cd Sub-Agent-Orchestrator
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Package in Editable Mode

```bash
pip install -e .
```

Verify installation:

```bash
sub-agent-orchestrator --help
```

---

## Configuration

Sub-Agent Orchestrator supports two operational modes:

### Mode A: Standalone Mode (Default, Zero External Setup)

Out of the box, the orchestrator requires no external services or third-party accounts. Task state is stored locally in `.specify/memory/task_ledger.db` and research notes are kept within the project root.

```bash
# Run with explicit standalone flag or let it detect default environment
sub-agent-orchestrator --standalone init --id proj-01 --name "My Service"
```

### Mode B: Obsidian Second Brain Integration (Optional)

To synchronize research findings, user profiles, and troubleshooting logs directly into an Obsidian Second Brain vault, configure the vault path via environment variable or `.env`:

**Option 1: Environment Variable**
```bash
export SECOND_BRAIN_PATH="/path/to/your/SecondBrain"
```

**Option 2: `.env` File**
Create a `.env` file in the project root:
```env
SECOND_BRAIN_PATH=~/Documents/SecondBrain
```

**Synchronized Assets:**
- User Profile: `$SECOND_BRAIN_PATH/01_PROFILE/User_Profile.md`
- AI Guidelines: `$SECOND_BRAIN_PATH/02_RULES_GUIDELINES/Base_Agent_AI_Guidelines.md`
- Troubleshooting Log: `$SECOND_BRAIN_PATH/05_PROJECTS/Project_Changelog_and_Troubleshooting_Log.md`
- Research Notes: `$SECOND_BRAIN_PATH/06_DATA_SEARCH/<topic>/` (enforces `<= 45 KB` file limit)

---

## CLI Usage Guide

The CLI entrypoint is `sub-agent-orchestrator` (or directly via `./bin/sub-agent-orchestrator`).

### 1. Initialize a Project

Registers a project in the SQLite WAL ledger:

```bash
sub-agent-orchestrator init --id api-service --name "Core API Service" --desc "Authentication and Billing API"
```

Output:
```
✅ Initialized project 'Core API Service' (api-service) at /path/to/repo
```

### 2. Freeze an API Contract

Freezes an immutable interface before worker agents write code:

```bash
sub-agent-orchestrator freeze-contract auth_v1.json '{
  "endpoints": {
    "/login": {"method": "POST", "body": {"user": "str", "pass": "str"}}
  }
}'
```

Output:
```
🔒 Contract frozen: /path/to/repo/contracts/auth_v1.json
```

### 3. Inspect Tasks

Displays all registered tasks, their assigned roles, and current statuses:

```bash
sub-agent-orchestrator tasks
```

Output:
```
ID           ROLE                      STATUS          TITLE
---------------------------------------------------------------------------
T-BE-01      backend-engineer          IDLE            Build Auth Endpoints
T-FE-01      frontend-engineer         IDLE            Build Login UI Form
```

### 4. Dispatch a Task to an Isolated Worktree

Creates a dedicated Git worktree branch and locks the task:

```bash
sub-agent-orchestrator dispatch T-BE-01
```

Output:
```
🚀 Task T-BE-01 dispatched to worktree: /path/to/repo/.worktrees/backend-T-BE-01
```

### 5. Run the QA Gate

Audits worktree changes against permitted boundaries, tests, and UI/UX rules:

```bash
sub-agent-orchestrator qa T-BE-01
```

Output:
```
✅ QA Verdict: PASS (Exit code: 0)
```

If boundaries or tests fail:
```
❌ QA Verdict: FAIL (Exit code: 1)
Findings:
  - Unauthorized modified file: frontend/component.jsx
```

### 6. Merge an Approved Task

Merges the task branch into `main` and tears down the temporary worktree:

```bash
sub-agent-orchestrator merge T-BE-01
```

Output:
```
🎉 Merged task T-BE-01 to main and pruned worktree.
```

### 7. Run Autonomous Self-Healing Revision Loop

Executes a task end-to-end. If QA rejects an attempt, the Trainer diagnoses the issue and automatically coaches the worker through revisions up to `--retries` attempts:

```bash
sub-agent-orchestrator run-auto T-AUTO-01 --retries 3
```

Output:
```
🤖 Starting autonomous self-healing execution loop for T-AUTO-01 (Max retries: 3)...
  🧑‍🏫 [Trainer Coaching Received]: Trainer Coaching (Attempt 1/3): Fix issues: File boundary violation
✅ Task T-AUTO-01 PASSED QA and was MERGED to main.
```

---

## Programmatic Python SDK

You can embed Sub-Agent Orchestrator directly within Python applications and automation scripts.

### Full Multi-Agent Lifecycle Example

```python
from pathlib import Path
from contracts.types import AgentRole, Task, TaskStatus
from core.orchestrator import Orchestrator
from agents.manager_agent import ManagerAgent
from agents.backend_agent import BackendAgent
from agents.qa_agent import QAAgent
from agents.trainer_agent import TrainerAgent

# 1. Initialize Orchestrator (Standalone or Second Brain)
orchestrator = Orchestrator(project_root=".")
manager = ManagerAgent(orchestrator)
backend = BackendAgent(orchestrator)
qa = QAAgent(orchestrator)
trainer = TrainerAgent(orchestrator)

# 2. Register Project
orchestrator.init_project(
    project_id="app-billing",
    name="Billing System",
    description="Recurring subscription billing microservice"
)

# 3. Freeze API Contract
orchestrator.freeze_contract(
    filename="billing_api.json",
    contract_content='{"version": "1.0.0", "endpoints": ["/v1/invoices"]}'
)

# 4. Decompose Tasks via Manager
tasks = manager.decompose_project(
    project_id="app-billing",
    plan_spec={
        "tasks": [
            {
                "id": "T-BILL-01",
                "title": "Implement Invoice Generation Service",
                "assigned_role": AgentRole.BACKEND.value,
                "file_boundaries": ["backend/**", "api/**"],
                "dependencies": []
            }
        ]
    }
)

# 5. Dispatch Task to Isolated Git Worktree
task, worktree_path = orchestrator.dispatch_task("T-BILL-01")
print(f"Agent working in: {worktree_path}")

# 6. Worker creates backend code inside worktree
service_file = Path(worktree_path) / "backend" / "invoice.py"
service_file.parent.mkdir(parents=True, exist_ok=True)
service_file.write_text("def generate_invoice(user_id): return {'id': 1}", encoding="utf-8")

# 7. QA Gate Audit
audit = qa.audit_task("T-BILL-01")

if audit.verdict == "PASS":
    # 8. Merge to main and prune worktree
    orchestrator.merge_to_main("T-BILL-01")
    print("Merged successfully to main.")
else:
    # 9. Trainer Intervention on failure
    trainer.handle_incident(
        task_id="T-BILL-01",
        symptom=audit.test_output,
        root_cause="Boundary or assertion failure",
        resolution="Coaching dispatched",
        preventive_rule="Check boundaries before submitting"
    )
```

### Autonomous Self-Healing Revision Example

```python
from core.orchestrator import Orchestrator
from pathlib import Path

orchestrator = Orchestrator(project_root=".")

def custom_worker(task, worktree_path, coaching):
    wt = Path(worktree_path)
    if coaching:
        print(f"Applying coaching instruction: {coaching}")
    
    # Write implementation
    target = wt / "backend" / "service.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("def process(): return True\n", encoding="utf-8")

# Automatically loop worker -> QA -> Trainer -> merge
success, message = orchestrator.auto_execute_lifecycle(
    task_id="T-TASK-02",
    worker_fn=custom_worker,
    max_retries=3
)
print(message)
```

---

## Running the Test Suite

The test suite covers integration lifecycles, worktree creation/cleanup, role boundary enforcement, SQLite concurrency, UI/UX anti-slop audits, and standalone fallbacks.

Run the entire suite using Python's standard test runner:

```bash
python3 -m unittest discover -s tests -v
```

Expected output:

```
test_autonomous_auto_revision_loop (test_orchestrator_flow.TestOrchestratorFlow) ... ok
test_full_multiagent_lifecycle (test_orchestrator_flow.TestOrchestratorFlow) ... ok
test_qa_approves_crafted_ui (test_qa_uiux_audit.TestQAUIUXAudit) ... ok
test_qa_rejects_slop_ui (test_qa_uiux_audit.TestQAUIUXAudit) ... ok
test_agent_classes_match_role_constants (test_role_contracts.TestRoleContracts) ... ok
test_backend_and_frontend_boundaries_disjoint (test_role_contracts.TestRoleContracts) ... ok
test_qa_veto_and_read_only_production (test_role_contracts.TestRoleContracts) ... ok
test_role_contracts_json_schema_and_roles (test_role_contracts.TestRoleContracts) ... ok
test_context_ingestion (test_second_brain_bridge.TestSecondBrainBridge) ... ok
test_save_research_note_size_guardrail (test_second_brain_bridge.TestSecondBrainBridge) ... ok
test_standalone_mode_fallback (test_second_brain_bridge.TestSecondBrainBridge) ... ok
test_sync_troubleshooting_case (test_second_brain_bridge.TestSecondBrainBridge) ... ok
test_add_and_get_task (test_task_engine.TestTaskEngine) ... ok
test_atomic_claim_with_dependencies (test_task_engine.TestTaskEngine) ... ok
test_audit_pass_and_fail (test_task_engine.TestTaskEngine) ... ok
test_create_and_remove_worktree (test_worktree_manager.TestWorktreeManager) ... ok
test_file_boundaries_validation (test_worktree_manager.TestWorktreeManager) ... ok

----------------------------------------------------------------------
Ran 17 tests in 2.878s

OK
```

---

## Repository Structure

```
sub-agent-orchestrator/
├── agents/                      # 6 Sub-Agent Implementations
│   ├── manager_agent.py         # Agent 1: Decomposer & Coordinator
│   ├── backend_agent.py         # Agent 2: Backend & Database Specialist
│   ├── frontend_agent.py        # Agent 3: UI/UX & A11y Specialist
│   ├── qa_agent.py              # Agent 4: Security, QA & Anti-Slop Auditor
│   ├── researcher_agent.py      # Agent 5: Multi-Source Intelligence
│   └── trainer_agent.py         # Agent 6: Incident Remediation & KB Sync
├── bin/
│   └── sub-agent-orchestrator   # CLI wrapper script
├── contracts/
│   ├── role_contracts.json      # File boundaries & permission schema
│   └── types.py                 # Core dataclasses and Enum definitions
├── core/
│   ├── cli.py                   # Argument parser & CLI dispatch logic
│   ├── orchestrator.py          # Master coordinator & auto-execution loop
│   ├── second_brain_bridge.py   # Obsidian Second Brain bridge
│   ├── task_engine.py           # SQLite WAL atomic task ledger
│   └── worktree_manager.py      # Git worktree filesystem isolation
├── tests/                       # Complete verification test suite
├── pyproject.toml               # Python packaging configuration
├── CONTRIBUTING.md              # Boundary & contract contribution guide
├── LICENSE                      # MIT License
└── README.md                    # Project documentation
```

---

## Contributing

Review [`CONTRIBUTING.md`](CONTRIBUTING.md) for branch namespace rules, contract freezing guidelines, and QA gate standards.

## License

This project is licensed under the [MIT License](LICENSE).
