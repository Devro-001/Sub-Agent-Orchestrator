# Contributing to Sub-Agent Orchestrator

Thank you for contributing to the Sub-Agent Orchestrator project. This repository enforces strict architectural boundaries, deterministic quality gates, and contract-driven multi-agent workflows.

---

## Core Engineering Principles

1. **Ponytail Principle (Minimalist & Dependency-Light)**  
   Favor standard library solutions and native platform primitives before introducing external dependencies. Avoid premature abstractions and boilerplate.

2. **Contract Freeze Before Implementation**  
   Interface definitions, API payloads, and database schemas must be frozen in `contracts/` prior to writing implementation code. Subsystems operate against immutable specifications.

3. **Strict Filesystem Isolation**  
   Work is partitioned into isolated Git worktrees (`.worktrees/`). Agents and contributors may only modify files within their assigned boundary scope.

4. **Deterministic QA Veto Gate**  
   No code is merged into `main` without passing automated verification, file boundary checks, and UI/UX accessibility audits.

---

## Architectural Role Boundaries

Filesystem write permissions are defined in `contracts/role_contracts.json`. Contributions must respect these demarcations:

| Role | Permitted Write Paths | Prohibited Write Paths |
| :--- | :--- | :--- |
| **Manager** (`orchestrator-manager`) | `specs/**`, `.specify/**`, `plans/**`, `contracts/**`, `tasks.md` | `server/**`, `client/**`, `src/**` |
| **Backend** (`backend-engineer`) | `server/**`, `backend/**`, `api/**`, `database/**`, `lib/core/**`, `tests/backend/**` | `client/**`, `frontend/**`, `styles/**`, `contracts/**` |
| **Frontend** (`frontend-engineer`) | `client/**`, `frontend/**`, `src/components/**`, `styles/**`, `public/**`, `tests/frontend/**` | `server/**`, `backend/**`, `api/**`, `database/**`, `contracts/**` |
| **QA Auditor** (`qa-security-auditor`) | `tests/**`, `e2e/**`, `security/**`, `audit-report.md` | `server/**`, `client/**`, `src/**` |
| **Researcher** (`data-researcher`) | `research/**` | `server/**`, `client/**`, `tests/**`, `src/**` |
| **Trainer** (`trainer-continuous-learning`) | `coaching/**` | `server/**`, `client/**`, `src/**`, `tests/**` |

---

## Development Workflow

### 1. Environment Setup

```bash
git clone https://github.com/<username>/sub-agent-orchestrator.git
cd sub-agent-orchestrator

python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 2. Branching & Worktree Discipline

Do not perform direct multi-role modifications on a single branch. For feature development:

- Create isolated branches under the `worker/<role-slug>/<task-id>` namespace.
- Use `git worktree` to isolate concurrent work environments:
  ```bash
  git worktree add -b worker/backend/T-NEW .worktrees/backend-T-NEW HEAD
  ```
- Keep changes strictly within your assigned role boundary.

### 3. Contract Freezing

If a feature introduces or modifies inter-agent boundaries or API schemas:
1. Update or create the schema file under `contracts/`.
2. Commit the contract independently:
   ```bash
   sub-agent-orchestrator freeze-contract schema.json '{"endpoint": "/v1/resource"}'
   ```
3. Once frozen, dependent agents and workers implement against that contract without altering it.

### 4. Running the Test Suite

All contributions must pass the complete test suite:

```bash
python3 -m unittest discover -s tests -v
```

Before submitting a pull request, verify:
- All 17+ tests pass without errors or warnings.
- SQLite WAL ledger migrations run cleanly.
- No orphan files remain in `.worktrees/`.
- Markdown files do not exceed the 45 KB hard guardrail.

---

## QA Gate Standards

Every submission is evaluated against three verification dimensions:

1. **Boundary Conformance**: No files modified outside permitted paths.
2. **Functional Integrity**: Full test suite pass (`exit_code == 0`).
3. **Frontend Craft & A11y (when applicable)**:
   - WCAG AA accessibility compliance (all `<img>` tags require `alt` attributes, buttons require accessible labels).
   - Anti-Slop verification: No generic copy, clichéd marketing filler, or generic neon gradient backgrounds.

---

## Submitting Pull Requests

1. Fork the repository and create a feature branch from `main`.
2. Ensure your commit messages follow Conventional Commits (e.g., `feat(core): add worktree cleanup hook`, `fix(task-engine): prevent race condition in atomic claim`).
3. Open a Pull Request detailing the purpose, affected contracts, and test evidence.
4. Maintainers will run the automated QA verification gate before merging.
