# Comparison of Ralph Loop Implementations

This document compares the Bash script implementation of the "Ralph loop" with the Python implementation in `ralph/graph.py`.

## Overview

The **Bash script** is a high-level orchestration script that manages distinct execution runs, archiving previous states based on git branches, and logging progress to a file. It treats the underlying agent (AMP or Claude) as a black box process.

The **Python script (`ralph/graph.py`)** is the internal execution loop for the agent itself. It manages the agent's state in memory and loops until a termination condition is met.

## Feature Comparison

| Feature | Bash Implementation (`ralph.sh`) | Python Implementation (`ralph/graph.py`) |
| :--- | :--- | :--- |
| **Primary Role** | Workflow Orchestration & Wrapper | Internal Agent Execution Loop |
| **Agent Execution** | Executes external CLI tools (`amp`, `claude`) | Invokes Python `create_single_step_agent` object |
| **State Persistence** | File-based (`prd.json`, `progress.txt`) | Memory-based (variable `messages`) |
| **Context Management** | Relies on git branch switching | Relies on Python object lifecycle |
| **Archiving** | **Yes** (Archives `prd.json` on branch change) | **No** (Ephemeral execution) |
| **Progress Logging** | Writes to `progress.txt` | Prints to stdout (`click.echo`) |
| **Completion Signal** | String match: `<promise>COMPLETE</promise>` | Tool message check: `ralph_DONE` |
| **Input Source** | Static files (`prompt.md`, `CLAUDE.md`) | Function argument (`instruction`) |

## Key Differences

### 1. Scope of Responsibility
*   **Bash:** Initializing the environment, archiving old runs, tracking the current git branch, and invoking the agent in a loop. It assumes the agent is an external process that might fail or need restarting.
*   **Python:** Running the agent's internal reasoning loop. It assumes it *is* the agent process.

### 2. Archiving Strategy
*   **Bash:** Implements a specific workflow where changing git branches signals a new "task" or context. It automatically archives the previous run's artifacts (`prd.json`, `progress.txt`) into a timestamped directory.
*   **Python:** Has no concept of past runs or archiving. It runs purely in the "now".

### 3. Loop Mechanism
*   **Bash:**
    ```bash
    for i in $(seq 1 $MAX_ITERATIONS); do
      OUTPUT=$(... run tool ...)
      if echo "$OUTPUT" | grep -q "COMPLETE"; then exit 0; fi
    done
    ```
    Re-runs the entire tool process each iteration.
*   **Python:**
    ```python
    for i in range(limit):
      result = agent.invoke({...})
      if check_done(result): break
    ```
    Maintains the loaded agent in memory and steps it forward.

## Recommendations for Python Implementation

To match the functionality of the Bash script, the Python implementation would need to:

1.  **Add File Logging:** Implement a file handler for logging to write to a `progress.txt` or similar log file.
2.  **Implement Archiving Logic:** Add a startup check that looks at git branch or a persistence file to determine if the previous run should be archived.
3.  **Persist State:** Save the `messages` or agent state to disk (e.g., `prd.json` or a pickle file) after each step so it can be resumed if the process is killed.
