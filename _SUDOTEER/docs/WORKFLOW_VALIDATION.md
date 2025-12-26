# 🔄 _SUDOTEER Workflow Validation Chain

## Overview

The Validation Chain is the automated oversight mechanism that ensures high-quality output across the agency. It enforces a linear "Check-and-Balance" system between agents.

## The Chain of Custody

1. **Architect**: Designs the plan.
2. **Coder**: Implements the technical solution based on the plan.
3. **Tester**: Validates the implementation with unit tests.
4. **Documenter**: Summarizes the work into the Almanac.
5. **Validator**: Performs the final "Surge Audit" to verify all artifacts meet the mission criteria.

## State Transitions

- `idle` -> `active`: Agent has received a task from the Bus.
- `active` -> `success`: Agent has completed the task and validated the output.
- `active` -> `error`: Agent has failed a self-audit or encountered a runtime exception.

## A2M Communication (Agent-to-Manager)

Agents report their status to the **Supervisor** and the **UI Bridge** through structured signals:

```json
{
    "from_agent": "coder_01",
    "status": "success",
    "artifacts": ["main.py", "utils.py"],
    "utilization": 450
}
```

## Resilience Heuristics

-   **Auto-Retry**: If an agent fails, the Orchestrator attempts a 3-pass retry with diagnostic injection.
-   **Dead Man's Switch**: If an agent hangs for >60s, the UI Bridge broadcasts a warning and the Supervisor attempts a restart.
-   **Financial Stability**: The `finance_tracker` monitors token usage and cost-effectiveness. Continuous failures trigger a system halt.

## Visual Integration

The Electron frontend provides real-time visualization of this workflow.

- **Node States**: Idle, Active (Breathing), Success (Solid Glow), Error (Shaking).
- **Data Flow**: Animated connectors show the "Torch" being passed between nodes.

## Example Execution
```python
from backend.core.orchestrator import orchestrator

result = await orchestrator.execute_validation_chain(
	goal="Create a secure file-swapping utility with SQLite storage."
)
```

## Monitoring
The system logs tokens, utilization, and effectiveness metrics at the end of every workflow execution.
