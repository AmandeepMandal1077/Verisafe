# VERISAFE — Development Workflow

> **Security-Aware Verification Pipeline for Repairing Vulnerable LLM-Generated Code**

This document outlines the phased development workflow for the VERISAFE research prototype. Each phase is broken into roles, tasks, and estimated time allocations.

---

## Phase 1 — Foundation & Tool Integration

**Objective:** Build the core infrastructure — API connectivity, SAST tool wrappers, and the verification engine.

---

### Role 1: AI & Prompt Engineer

**Focus:** LLM API integration and VERISAFE prompt construction.

| # | Task | Description | Est. Time |
|---|------|-------------|-----------|
| 1 | **API Wrappers** | Write a Python script (`llm_client.py`) with a function `ask_llm(prompt, model="gpt-4o")` that can successfully call an LLM API (OpenAI / Gemini / Claude) and return the raw code response. Pick **one model** for the MVP. | 2 hrs |
| 2 | **The Prompt Builder** | Write a function `build_verisafe_prompt(vulnerable_code, vuln_type, lines, fix_guidance)` that stitches input variables into a structured prompt instructing the LLM to produce a secure patch. | 3 hrs |
| 3 | **Fallback / Retry Logic** | Write a function that takes failure reasons from the Verification stage and re-prompts the LLM: _"Your last patch failed because [Reason]. Try again."_ Implements the iterative repair loop. | 2 hrs |

**Deliverables:** `llm_client.py` with `ask_llm()`, `build_verisafe_prompt()`, and `retry_with_feedback()`.

---

### Role 2: Security Analyst

**Focus:** Integrating SAST tools (Bandit & Semgrep) as the Detection & Vulnerability Check modules.

| # | Task | Description | Est. Time |
|---|------|-------------|-----------|
| 1 | **Subprocess Wrappers** | Write `sast_runner.py`. Use Python's `subprocess.run()` to execute `bandit -r target.py -f json` and `semgrep --json target.py`. | 3 hrs |
| 2 | **JSON Parsing** | Parse the raw tool output into a clean, normalized list of findings: `[{"tool": "bandit", "type": "B608: SQL Injection", "lines": [14, 15]}]`. | 2 hrs |
| 3 | **The Knowledge Base** | Create a Python dictionary (`rules.py`) mapping common SAST rule IDs to best-practice fix guidance required for Baseline E. Example: `{"B608": "Use parameterized queries with SQLAlchemy instead of string formatting."}` | 2 hrs |

**Deliverables:** `sast_runner.py` with `run_bandit()`, `run_semgrep()`, `parse_results()`; `rules.py` knowledge base.

---

### Role 3: Architect & Verifier

**Focus:** Building the Verification Flow and the Main Orchestrator.

| # | Task | Description | Est. Time |
|---|------|-------------|-----------|
| 1 | **Patch Relevance Checker** | Write `verify.py`. Use Python's `difflib` to compare the original source with the patched version. Ensure modifications only occur around the flagged vulnerable line numbers. | 3 hrs |
| 2 | **Hallucination Checker** | Use Python's `ast` module to parse the patched code, extract all `import` statements, and check them against a predefined allowlist of safe libraries. Flag any hallucinated or unknown imports. | 2 hrs |
| 3 | **The Main Orchestrator** | Write `main.py` — the glue script that drives the full pipeline end-to-end (see Phase 2 below). | 2 hrs |

**Deliverables:** `verify.py` with `check_patch_relevance()`, `check_hallucinations()`; `main.py` orchestrator.

---

## Phase 2 — Pipeline Assembly & Integration

**Objective:** Wire all modules into the end-to-end VERISAFE pipeline.

### Orchestrator Flow (`main.py`)

```
┌─────────────────────────────────────────────────────────────┐
│                      VERISAFE Pipeline                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Run SAST tools on test_app.py                           │
│     └── sast_runner.run_bandit() + run_semgrep()            │
│                                                             │
│  2. Parse & normalize findings                              │
│     └── sast_runner.parse_results()                         │
│                                                             │
│  3. Enrich findings with fix guidance                       │
│     └── rules.py knowledge base lookup                      │
│                                                             │
│  4. Build the VERISAFE prompt                               │
│     └── llm_client.build_verisafe_prompt()                  │
│                                                             │
│  5. Send prompt to LLM                                      │
│     └── llm_client.ask_llm()                                │
│                                                             │
│  6. Save patched code → patched_app.py                      │
│                                                             │
│  7. Verify the patch                                        │
│     ├── verify.check_patch_relevance()                      │
│     └── verify.check_hallucinations()                       │
│                                                             │
│  8. Re-run SAST tools on patched_app.py                     │
│     └── sast_runner.run_bandit() + run_semgrep()            │
│                                                             │
│  9. Report result                                           │
│     ├── ✅ [SUCCESS] Pipeline Passed                        │
│     └── ❌ [FAIL] Retrying… (loop back to step 4)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 3 — Verification & Validation

**Objective:** Ensure the pipeline correctly detects, patches, and verifies security vulnerabilities.

| # | Task | Description |
|---|------|-------------|
| 1 | **Unit Tests** | Write unit tests for each module — `llm_client`, `sast_runner`, `rules`, `verify`. |
| 2 | **Integration Test** | Run the full pipeline against `test_app.py` end-to-end and validate the output. |
| 3 | **Edge Cases** | Test with code containing multiple vulnerabilities, nested issues, or no vulnerabilities at all. |
| 4 | **Retry Loop Validation** | Confirm the fallback/retry logic triggers correctly when a patch fails verification. |

---

## Phase 4 — Documentation & Reporting

**Objective:** Package the prototype for presentation and academic submission.

| # | Task | Description |
|---|------|-------------|
| 1 | **README.md** | Professional documentation covering setup, usage, architecture, and limitations. |
| 2 | **Sample Outputs** | Capture and document example pipeline runs with before/after code diffs. |
| 3 | **Research Alignment** | Map each module back to the corresponding section in the research paper (e.g., Fig 4.1 verification flow). |
| 4 | **Demo Preparation** | Prepare a live demo walkthrough of the pipeline. |

---

## Project File Structure (Target)

```
Verisafe/
├── main.py                 # Orchestrator — drives the full pipeline
├── llm_client.py           # LLM API wrapper + prompt builder + retry logic
├── sast_runner.py          # Bandit & Semgrep subprocess wrappers + JSON parsers
├── verify.py               # Patch relevance checker + hallucination detector
├── rules.py                # Knowledge base: SAST rule ID → fix guidance mapping
├── test_app.py             # Intentionally vulnerable Flask app (input)
├── patched_app.py          # Auto-generated secure version (output)
├── requirements.txt        # Python dependencies
├── tests/                  # Unit and integration tests
│   ├── test_llm_client.py
│   ├── test_sast_runner.py
│   └── test_verify.py
├── README.md               # Project documentation
├── WORKFLOW.md              # This file
└── .gitignore
```

---

## Summary Timeline

| Phase | Description | Estimated Effort |
|-------|-------------|------------------|
| **Phase 1** | Foundation & Tool Integration | ~21 hrs (across 3 roles) |
| **Phase 2** | Pipeline Assembly & Integration | ~3–4 hrs |
| **Phase 3** | Verification & Validation | ~4–5 hrs |
| **Phase 4** | Documentation & Reporting | ~3–4 hrs |
| | **Total** | **~31–34 hrs** |

---

> _This workflow is designed for the initial MVP. Subsequent iterations may introduce additional SAST rules, support for multiple programming languages, or integration with CI/CD pipelines._
