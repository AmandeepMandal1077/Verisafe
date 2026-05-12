# VERISAFE

### Security-Aware Verification Pipeline for Repairing Vulnerable LLM-Generated Code

---

## Abstract

Large Language Models (LLMs) are increasingly used to generate backend application code, yet studies consistently show that LLM-generated code frequently contains security vulnerabilities — even when functionally correct. This research prototype, **VERISAFE**, presents a closed-loop security verification pipeline that treats all LLM-generated code as untrusted by default. The system combines static analysis security testing (SAST) with AST-based patch verification and iterative LLM-driven repair to detect, localize, explain, patch, and verify security flaws in Python/Flask applications. By coupling automated vulnerability detection with guided secure-coding prompts and multi-stage patch validation, VERISAFE demonstrates a practical approach to improving the security posture of AI-generated code before deployment.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Why This Matters](#why-this-matters)
- [Prototype Workflow](#prototype-workflow)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Example Usage](#example-usage)
- [Expected Output](#expected-output)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [License](#license)

---

## Problem Statement

LLM-generated code is often **functionally correct but security-deficient**. Common issues include:

- Hardcoded credentials and weak authentication patterns
- Missing input validation and sanitization
- SQL/NoSQL injection via string concatenation
- Unsafe file upload handling without type or size restrictions
- Insecure session and cookie configurations
- Use of deprecated or vulnerable libraries

Existing code generation tools focus primarily on correctness and rarely perform security verification. There is a critical need for an automated pipeline that can detect these vulnerabilities, generate secure patches, and verify that the patches are both safe and relevant — without introducing hallucinated dependencies or breaking existing functionality.

---

## Why This Matters

- **LLM adoption is accelerating.** Developers increasingly rely on AI-generated code for rapid prototyping and production development.
- **Security is an afterthought.** Most LLM code generation workflows lack any security verification stage.
- **Patches can introduce new risks.** Naively applying LLM-suggested fixes can introduce hallucinated imports, irrelevant code changes, or incomplete patches.
- **Research gap.** Few systems implement a closed-loop pipeline that detects → patches → verifies → retries, treating the LLM output as untrusted at every stage.

VERISAFE addresses this gap by implementing a multi-stage verification pipeline grounded in static analysis and AST-based inspection.

---

## Prototype Workflow

The VERISAFE pipeline follows a seven-stage verification flow:

```
┌──────────────────────────────────────────────────────────────────┐
│                        VERISAFE Pipeline                         │
│                                                                  │
│   ┌───────────┐    ┌───────────┐    ┌───────────┐               │
│   │  1. BUILD  │───▶│ 2. DETECT │───▶│3. LOCALIZE│               │
│   │  Generate  │    │  Run SAST │    │ Map lines │               │
│   │   code     │    │  tools    │    │ & context │               │
│   └───────────┘    └───────────┘    └─────┬─────┘               │
│                                           │                      │
│                                           ▼                      │
│   ┌───────────┐    ┌───────────┐    ┌───────────┐               │
│   │ 6. VERIFY │◀───│ 5. PATCH  │◀───│4. EXPLAIN │               │
│   │ Relevance │    │ LLM-based │    │ Map to    │               │
│   │ & Safety  │    │ secure    │    │ guidance  │               │
│   │ checks    │    │ repair    │    │           │               │
│   └─────┬─────┘    └───────────┘    └───────────┘               │
│         │                                                        │
│         ▼                                                        │
│   ┌───────────┐         ┌──────────────────┐                    │
│   │ 7. REPORT │         │   RETRY LOOP     │                    │
│   │ Pass/Fail │────────▶│ If fail, re-prompt│──── back to 5     │
│   └───────────┘         └──────────────────┘                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Stage Breakdown

| Stage           | Description                                                                                                                  |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **1. Build**    | Accept or generate Python/Flask source code for analysis.                                                                    |
| **2. Detect**   | Run Bandit and Semgrep to identify security vulnerabilities.                                                                 |
| **3. Localize** | Extract vulnerable line numbers, rule IDs, and code context.                                                                 |
| **4. Explain**  | Map each finding to a human-readable explanation and secure coding guidance using the knowledge base.                        |
| **5. Patch**    | Construct a structured prompt (VERISAFE prompt) and send it to an LLM to generate a secure patch.                            |
| **6. Verify**   | Validate the patch using `difflib` (relevance check) and `ast` (hallucination check). Re-run SAST tools on the patched code. |
| **7. Report**   | Output `[SUCCESS] Pipeline Passed` or `[FAIL] Retrying…` and loop back if verification fails.                                |

---

## Features

- **Dual SAST Integration** — Runs both Bandit and Semgrep for comprehensive vulnerability coverage.
- **Structured Prompt Engineering** — Builds context-aware prompts with vulnerability type, affected lines, and best-practice fix guidance.
- **Patch Relevance Verification** — Uses `difflib` to ensure the LLM only modified code around the flagged vulnerability, not unrelated sections.
- **Hallucination Detection** — Uses Python's `ast` module to inspect imports in the patched code and flag any that aren't in the approved allowlist.
- **Iterative Repair Loop** — If a patch fails verification, the system automatically re-prompts the LLM with the failure reason.
- **Knowledge Base** — Maps SAST rule IDs to secure coding guidance (e.g., `B608` → _"Use parameterized queries"_).
- **End-to-End Orchestration** — A single `main.py` script drives the full pipeline from detection to verified output.

---

## Tech Stack

| Component          | Technology                                 |
| ------------------ | ------------------------------------------ |
| Language           | Python 3.10+                               |
| Target Framework   | Flask                                      |
| Static Analysis    | Bandit, Semgrep                            |
| LLM Integration    | OpenAI API (GPT-4o) / Gemini / Claude      |
| Patch Verification | `difflib`, `ast` (Python standard library) |
| Process Management | `subprocess` (Python standard library)     |
| Data Format        | JSON                                       |

---

## Project Structure

```
Verisafe/
├── main.py                 # Pipeline orchestrator
├── llm_client.py           # LLM API wrapper, prompt builder, retry logic
├── sast_runner.py          # Bandit & Semgrep execution + result parsing
├── verify.py               # Patch relevance & hallucination checking
├── rules.py                # Knowledge base: rule ID → fix guidance
├── test_app.py             # Sample vulnerable Flask app (input)
├── patched_app.py          # Auto-generated patched version (output)
├── requirements.txt        # Python dependencies
├── tests/                  # Unit and integration tests
├── WORKFLOW.md             # Development workflow & phases
└── README.md               # This file
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- `pip` package manager
- An API key for at least one supported LLM (OpenAI, Google Gemini, or Anthropic Claude)
- Bandit and Semgrep installed and available on `PATH`

### Setup

```bash
# Clone the repository
git clone https://github.com/<your-org>/verisafe.git
cd verisafe

# Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Install SAST tools (if not already installed)
pip install bandit
pip install semgrep

# Set your LLM API key
export OPENAI_API_KEY="your-api-key-here"          # Linux/macOS
set OPENAI_API_KEY=your-api-key-here               # Windows
```

---

## How to Run

### Run the Full Pipeline

```bash
python main.py --target test_app.py
```

This will:

1. Run Bandit and Semgrep on `test_app.py`
2. Parse and normalize the findings
3. Build a VERISAFE prompt with vulnerability context and fix guidance
4. Send the prompt to the configured LLM
5. Save the patched code to `patched_app.py`
6. Verify the patch (relevance + hallucination checks)
7. Re-run SAST tools on `patched_app.py`
8. Print the final result

### Run Individual Modules

```bash
# Run SAST analysis only
python sast_runner.py --target test_app.py

# Verify a patched file
python verify.py --original test_app.py --patched patched_app.py

# Test the LLM connection
python llm_client.py --test
```

---

## Example Usage

### Input: `test_app.py` (Vulnerable Flask App)

```python
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # SQL Injection vulnerability — string formatting in query
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    if user:
        return "Login successful"
    return "Invalid credentials"
```

### Output: `patched_app.py` (Secured Version)

```python
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Fixed: Using parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE username=? AND password=?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    if user:
        return "Login successful"
    return "Invalid credentials"
```

---

## Expected Output

```
═══════════════════════════════════════════════════════
              VERISAFE Pipeline — Run Report
═══════════════════════════════════════════════════════

[SCAN]    Running Bandit on test_app.py...
[SCAN]    Running Semgrep on test_app.py...
[DETECT]  Found 1 vulnerability:
            • B608: SQL Injection (lines 13-14)

[EXPLAIN] Guidance: Use parameterized queries instead
          of string formatting.

[PATCH]   Sending VERISAFE prompt to GPT-4o...
[PATCH]   Patched code saved to patched_app.py

[VERIFY]  Patch relevance check: ✅ PASSED
[VERIFY]  Hallucination check:   ✅ PASSED

[RESCAN]  Running Bandit on patched_app.py...
[RESCAN]  Running Semgrep on patched_app.py...
[RESCAN]  Vulnerabilities found: 0

═══════════════════════════════════════════════════════
  ✅ [SUCCESS] Pipeline Passed — All checks cleared.
═══════════════════════════════════════════════════════
```

---

## Limitations

- **Prototype scope.** Currently targets Python/Flask applications only. Other frameworks and languages are not supported.
- **Single-file analysis.** The current MVP processes one file at a time; multi-file projects require manual iteration.
- **LLM dependency.** Patch quality depends on the underlying LLM's capabilities. Results may vary across models and API versions.
- **SAST coverage.** Bandit and Semgrep do not cover all vulnerability classes. Runtime and logic vulnerabilities are outside the current detection scope.
- **No dynamic analysis.** The pipeline relies entirely on static analysis; it does not execute the code or perform fuzzing.
- **Knowledge base size.** The current rule-to-guidance mapping covers common OWASP findings but is not exhaustive.
- **Retry bound.** The iterative repair loop does not currently enforce a maximum retry count, which should be added for production use.

---

## Future Work

- **Multi-language support.** Extend the pipeline to Java, JavaScript/Node.js, and Go backends.
- **CI/CD integration.** Package VERISAFE as a GitHub Action or GitLab CI stage for automated security review.
- **Dynamic analysis.** Incorporate runtime testing (e.g., fuzzing, integration tests) into the verification stage.
- **Expanded knowledge base.** Auto-generate fix guidance from CWE/CVE databases.
- **Fine-tuned models.** Evaluate domain-specific fine-tuned LLMs for improved patch accuracy.
- **Confidence scoring.** Assign a confidence score to each patch based on verification depth and SAST delta.
- **Multi-file context.** Support whole-project analysis with cross-file dependency tracking.

---

## License

This project is developed as a research prototype. License details will be added upon publication.

---

## Acknowledgements

This prototype was developed as part of a research project on secure code verification and repair for LLM-generated backend applications.

---

<p align="center">
  <strong>VERISAFE</strong> — Treating AI-generated code as untrusted, by default.
</p>
