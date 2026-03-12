# Evennia LLMNPC Implementation Plan

## TL;DR

> **Quick Summary**: Add a non-blocking LLM-powered NPC typeclass for Evennia that listens to speech selectively, calls an OpenAI-compatible API off the reactor thread, and responds in-room with robust fallback and test coverage.
>
> **Deliverables**:
> - `requirements.txt` dependency updates for `python-dotenv` and `openai`
> - `server/conf/settings.py` safe `.env` + LLM config wiring
> - `typeclasses/llm_npc.py` with trigger filtering, single-flight lock, and async-safe API call flow
> - `typeclasses/tests.py` mock-based Evennia tests for trigger, lock, fallback, and success behavior
> - In-game creation/binding command sequence for spawning NPC
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves + final verification wave
> **Critical Path**: Task 1 -> Task 4 -> Task 7 -> Task 10 -> Task 11 -> Task 12/F1-F4

---

## Context

### Original Request
Implement an LLM-driven NPC in an Evennia game project (Railway + PostgreSQL), with strict non-blocking behavior, environment-driven configuration, selective trigger logic, error fallback, and unit tests using EvenniaTest + mock.

### Interview Summary
**Key Discussions**:
- Non-blocking API invocation is mandatory in Twisted/Evennia runtime.
- `.env` must be supported locally while Railway production uses injected env vars.
- NPC should only react when explicitly addressed to reduce token cost.
- Include anti-concurrency guard and in-character fallback line on failure.
- Deliverables are constrained to specific files and a creation command sequence.

**Research Findings**:
- Project has minimal dependencies and no existing test files.
- `typeclasses/objects.py` documents relevant hooks (`at_msg_receive`, `at_say`) and confirms clean extension points.
- Official Evennia listening tutorial recommends `msg` capture + `at_heard_say` style flow for speech reactions.
- Twisted guidance confirms blocking network I/O must be offloaded from reactor thread.

### Metis Review
**Identified Gaps (addressed in this plan)**:
- Clarify hook strategy and avoid vague “some speech hook” implementation.
- Lock down anti-loop and anti-spam behavior explicitly.
- Define deterministic fallback behavior and logging requirements.
- Add concrete acceptance criteria for non-blocking and lock behavior.
- Prevent scope creep into long-term memory, vector DB, or admin UI.

---

## Work Objectives

### Core Objective
Deliver a production-safe LLM NPC baseline for Evennia that is reactive, non-blocking, cost-aware, and testable under Railway/local environments.

### Concrete Deliverables
- `requirements.txt` includes `.env` loader and chosen LLM HTTP integration dependency.
- `server/conf/settings.py` exposes canonical LLM config variables with safe defaults.
- `typeclasses/llm_npc.py` implements LLMNPC behavior and async offload wrapper.
- `typeclasses/tests.py` contains mock-based tests using Evennia test primitives.
- A command snippet is documented to create and place NPC in-game.

### Definition of Done
- [x] `evennia test typeclasses.tests` passes for all new test cases.
- [x] NPC does not block player interaction while waiting on remote LLM call.
- [x] NPC only responds to explicit address patterns (configured in logic).
- [x] API failures produce stable fallback response and error logs.
- [x] Required env vars are loaded from `.env` locally and env vars in Railway.

### Must Have
- Twisted-safe, non-blocking external API call path.
- Trigger filtering + anti-concurrency single-flight guard.
- Mocked tests for success and failure code paths.

### Must NOT Have (Guardrails)
- No vector DB / long-term memory system.
- No streaming token UI or admin dashboards.
- No plaintext API key in repository.
- No blocking HTTP call in reactor thread.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — All verification steps are command/tool executable.

### Test Decision
- **Infrastructure exists**: NO local test suite currently present
- **Automated tests**: YES (TDD workflow)
- **Framework**: Evennia test runner (`evennia test`), unittest/mock style via Evennia test resources
- **If TDD**: Each implementation task includes RED -> GREEN -> REFACTOR checks

### QA Policy
Evidence is saved under `.sisyphus/evidence/task-{N}-{scenario}.{ext}`.

- **Code/unit**: Run `evennia test typeclasses.tests` with explicit case labels when possible.
- **Async safety**: Verify callback-based response flow and absence of synchronous wait in hooks.
- **Config**: Validate env fallback behavior using isolated env/mocked settings.
- **In-game behavior**: Use command-level simulation where test utilities allow object speech interactions.

---

## Execution Strategy

### Parallel Execution Waves

Wave 1 (Start Immediately — foundations)
├── Task 1: Freeze architecture defaults and acceptance contract [quick]
├── Task 2: Prepare dependency and config loading plan [quick]
├── Task 3: Define trigger/filter and lock policy matrix [deep]
├── Task 4: Define LLM gateway interface + error taxonomy [deep]
└── Task 5: Define deterministic test harness strategy [unspecified-high]

Wave 2 (After Wave 1 — implementation modules, max parallel)
├── Task 6: Update `requirements.txt` with required packages [quick] (depends: 2)
├── Task 7: Update `server/conf/settings.py` for `.env` + LLM vars [unspecified-high] (depends: 2, 4)
├── Task 8: Create `typeclasses/llm_npc.py` skeleton and state fields [quick] (depends: 1, 3)
├── Task 9: Implement non-blocking LLM call wrapper and callbacks [deep] (depends: 4, 8)
└── Task 10: Implement speech trigger + lock + fallback behavior [deep] (depends: 3, 8, 9)

Wave 3 (After Wave 2 — tests + validation)
├── Task 11: Implement `typeclasses/tests.py` mocked unit tests [unspecified-high] (depends: 5, 7, 10)
├── Task 12: Add command snippet + usage validation notes [writing] (depends: 10)
└── Task 13: Stabilize edge cases from failing tests [deep] (depends: 11)

Wave 4 (After Wave 3 — integration quality)
├── Task 14: Full test run and artifact capture [unspecified-high] (depends: 11, 13)
├── Task 15: Non-blocking behavior verification scenarios [deep] (depends: 10, 14)
└── Task 16: Scope compliance and security review [oracle] (depends: 7, 10, 14)

Wave FINAL (After ALL tasks — independent review, 4 parallel)
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real scenario QA replay (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: 1 -> 4 -> 7 -> 10 -> 11 -> 14 -> F1/F4
Parallel Speedup: ~60%
Max Concurrent: 5 (Wave 2)

### Dependency Matrix (Full)
- **1**: Blocked By: None | Blocks: 8
- **2**: Blocked By: None | Blocks: 6, 7
- **3**: Blocked By: None | Blocks: 8, 10
- **4**: Blocked By: None | Blocks: 7, 9
- **5**: Blocked By: None | Blocks: 11
- **6**: Blocked By: 2 | Blocks: 14
- **7**: Blocked By: 2, 4 | Blocks: 11, 16
- **8**: Blocked By: 1, 3 | Blocks: 9, 10
- **9**: Blocked By: 4, 8 | Blocks: 10
- **10**: Blocked By: 3, 8, 9 | Blocks: 11, 12, 15, 16
- **11**: Blocked By: 5, 7, 10 | Blocks: 13, 14
- **12**: Blocked By: 10 | Blocks: F1
- **13**: Blocked By: 11 | Blocks: 14
- **14**: Blocked By: 11, 13 | Blocks: 15, 16, F2, F3
- **15**: Blocked By: 10, 14 | Blocks: F3
- **16**: Blocked By: 7, 10, 14 | Blocks: F1, F4
- **F1**: Blocked By: 12, 16 | Blocks: completion gate
- **F2**: Blocked By: 14 | Blocks: completion gate
- **F3**: Blocked By: 14, 15 | Blocks: completion gate
- **F4**: Blocked By: 16 | Blocks: completion gate

### Agent Dispatch Summary
- **Wave 1 (5 tasks)**: T1 quick, T2 quick, T3 deep, T4 deep, T5 unspecified-high
- **Wave 2 (5 tasks)**: T6 quick, T7 unspecified-high, T8 quick, T9 deep, T10 deep
- **Wave 3 (3 tasks)**: T11 unspecified-high, T12 writing, T13 deep
- **Wave 4 (3 tasks)**: T14 unspecified-high, T15 deep, T16 oracle
- **Final (4 tasks)**: F1 oracle, F2 unspecified-high, F3 unspecified-high, F4 deep

---

## TODOs

- [x] 1. Freeze architecture defaults and acceptance contract

  **What to do**:
  - Confirm final hook model for execution: capture speech events via NPC message pipeline and route to a dedicated `at_heard_say`-style handler in `typeclasses/llm_npc.py`.
  - Record concrete behavior contract: explicit-address trigger, single-flight lock policy, fallback text policy, and no-react-to-self rule.
  - Define exact env var names and defaulting/error behavior to avoid implementation ambiguity.

  **Must NOT do**:
  - Do not add memory/vector-store scope.
  - Do not introduce additional command systems beyond requested spawn snippet.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Specification hardening and contract writing in one file.
  - **Skills**: `superpowers/writing-plans`
    - `superpowers/writing-plans`: Keeps task acceptance concrete and executable.
  - **Skills Evaluated but Omitted**:
    - `superpowers/test-driven-development`: Applied in later implementation tasks directly.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-5)
  - **Blocks**: 8
  - **Blocked By**: None

  **References**:
  - `typeclasses/objects.py:192` - Documents `at_msg_receive` hook availability.
  - `typeclasses/objects.py:210` - Documents `at_say` hook semantics and speech lifecycle.
  - `server/conf/settings.py:46` - Current env-based config style to follow.
  - `https://www.evennia.com/docs/latest/Howtos/Tutorial-NPC-Listening.html` - Official speech-listening pattern.

  **Acceptance Criteria**:
- [x] Contract for trigger, lock, fallback, and env behavior is explicitly written in task notes and reflected in downstream tasks.
- [x] No unresolved behavior ambiguity remains for Tasks 8-11.

  **QA Scenarios**:
  ```
  Scenario: Contract completeness check
    Tool: Bash
    Preconditions: Plan file updated with task details
    Steps:
      1. Read `.sisyphus/plans/llm-npc-evennia.md`
      2. Verify sections include trigger rules, lock policy, fallback behavior, env keys
      3. Confirm all four items are referenced by later tasks
    Expected Result: All required contract fields present and linked downstream
    Failure Indicators: Any one of trigger/lock/fallback/env missing or vague
    Evidence: .sisyphus/evidence/task-1-contract-check.txt

  Scenario: Scope guard check
    Tool: Bash
    Preconditions: Task 1 complete
    Steps:
      1. Search plan text for "vector", "memory store", "admin panel"
      2. Confirm these appear only in exclusion/guardrail context
    Expected Result: No scope creep in implementation tasks
    Evidence: .sisyphus/evidence/task-1-scope-guard.txt
  ```

  **Commit**: NO

- [x] 2. Prepare dependency and config loading plan

  **What to do**:
  - Lock minimal dependency additions (`python-dotenv` + `openai`).
  - Define settings loading order: local `.env` optional, Railway env authoritative.
  - Specify explicit fallback when required keys are missing.

  **Must NOT do**:
  - Do not hardcode API keys or provider URLs.
  - Do not alter unrelated network settings in `settings.py`.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Narrow dependency/config decision work.
  - **Skills**: `superpowers/writing-plans`
    - `superpowers/writing-plans`: Forces explicit file-level steps and verification.
  - **Skills Evaluated but Omitted**:
    - `superpowers/systematic-debugging`: Not a bug investigation task.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 6, 7
  - **Blocked By**: None

  **References**:
  - `requirements.txt:1` - Existing dependency baseline.
  - `server/conf/settings.py:48` - Current env pattern already used for DB config.
  - `https://pypi.org/project/python-dotenv/` - `.env` loading behavior and defaults.

  **Acceptance Criteria**:
- [x] Dependency list and rationale are fixed before edits.
- [x] Settings load-order contract is explicitly defined.

  **QA Scenarios**:
  ```
  Scenario: Dependency decision validation
    Tool: Bash
    Preconditions: Task notes updated
    Steps:
      1. Verify chosen dependency set contains no redundant HTTP clients
      2. Verify each added package maps to a concrete use in tasks 7-10
    Expected Result: One clear client strategy and no duplicate stack
    Evidence: .sisyphus/evidence/task-2-deps-decision.txt

  Scenario: Missing-key policy review
    Tool: Bash
    Preconditions: Task notes updated
    Steps:
      1. Confirm policy for absent `LLM_API_KEY` is documented (fallback + log)
      2. Confirm no startup hard-crash requirement is introduced
    Expected Result: Runtime-safe behavior documented for missing config
    Evidence: .sisyphus/evidence/task-2-missing-key-policy.txt
  ```

  **Commit**: NO

- [x] 3. Define trigger/filter and lock policy matrix

  **What to do**:
  - Define explicit address rules (case-insensitive NPC name mention + say-type filter).
  - Define message exclusions (system messages, NPC self-output, unrelated room speech).
  - Define single-flight behavior while thinking (ignore/brief busy reply policy).

  **Must NOT do**:
  - Do not use broad “any room text triggers LLM” behavior.
  - Do not allow recursive self-trigger loops.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Correctness-sensitive logic with cost and stability implications.
  - **Skills**: `superpowers/brainstorming`
    - `superpowers/brainstorming`: Useful for evaluating trigger policy trade-offs.
  - **Skills Evaluated but Omitted**:
    - `superpowers/test-driven-development`: Implemented in later coding tasks.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 8, 10
  - **Blocked By**: None

  **References**:
  - `typeclasses/objects.py:192` - Incoming message interception point.
  - `typeclasses/objects.py:210` - Speech hook semantics.
  - `https://www.evennia.com/docs/latest/Howtos/Tutorial-NPC-Listening.html` - Canonical say-detection pattern.

  **Acceptance Criteria**:
- [x] Trigger matrix includes positive and negative examples.
- [x] Lock behavior for concurrent inputs is deterministic and testable.

  **QA Scenarios**:
  ```
  Scenario: Trigger matrix verification
    Tool: Bash
    Preconditions: Trigger matrix written in plan/task notes
    Steps:
      1. Verify at least 3 positive examples (name mention variants)
      2. Verify at least 3 negative examples (non-addressed, system text, self text)
    Expected Result: Matrix supports deterministic implementation/testing
    Evidence: .sisyphus/evidence/task-3-trigger-matrix.txt

  Scenario: Lock policy conflict check
    Tool: Bash
    Preconditions: Lock policy documented
    Steps:
      1. Verify policy defines behavior for second input during thinking
      2. Verify behavior is reflected in Task 11 test scope
    Expected Result: Lock policy and tests are aligned
    Evidence: .sisyphus/evidence/task-3-lock-policy.txt
  ```

  **Commit**: NO

- [x] 4. Define LLM gateway interface and error taxonomy

  **What to do**:
  - Define internal helper interface for external call (inputs: speaker text/context, outputs: NPC reply text).
  - Define timeout, network error, and invalid-response handling rules.
  - Define callback/errback responsibilities between worker thread and reactor thread.

  **Must NOT do**:
  - Do not mix Evennia object operations inside worker-thread network function.
  - Do not expose raw API exceptions to players.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Threading boundaries and fault handling are critical.
  - **Skills**: `superpowers/writing-plans`
    - `superpowers/writing-plans`: Ensures explicit contract and acceptance checks.
  - **Skills Evaluated but Omitted**:
    - `superpowers/systematic-debugging`: Preventive design stage, not failure triage.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 7, 9
  - **Blocked By**: None

  **References**:
  - `https://docs.twisted.org/en/stable/core/howto/threading.html` - Reactor-thread and worker-thread best practices.
  - `https://docs.twisted.org/en/twisted-21.2.0/api/twisted.internet.threads.html` - `deferToThread` contract.
  - `server/conf/settings.py:94` - Existing websocket/env config pattern for new LLM vars style.

  **Acceptance Criteria**:
- [x] Clear interface is documented for the LLM call helper.
- [x] Error classes map to deterministic fallback text and logs.

  **QA Scenarios**:
  ```
  Scenario: Error taxonomy completeness
    Tool: Bash
    Preconditions: Task contract documented
    Steps:
      1. Verify taxonomy includes timeout, transport, non-200, parse error
      2. Verify each maps to fallback + error log path
    Expected Result: No unclassified runtime error path remains
    Evidence: .sisyphus/evidence/task-4-error-taxonomy.txt

  Scenario: Thread-boundary check
    Tool: Bash
    Preconditions: Threading policy documented
    Steps:
      1. Confirm worker function is network-only and side-effect minimal
      2. Confirm game-world output is callback-side only
    Expected Result: Thread safety boundaries are explicit
    Evidence: .sisyphus/evidence/task-4-thread-boundary.txt
  ```

  **Commit**: NO

- [x] 5. Define deterministic test harness strategy

  **What to do**:
  - Define test base class approach (`EvenniaTest`) and where new tests will live (`typeclasses/tests.py`).
  - Define mocking seam for external LLM call helper.
  - Define assertions for success, non-trigger, lock contention, and fallback error path.

  **Must NOT do**:
  - Do not rely on live network/API in tests.
  - Do not make assertions on unstable timestamp/log text.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Test architecture and fixtures for framework-specific runtime.
  - **Skills**: `superpowers/test-driven-development`
    - `superpowers/test-driven-development`: Forces red-green discipline and reliable seams.
  - **Skills Evaluated but Omitted**:
    - `superpowers/systematic-debugging`: Not debugging existing failing suite.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 11
  - **Blocked By**: None

  **References**:
  - `https://www.evennia.com/docs/latest/Coding/Unit-Testing.html` - Evennia testing guidance.
  - `https://www.evennia.com/docs/latest/api/evennia.utils.test_resources.html` - Evennia test resources.
  - `typeclasses/characters.py:16` - Character type baseline expected for NPC subclassing.

  **Acceptance Criteria**:
- [x] Test seam and mock point are documented and implementation-ready.
- [x] Test case matrix maps 1:1 to required behaviors.

  **QA Scenarios**:
  ```
  Scenario: Test matrix completeness
    Tool: Bash
    Preconditions: Test strategy section drafted
    Steps:
      1. Verify cases include: trigger success, ignore non-addressed, lock contention, API exception fallback
      2. Verify each case has deterministic expected output
    Expected Result: Full behavior matrix covered without external network dependency
    Evidence: .sisyphus/evidence/task-5-test-matrix.txt

  Scenario: Mock seam validity check
    Tool: Bash
    Preconditions: Mock seam documented
    Steps:
      1. Verify seam points to a single helper function in `typeclasses/llm_npc.py`
      2. Verify tests can patch that helper without patching Twisted internals
    Expected Result: Mock strategy is simple and robust
    Evidence: .sisyphus/evidence/task-5-mock-seam.txt
  ```

  **Commit**: NO

- [x] 6. Update `requirements.txt` with required runtime dependencies

  **What to do**:
  - Add `python-dotenv`.
  - Add `openai` as the single OpenAI-compatible client dependency (no duplicate stack).
  - Keep dependency list minimal and aligned with Task 2 decision.

  **Must NOT do**:
  - Do not add multiple overlapping client libraries.
  - Do not remove existing deployment-critical packages.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small, scoped dependency update.
  - **Skills**: `superpowers/test-driven-development`
    - `superpowers/test-driven-development`: Ensures install/usage verification follows change.
  - **Skills Evaluated but Omitted**:
    - `superpowers/brainstorming`: Decision already finalized in Task 2.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 14
  - **Blocked By**: 2

  **References**:
  - `requirements.txt:1` - Current baseline list.
  - `server/conf/settings.py:46` - Existing env-use style to align dependency rationale.

  **Acceptance Criteria**:
- [x] `requirements.txt` contains exactly the selected additional packages.
- [x] Dependency updates do not introduce conflicting clients.

  **QA Scenarios**:
  ```
  Scenario: Dependency install verification
    Tool: Bash
    Preconditions: requirements updated
    Steps:
      1. Run `pip install -r requirements.txt`
      2. Confirm installation succeeds without resolver conflicts
    Expected Result: Exit code 0; no conflict error
    Evidence: .sisyphus/evidence/task-6-pip-install.txt

  Scenario: Duplicate stack guard
    Tool: Bash
    Preconditions: requirements updated
    Steps:
      1. Inspect requirements for overlapping HTTP/LLM SDK pairs
      2. Confirm one canonical integration path remains
    Expected Result: Single chosen runtime stack
    Evidence: .sisyphus/evidence/task-6-stack-guard.txt
  ```

  **Commit**: YES
  - Message: `chore(deps): add llm npc runtime dependencies`
  - Files: `requirements.txt`
  - Pre-commit: `pip install -r requirements.txt`

- [x] 7. Update `server/conf/settings.py` for `.env` and LLM variables

  **What to do**:
  - Add optional local `.env` loading (dotenv) early in settings import flow.
  - Add canonical LLM config variables: `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL_NAME`, `LLM_SYSTEM_PROMPT`.
  - Preserve and avoid regression of existing Railway DB/web/TCP settings.

  **Must NOT do**:
  - Do not hardcode secrets or overwrite Railway-injected values.
  - Do not break existing web/telnet/websocket config currently in file.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: High-risk settings file with existing deployment-specific edits.
  - **Skills**: `superpowers/test-driven-development`, `superpowers/systematic-debugging`
    - `superpowers/test-driven-development`: Validate config behavior via tests/checks.
    - `superpowers/systematic-debugging`: Protect against accidental settings regressions.
  - **Skills Evaluated but Omitted**:
    - `superpowers/using-git-worktrees`: Not required for this scoped change.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 11, 16
  - **Blocked By**: 2, 4

  **References**:
  - `server/conf/settings.py:46` - Existing env import area.
  - `server/conf/settings.py:49` - DB env mapping block to preserve.
  - `server/conf/settings.py:61` - Railway deployment block to preserve.
  - `https://pypi.org/project/python-dotenv/` - Safe load behavior.

  **Acceptance Criteria**:
- [x] Local `.env` values load when present; Railway env overrides remain effective.
- [x] All four LLM variables are exposed via settings.
- [x] Existing deployment behavior remains intact.

  **QA Scenarios**:
  ```
  Scenario: Settings import sanity
    Tool: Bash
    Preconditions: settings updated
    Steps:
      1. Run `python -m py_compile server/conf/settings.py`
      2. Run lightweight settings import check under project env
    Expected Result: No syntax/import errors
    Evidence: .sisyphus/evidence/task-7-settings-compile.txt

  Scenario: Env precedence check
    Tool: Bash
    Preconditions: temporary `.env` file in local test context
    Steps:
      1. Set conflicting process env + `.env` values for one LLM key
      2. Import settings and inspect resolved value
    Expected Result: Process env has priority in production-style run, `.env` fills missing only
    Evidence: .sisyphus/evidence/task-7-env-precedence.txt
  ```

  **Commit**: YES
  - Message: `feat(settings): add llm env config loading`
  - Files: `server/conf/settings.py`
  - Pre-commit: `python -m py_compile server/conf/settings.py`

- [x] 8. Create `typeclasses/llm_npc.py` skeleton and state fields

  **What to do**:
  - Add `LLMNPC` class inheriting from project character base + `DefaultCharacter` chain.
  - Define state fields for lock/cooldown (`is_thinking`, timestamp/counter as needed).
  - Add speech-entry methods and helper stubs (`should_respond`, `build_prompt`, `_call_llm`, `_on_llm_success`, `_on_llm_error`).

  **Must NOT do**:
  - Do not make live API call in constructor/creation hooks.
  - Do not emit room messages from background worker thread.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Structural scaffolding before behavior wiring.
  - **Skills**: `superpowers/test-driven-development`
    - `superpowers/test-driven-development`: Keeps scaffolding aligned with upcoming tests.
  - **Skills Evaluated but Omitted**:
    - `superpowers/frontend-ui-ux`: Not relevant.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 9, 10
  - **Blocked By**: 1, 3

  **References**:
  - `typeclasses/characters.py:16` - Inheritance baseline for characters.
  - `typeclasses/objects.py:192` - Incoming message hook location.
  - `https://www.evennia.com/docs/latest/Howtos/Tutorial-NPC-Listening.html` - NPC listening shape.

  **Acceptance Criteria**:
- [x] `typeclasses/llm_npc.py` exists with class skeleton and helper method stubs.
- [x] Lock and trigger helper interfaces are testable and isolated.

  **QA Scenarios**:
  ```
  Scenario: Typeclass import check
    Tool: Bash
    Preconditions: file created
    Steps:
      1. Run `python -m py_compile typeclasses/llm_npc.py`
      2. Import class from module in a Python check
    Expected Result: No import/syntax errors
    Evidence: .sisyphus/evidence/task-8-typeclass-import.txt

  Scenario: Interface completeness check
    Tool: Bash
    Preconditions: class scaffold complete
    Steps:
      1. Verify required helper methods exist
      2. Verify lock state field initialization exists
    Expected Result: Scaffold covers all downstream behavior points
    Evidence: .sisyphus/evidence/task-8-interface-check.txt
  ```

  **Commit**: YES
  - Message: `feat(npc): scaffold llm npc typeclass`
  - Files: `typeclasses/llm_npc.py`
  - Pre-commit: `python -m py_compile typeclasses/llm_npc.py`

- [x] 9. Implement non-blocking LLM call wrapper and callbacks

  **What to do**:
  - Implement worker function for outbound LLM API call (OpenAI-compatible payload).
  - Offload API call via Twisted-safe async mechanism (`deferToThread` or Evennia wrapper).
  - Implement success callback to format and emit NPC response on reactor thread.
  - Implement error callback to log and emit fallback in-character line.

  **Must NOT do**:
  - Do not run synchronous HTTP directly inside speech hook.
  - Do not swallow errors without logging context.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Concurrency and threading boundary correctness.
  - **Skills**: `superpowers/test-driven-development`, `superpowers/systematic-debugging`
    - `superpowers/test-driven-development`: Red-green for async flow.
    - `superpowers/systematic-debugging`: Prevent callback/thread misuse.
  - **Skills Evaluated but Omitted**:
    - `superpowers/brainstorming`: Design already fixed.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 10
  - **Blocked By**: 4, 8

  **References**:
  - `https://docs.twisted.org/en/twisted-21.2.0/api/twisted.internet.threads.html` - `deferToThread` behavior.
  - `https://docs.twisted.org/en/stable/core/howto/threading.html` - Reactor-thread safety guidelines.
  - `typeclasses/llm_npc.py` - helper skeleton from Task 8.

  **Acceptance Criteria**:
- [x] Speech hook returns immediately after scheduling async call.
- [x] Success path emits room reply and unlocks state.
- [x] Error path logs exception details and emits fallback reply.

  **QA Scenarios**:
  ```
  Scenario: Async scheduling verification
    Tool: Bash
    Preconditions: Task 9 implemented
    Steps:
      1. Mock LLM worker to sleep/block in worker context
      2. Trigger NPC speech hook and measure immediate return in test
    Expected Result: Hook does not block while worker runs
    Evidence: .sisyphus/evidence/task-9-nonblocking.txt

  Scenario: Error callback fallback
    Tool: Bash
    Preconditions: Task 9 implemented
    Steps:
      1. Mock LLM worker to raise timeout/transport exception
      2. Trigger NPC and assert fallback line is sent
      3. Assert logger called with exception context
    Expected Result: Graceful fallback with logged error
    Evidence: .sisyphus/evidence/task-9-error-fallback.txt
  ```

  **Commit**: YES
  - Message: `feat(npc): add async llm gateway callbacks`
  - Files: `typeclasses/llm_npc.py`
  - Pre-commit: `evennia test typeclasses.tests`

- [x] 10. Implement trigger filtering, lock guard, and speech response behavior

  **What to do**:
  - Implement strict response filter (name mention + say-type filtering).
  - Implement anti-loop guard (`from_obj == self` ignore).
  - Implement single-flight lock (`is_thinking`) and lock release semantics.
  - Implement reply emission method (room-visible response).

  **Must NOT do**:
  - Do not trigger on every room/system message.
  - Do not allow lock to remain set on exceptions.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Core business behavior with high regression risk.
  - **Skills**: `superpowers/test-driven-development`
    - `superpowers/test-driven-development`: Behavior-first implementation.
  - **Skills Evaluated but Omitted**:
    - `superpowers/systematic-debugging`: Only if tests expose race/failure.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 11, 12, 15, 16
  - **Blocked By**: 3, 8, 9

  **References**:
  - `typeclasses/objects.py:192` - message receive hook semantics.
  - `typeclasses/objects.py:210` - speech-related behavior reference.
  - `https://www.evennia.com/docs/latest/Howtos/Tutorial-NPC-Listening.html` - explicit say-detection examples.

  **Acceptance Criteria**:
- [x] NPC responds only when explicitly addressed by configured rule.
- [x] Concurrent triggers while thinking obey defined lock policy.
- [x] Fallback line matches required persona-safe wording pattern.

  **QA Scenarios**:
  ```
  Scenario: Explicit-address trigger
    Tool: Bash
    Preconditions: Task 10 implemented
    Steps:
      1. Trigger message containing NPC name (e.g., "llmnpc, 你好吗")
      2. Assert one LLM call scheduled and one response emitted
    Expected Result: Positive trigger path works once
    Evidence: .sisyphus/evidence/task-10-trigger-positive.txt

  Scenario: Non-addressed message ignored
    Tool: Bash
    Preconditions: Task 10 implemented
    Steps:
      1. Trigger generic room say without NPC name
      2. Assert LLM call count remains zero
    Expected Result: No cost-incurring call on irrelevant speech
    Evidence: .sisyphus/evidence/task-10-trigger-negative.txt
  ```

  **Commit**: YES
  - Message: `feat(npc): add trigger filter and lock guard`
  - Files: `typeclasses/llm_npc.py`
  - Pre-commit: `evennia test typeclasses.tests`

- [x] 11. Implement `typeclasses/tests.py` with mock-based Evennia tests

  **What to do**:
  - Add `EvenniaTest` test class for LLMNPC behavior.
  - Mock LLM helper to avoid network.
  - Cover success trigger, ignore path, lock path, and exception fallback path.
  - Verify expected room output calls / messaging side effects.

  **Must NOT do**:
  - Do not rely on live API key or external endpoint in CI/local tests.
  - Do not write flaky time-dependent assertions.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Framework-specific behavior testing and deterministic mocks.
  - **Skills**: `superpowers/test-driven-development`
    - `superpowers/test-driven-development`: Required discipline for this task.
  - **Skills Evaluated but Omitted**:
    - `superpowers/brainstorming`: Test matrix already finalized.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: 13, 14
  - **Blocked By**: 5, 7, 10

  **References**:
  - `typeclasses/tests.py` - target file for new tests.
  - `https://www.evennia.com/docs/latest/Coding/Unit-Testing.html` - test framework usage.
  - `https://www.evennia.com/docs/latest/api/evennia.utils.test_resources.html` - Evennia test resources and helpers.

  **Acceptance Criteria**:
- [x] Test module runs under `evennia test typeclasses.tests`.
- [x] Mocks fully intercept outbound LLM integration seam.
- [x] Required behavior matrix covered with deterministic assertions.

  **QA Scenarios**:
  ```
  Scenario: Unit suite execution
    Tool: Bash
    Preconditions: tests implemented
    Steps:
      1. Run `evennia test typeclasses.tests`
      2. Confirm all new test cases pass
    Expected Result: Exit code 0 and expected case count
    Evidence: .sisyphus/evidence/task-11-unit-suite.txt

  Scenario: Network isolation check
    Tool: Bash
    Preconditions: tests implemented
    Steps:
      1. Disable outbound network in test environment/mock
      2. Run tests again
    Expected Result: Tests still pass, proving complete mock isolation
    Evidence: .sisyphus/evidence/task-11-network-isolation.txt
  ```

  **Commit**: YES
  - Message: `test(npc): add llm npc behavior tests`
  - Files: `typeclasses/tests.py`
  - Pre-commit: `evennia test typeclasses.tests`

- [x] 12. Add in-game creation and binding command snippet

  **What to do**:
  - Provide exact Evennia in-game commands to create NPC object using new typeclass.
  - Include command to place NPC in room and quick sanity interaction command.
  - Add concise operator notes on required env vars before usage.

  **Must NOT do**:
  - Do not invent custom management command unless explicitly requested.
  - Do not include secrets in command examples.

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Precise operational documentation snippet.
  - **Skills**: `superpowers/writing-plans`
    - `superpowers/writing-plans`: Ensures executable, exact commands.
  - **Skills Evaluated but Omitted**:
    - `superpowers/test-driven-development`: Not a code behavior task.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: F1
  - **Blocked By**: 10

  **References**:
  - `https://www.evennia.com/docs/latest/Howtos/Beginner-Tutorial/Part3/Beginner-Tutorial-Adding-Command-And-Trait.html` - command usage style references.
  - `typeclasses/llm_npc.py` - final class path for typeclass creation.

  **Acceptance Criteria**:
- [x] Command snippet includes create + set typeclass + move/drop placement.
- [x] Snippet uses correct project-relative typeclass path.

  **QA Scenarios**:
  ```
  Scenario: Command syntax validation
    Tool: Bash
    Preconditions: snippet drafted
    Steps:
      1. Validate command strings match Evennia command syntax
      2. Confirm typeclass path points to existing module/class
    Expected Result: Commands are copy-paste executable in-game
    Evidence: .sisyphus/evidence/task-12-command-syntax.txt

  Scenario: Env prerequisite check
    Tool: Bash
    Preconditions: snippet drafted
    Steps:
      1. Verify required env vars listed near command snippet
      2. Verify no secret values embedded
    Expected Result: Safe operational guidance
    Evidence: .sisyphus/evidence/task-12-env-prereq.txt
  ```

  **Commit**: NO

- [x] 13. Stabilize edge cases from failing tests

  **What to do**:
  - Fix failures from Task 11 focusing on malformed message payloads, `from_obj is None`, and lock-release guarantees.
  - Harden response text parsing to avoid crashes on unexpected message structure.
  - Ensure all error exits release thinking lock.

  **Must NOT do**:
  - Do not bypass tests by weakening assertions.
  - Do not add broad `except Exception: pass` without logging.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Bug-fix stabilization for race/error paths.
  - **Skills**: `superpowers/systematic-debugging`
    - `superpowers/systematic-debugging`: Best fit for failure-driven refinement.
  - **Skills Evaluated but Omitted**:
    - `superpowers/brainstorming`: Not design-stage anymore.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential in Wave 3
  - **Blocks**: 14
  - **Blocked By**: 11

  **References**:
  - `typeclasses/tests.py` - failing case expectations.
  - `typeclasses/llm_npc.py` - lock and parsing logic under fix.
  - `https://www.evennia.com/docs/latest/Howtos/Tutorial-NPC-Listening.html` - expected `msg` payload assumptions.

  **Acceptance Criteria**:
- [x] All previously failing unit tests pass without reducing coverage intent.
- [x] Edge-case handling is explicit and logged where appropriate.

  **QA Scenarios**:
  ```
  Scenario: Regression closure
    Tool: Bash
    Preconditions: Task 13 fixes applied
    Steps:
      1. Re-run only previously failing tests
      2. Confirm pass and no new failures introduced
    Expected Result: Stable edge-case coverage
    Evidence: .sisyphus/evidence/task-13-regression-closure.txt

  Scenario: Lock release guarantee
    Tool: Bash
    Preconditions: Task 13 fixes applied
    Steps:
      1. Force exception path in LLM callback
      2. Trigger next message and verify processing continues
    Expected Result: Lock resets correctly after failure
    Evidence: .sisyphus/evidence/task-13-lock-release.txt
  ```

  **Commit**: YES
  - Message: `fix(npc): harden edge-case message handling`
  - Files: `typeclasses/llm_npc.py`, `typeclasses/tests.py`
  - Pre-commit: `evennia test typeclasses.tests`

- [x] 14. Run full test suite and capture artifacts

  **What to do**:
  - Run target test suite and collect outputs.
  - Verify no syntax/import errors across touched files.
  - Save command outputs as evidence artifacts.

  **Must NOT do**:
  - Do not mark complete if tests are skipped/xfail without rationale.
  - Do not omit evidence artifacts.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Verification and artifact discipline.
  - **Skills**: `superpowers/verification-before-completion`
    - `superpowers/verification-before-completion`: Enforces evidence-first completion.
  - **Skills Evaluated but Omitted**:
    - `superpowers/brainstorming`: Not applicable.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: 15, 16, F2, F3
  - **Blocked By**: 11, 13

  **References**:
  - `requirements.txt` - dependency integrity check.
  - `server/conf/settings.py` - syntax/import sanity.
  - `typeclasses/llm_npc.py` - module sanity.
  - `typeclasses/tests.py` - test execution target.

  **Acceptance Criteria**:
- [x] `evennia test typeclasses.tests` passes.
- [x] Python compile/import checks pass for all changed Python files.
- [x] Evidence artifacts exist for all verification commands.

  **QA Scenarios**:
  ```
  Scenario: Full verification run
    Tool: Bash
    Preconditions: Implementation tasks complete
    Steps:
      1. Run `python -m py_compile server/conf/settings.py typeclasses/llm_npc.py typeclasses/tests.py`
      2. Run `evennia test typeclasses.tests`
      3. Capture outputs to evidence files
    Expected Result: All commands succeed with zero failures
    Evidence: .sisyphus/evidence/task-14-full-verify.txt

  Scenario: Artifact completeness
    Tool: Bash
    Preconditions: Verification run done
    Steps:
      1. Check evidence directory for task-14 artifacts
      2. Confirm timestamps and non-empty content
    Expected Result: Evidence files are present and readable
    Evidence: .sisyphus/evidence/task-14-artifact-check.txt
  ```

  **Commit**: NO

- [x] 15. Verify non-blocking runtime behavior under simulated latency

  **What to do**:
  - Simulate slow LLM response in mocked path.
  - Confirm NPC scheduling does not stall command processing flow.
  - Confirm lock behavior under rapid repeated messages.

  **Must NOT do**:
  - Do not infer non-blocking from code inspection alone.
  - Do not ignore lock contention behavior.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Concurrency behavior verification.
  - **Skills**: `superpowers/systematic-debugging`, `superpowers/verification-before-completion`
    - `superpowers/systematic-debugging`: Diagnose latency/ordering issues.
    - `superpowers/verification-before-completion`: Requires hard evidence.
  - **Skills Evaluated but Omitted**:
    - `superpowers/test-driven-development`: Already covered by test implementation tasks.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: F3
  - **Blocked By**: 10, 14

  **References**:
  - `typeclasses/llm_npc.py` - async call and lock implementation.
  - `typeclasses/tests.py` - latency/lock test cases.
  - `https://docs.twisted.org/en/stable/core/howto/threading.html` - expected reactor behavior.

  **Acceptance Criteria**:
- [x] Latency simulation proves response scheduling is asynchronous.
- [x] Rapid repeat inputs during lock do not create multi-call storm.

  **QA Scenarios**:
  ```
  Scenario: Simulated slow LLM
    Tool: Bash
    Preconditions: tests available with latency mock
    Steps:
      1. Run targeted latency test case
      2. Assert command flow continuation in test assertions
    Expected Result: No blocking behavior observed
    Evidence: .sisyphus/evidence/task-15-latency.txt

  Scenario: Burst input lock contention
    Tool: Bash
    Preconditions: lock test case implemented
    Steps:
      1. Trigger multiple rapid address messages in test harness
      2. Assert bounded API call count per lock policy
    Expected Result: Single-flight behavior enforced
    Evidence: .sisyphus/evidence/task-15-lock-contention.txt
  ```

  **Commit**: NO

- [x] 16. Scope and security compliance review

  **What to do**:
  - Ensure no secrets or provider keys are committed.
  - Ensure changes are limited to requested files/scope.
  - Ensure no accidental feature expansion beyond baseline LLMNPC behavior.

  **Must NOT do**:
  - Do not accept hidden scope expansion.
  - Do not leave insecure defaults that leak credentials.

  **Recommended Agent Profile**:
  - **Category**: `oracle`
    - Reason: Independent policy/scope audit before final review wave.
  - **Skills**: `superpowers/requesting-code-review`
    - `superpowers/requesting-code-review`: Structured readiness check.
  - **Skills Evaluated but Omitted**:
    - `superpowers/brainstorming`: Implementation already complete.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: F1, F4
  - **Blocked By**: 7, 10, 14

  **References**:
  - `requirements.txt`
  - `server/conf/settings.py`
  - `typeclasses/llm_npc.py`
  - `typeclasses/tests.py`

  **Acceptance Criteria**:
- [x] No hardcoded secret values appear in changed files.
- [x] No changes outside requested deliverable scope.
- [x] Guardrails still satisfied after final edits.

  **QA Scenarios**:
  ```
  Scenario: Secret leakage scan
    Tool: Bash
    Preconditions: Implementation complete
    Steps:
      1. Search changed files for token-like literals and API key patterns
      2. Confirm only env variable references remain
    Expected Result: No credentials committed
    Evidence: .sisyphus/evidence/task-16-secret-scan.txt

  Scenario: Scope drift scan
    Tool: Bash
    Preconditions: Implementation complete
    Steps:
      1. Compare changed file list against requested deliverables
      2. Flag any extra modules unrelated to feature
    Expected Result: Changes match agreed scope
    Evidence: .sisyphus/evidence/task-16-scope-scan.txt
  ```

  **Commit**: NO

---

## Final Verification Wave (MANDATORY)

- [x] F1. **Plan Compliance Audit** — `oracle`
  Verify every Must Have / Must NOT Have against changed files and evidence artifacts.

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run static checks/tests and scan for anti-patterns (`as any`, blanket exceptions, accidental secrets).

- [x] F3. **Real Scenario QA** — `unspecified-high`
  Replay QA scenarios from all tasks and save evidence under `.sisyphus/evidence/final-qa/`.

- [x] F4. **Scope Fidelity Check** — `deep`
  Ensure no implementation drift beyond requested scope.

---

## Commit Strategy

- **1**: `chore(deps): add llm npc runtime dependencies` — `requirements.txt`
- **2**: `feat(settings): add llm env config loading` — `server/conf/settings.py`
- **3**: `feat(npc): add async llm npc typeclass` — `typeclasses/llm_npc.py`
- **4**: `test(npc): add llm npc behavior tests` — `typeclasses/tests.py`

---

## Success Criteria

### Verification Commands
```bash
evennia test typeclasses.tests
```

### Final Checklist
- [x] All Must Have implemented
- [x] All Must NOT Have absent
- [x] All tests pass
- [x] Evidence artifacts captured
