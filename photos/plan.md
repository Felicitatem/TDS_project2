# TDS Project 2 — AI Data Analyst

An AI agent that sources, prepares, analyzes, and visualizes data from arbitrary inputs.

---

## Design Evolution

### Approach 1 — Single-pass code generation
- Provide `questions.txt` and any attachments (CSV, images, etc.) directly to the LLM and ask it to generate runnable code.
- Execute the returned code in a Python REPL.

**Issue:** The LLM often assumes non-existent variable/file names, causing frequent execution errors.

---

### Approach 2 — Two-stage (ingest → solve)
1. Ask the LLM only for code to **scrape/read and normalize all available data**.  
2. Feed the **question + the prepared outputs** back to the LLM:
   - If the question is small/answerable directly, respond immediately.
   - Otherwise, request solution code, execute it, and return the result.

---

### Approach 3 — Two-stage with explicit metadata handoff
- **Stage 1 (Ingestion):** Ask the LLM for scraping/reading code that also writes a `metadata.txt` capturing:
  - Dataset metadata (schemas/shapes, column descriptions).
  - Important file paths and what each file contains.
  - The original questions.
  - The **expected JSON response format**.
- **Stage 2 (Solve):** Call the LLM again with only the **file paths + metadata**, asking for solution code that returns JSON in the specified format.

**Execution robustness:** Allow the LLM up to **3 automatic retries** to fix minor code errors detected at runtime.

---

### Approach 4 — Improving answer quality
Some models (e.g., Gemini in tests) can be inconsistent for certain requests.  
- Strategy: generate **multiple candidate answers** via separate LLM calls and select the best based on simple validation/quality checks.

---

## Iterative Chat Strategy (Key Insight)
Maintain a **single chat session** and iterate step-by-step:
- Send only the **minimal failing context** (e.g., the error message and the code fragment), not the entire question each time.
- Benefits:
  - Faster iterations and **lower token usage**.
  - Tighter feedback loop: focus on the precise mistake.
- Logic validation:
  - Even if code runs, detect likely wrong logic via **empty or obviously invalid outputs** and request a targeted fix.

