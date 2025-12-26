# DSPy Refactoring Guide

## What Was Wrong

**Before**: Agents imported `dspy` but never actually used it
```python
import dspy
# ... then just wrote normal Python code with no DSPy signatures
```

## What's Fixed

**After**: Agents now use `dspy.ChainOfThought` with typed signatures
```python
from backend.core.dspy_signatures import DecomposeUserGoal
self.decomposer = dspy.ChainOfThought(DecomposeUserGoal)
result = self.decomposer(user_goal=goal, context=context)
```

---

## ✅ Refactored Agents

### Supervisor (Tier 1) - **DONE**
- Uses `DecomposeUserGoal` signature
- Uses `RouteToAgent` signature
- Uses `NarrateResults` signature
- All with `dspy.ChainOfThought` modules

---

## 🔧 TODO: Refactor Remaining Agents

### Architect (Tier 3)
**File**: `backend/agents/architect/agent.py`

**DSPy Signature to Use**: `ArchitectPlan`

**Pattern**:
```python
from backend.core.dspy_signatures import ArchitectPlan

class ArchitectAgent(SudoAgent):
    def __init__(self, agent_id, role):
        super().__init__(agent_id, role)
        self.planner = dspy.ChainOfThought(ArchitectPlan)

    async def forward(self, goal: str):
        result = self.planner(
            goal=goal,
            constraints="Budget: 2hrs, Tech: Python, DSPy, FastAPI"
        )
        # result.architecture, result.components, result.delegation_order
```

---

### Coder (Tier 3)
**File**: `backend/agents/coder/agent.py`

**DSPy Signature to Use**: `GenerateCode`

**Pattern**:
```python
from backend.core.dspy_signatures import GenerateCode

class CoderAgent(SudoAgent):
    def __init__(self, agent_id, role):
        super().__init__(agent_id, role)
        self.code_generator = dspy.ChainOfThought(GenerateCode)

    async def forward(self, task_description: str, architecture_plan: str):
        result = self.code_generator(
            task_description=task_description,
            architecture_plan=architecture_plan
        )
        # result.code, result.explanation
```

---

### Tester (Tier 3)
**File**: `backend/agents/tester/agent.py`

**DSPy Signatures to Use**:
- `GenerateTests` - for creating test suites
- `ValidateLogic` - for checking correctness

**Pattern**:
```python
from backend.core.dspy_signatures import GenerateTests, ValidateLogic

class TesterAgent(SudoAgent):
    def __init__(self, agent_id, role):
        super().__init__(agent_id, role)
        self.test_generator = dspy.ChainOfThought(GenerateTests)
        self.validator = dspy.ChainOfThought(ValidateLogic)

    async def forward(self, code: str, requirements: str):
        # Step 1: Generate tests
        test_result = self.test_generator(code=code, requirements=requirements)

        # Step 2: Validate logic
        validation = self.validator(
            code=code,
            test_results=test_result.test_code
        )
        # validation.is_valid, validation.issues, validation.recommendations
```

---

### Documenter (Tier 3)
**File**: `backend/agents/documenter/agent.py`

**DSPy Signature to Use**: `GenerateDocumentation`

**Pattern**:
```python
from backend.core.dspy_signatures import GenerateDocumentation

class DocumenterAgent(SudoAgent):
    def __init__(self, agent_id, role):
        super().__init__(agent_id, role)
        self.doc_generator = dspy.ChainOfThought(GenerateDocumentation)

    async def forward(self, code: str, architecture: str, test_results: str):
        result = self.doc_generator(
            code=code,
            architecture=architecture,
            test_results=test_results
        )
        # result.documentation, result.api_reference
```

---

### Validator (Tier 3)
**File**: `backend/agents/validator/agent.py`

**DSPy Signature to Use**: `AuditCodeBundle`

**Pattern**:
```python
from backend.core.dspy_signatures import AuditCodeBundle

class ValidatorAgent(SudoAgent):
    def __init__(self, agent_id, role):
        super().__init__(agent_id, role)
        self.auditor = dspy.ChainOfThought(AuditCodeBundle)

    async def forward(self, code: str, tests: str, docs: str):
        result = self.auditor(
            code=code,
            tests=tests,
            documentation=docs,
            quality_standards="PEP8, 100% test coverage, JSDoc"
        )
        # result.is_valid, result.audit_report, result.critical_issues
```

---

## Tier 2 Operational Agents (TODO)

Need to create these from scratch:

1. **ClimateAgent** - Uses `AnalyzeClimate` signature
2. **NutrientAgent** - Similar pattern for nutrients/irrigation
3. **PhotoperiodAgent** - Light cycle management
4. **PredictiveAgent** - Uses `PredictGrowthOutcome` signature
5. **AnomalyAgent** - Sensor drift detection

---

## Key Benefits

### Before (Fake DSPy):
- No structured prompting
- No type safety
- Manual string formatting
- No reasoning traces

### After (Real DSPy):
- ✅ Typed input/output fields
- ✅ Automatic prompt optimization
- ✅ Reasoning traces logged
- ✅ Can compile for better performance
- ✅ Can optimize with `dspy.teleprompt`

---

## Next Steps

1. **Refactor Architect** - Most important for delegation
2. **Refactor Coder, Tester, Validator** - Complete validation chain
3. **Create Tier 2 agents** - Greenhouse operations
4. **Test full workflow** - User goal → Supervisor → Agents → Results
5. **Add DSPy compilation** - Optimize prompts against examples

---

**Status**: Supervisor refactored ✅
**Remaining**: 5 Tier 3 agents + 5 Tier 2 agents = 10 agents to refactor
