# Agent Enhancement Plan - "Harness Architecture"

**Date**: 2025-12-23
**Objective**: Transform agents from stateless one-shot executors to **state-aware, persistent workers**
**Inspiration**: Andrej Karpathy's OS Metaphor + Agentic Workflow patterns

---

## 🎯 **CURRENT PROBLEM: AI Amnesia**

### Current State (BAD):
```
Agent starts → Executes task → Returns result → FORGETS EVERYTHING
```

**Like hiring a new engineer every 5 minutes who has:**
- ❌ No memory of previous work
- ❌ No understanding of project context
- ❌ No access to past decisions
- ❌ No continuity between sessions

### Target State (GOOD):
```
Agent starts → Reads state from artifacts → Executes with context → Updates state → Next iteration with full memory
```

---

## 🏗️ **THE HARNESS ARCHITECTURE**

### **Layer 1: Outer Harness (Safety & Control)**
**Purpose**: Guardrails, checkpoints, human oversight

**Components:**
1. **StateGuard** - Validates all state mutations
2. **CheckpointManager** - Saves snapshots before risky operations
3. **HumanApproval** - HITL for critical decisions
4. **RollbackEngine** - Undo mechanism for failures

### **Layer 2: Context Engine (Memory Management)**
**Purpose**: Information flow, compaction, retrieval

**Components:**
1. **ContextCompactor** - Summarizes old sessions
2. **ArtifactRetriever** - Loads state from files
3. **IsolationManager** - Prevents context overflow
4. **PriorityRouter** - What to remember vs forget

### **Layer 3: Agent Workers (Execution)**
**Purpose**: Actual work with full context

**Enhanced Agents:**
1. **InitializerAgent** - Bootstraps projects with memory
2. **TaskAgent** - Incremental progress with state awareness
3. **ValidatorAgent** - Checks against historical standards
4. **DocumenterAgent** - Chronicles decisions and rationale

---

## 📝 **MEMORY ARTIFACTS (The Source of Truth)**

### **Core Principle**: "The Codebase IS the Memory"

Instead of relying on external vector DBs or chat history, we use **Git + Artifacts**:

### **Artifact Files to Implement:**

#### 1. `agent_state.json` ✅ **CRITICAL**
```json
{
  "session_id": "sess_2025_12_23_001",
  "iteration": 42,
  "last_agents": ["coder_01", "tester_01", "validator_01"],
  "workflow_status": "in_progress",
  "completed_tasks": [
    {"id": "task_001", "agent": "coder_01", "completed_at": "2025-12-23T10:00:00Z"},
    {"id": "task_002", "agent": "tester_01", "completed_at": "2025-12-23T10:05:00Z"}
  ],
  "pending_tasks": [
    {"id": "task_003", "agent": "documenter_01", "priority": "high"}
  ],
  "context_summary": "Implementing validation chain for forensic audit system...",
  "next_agent": "documenter_01"
}
```

**Purpose**: Primary state file - tells agents where they are in the workflow

#### 2. `progress_log.md` ✅ **CRITICAL**
```markdown
# Agent Progress Log

## Session: 2025-12-23 (Iteration 42)

### 🎯 Current Goal
Complete validation chain integration with 100% test coverage

### ✅ Completed This Session
- Coder: Implemented BaseValidator class
- Tester: Created 15 unit tests (all passing)
- Documenter: Added JSDoc for validator methods

### 🔧 In Progress
- Validator: Running compliance checks

### ⚠️ Blockers
- None

### 💡 Decisions Made
- Using tabs for indentation (per .github/copilot-instructions.md)
- Validator runs in separate thread to avoid blocking

### 📊 Metrics
- Test Coverage: 88.4%
- Lines Added: 245
- Files Modified: 8
```

**Purpose**: Human-readable session notes - context for next iteration

#### 3. `feature_status.json` ✅ **CRITICAL**
```json
{
  "total_features": 47,
  "completed": 35,
  "in_progress": 5,
  "blocked": 2,
  "not_started": 5,
  "features": [
    {
      "id": "feat_validation_chain",
      "status": "in_progress",
      "tests_passing": 15,
      "tests_total": 20,
      "coverage": 88.4,
      "assigned_to": "validator_01",
      "started_at": "2025-12-23T09:00:00Z"
    }
  ]
}
```

**Purpose**: Test status tracking - "200+ tests passing" visibility

#### 4. `decisions.log` ✅ **IMPORTANT**
```
2025-12-23T10:00:00Z | Coder_01 | DECISION | Use tabs instead of spaces (project standard)
2025-12-23T10:05:00Z | Architect_01 | DECISION | Validator runs in background thread (performance)
2025-12-23T10:10:00Z | Tester_01 | DECISION | Pytest over unittest (team preference)
```

**Purpose**: Chronicles why decisions were made - prevents rework

#### 5. `context_handoff.txt` ✅ **CRITICAL**
```
SESSION HANDOFF - 2025-12-23 10:15 AM

CONTEXT:
Working on validation chain for forensic audit system.

LAST AGENT: tester_01
WHAT WAS DONE: Created 15 unit tests for BaseValidator class. All passing.

NEXT AGENT: documenter_01
WHAT TO DO: Add comprehensive JSDoc documentation for all validator methods.

STATE FILES:
- agent_state.json: Updated with iteration 42
- feature_status.json: Tests marked as passing
- progress_log.md: Session notes added

IMPORTANT NOTES:
- Validator must not block main thread
- Follow PascalCase for class names
- Use tabs for indentation

CONTINUE FROM: Line 127 in backend/agents/validator/agent.py
```

**Purpose**: Explicit handoff between agents - no context loss

---

## 🔄 **THE ITERATIVE LOOP (Enhanced)**

### Current Loop (BASIC):
```python
async def run_workflow(workflow, state):
    while current_node:
        state = await execute_node(current_node, state)
        current_node = get_next_node(state)
    return state
```

**Problems**:
- ❌ No memory between iterations
- ❌ No state persistence
- ❌ No context awareness

### Enhanced Loop (HARNESS):
```python
async def run_workflow_with_harness(workflow, initial_state):
    # STEP 1: READ STATE FROM ARTIFACTS
    state = await read_state_from_artifacts()
    state.update(initial_state)

    # STEP 2: LOAD CONTEXT
    context = await load_session_context()
    state["context"] = context

    # STEP 3: VERIFY ENVIRONMENT
    env_status = await verify_environment()
    if not env_status.healthy:
        logger.error("Environment degraded, aborting")
        return state

    # STEP 4: RUN REGRESSION TESTS
    regression_results = await run_regression_tests()
    state["regression_status"] = regression_results

    # STEP 5: ITERATIVE EXECUTION
    while not workflow_complete(state):
        # CHECKPOINT: Save state before risky operation
        await create_checkpoint(state)

        # TICK: Watchdog for stall detection
        ui_bridge.tick()

        # EXECUTE: Run next agent with full context
        current_node = get_next_node(state)

        try:
            state = await execute_node_with_memory(current_node, state)
        except Exception as e:
            logger.error(f"Agent failed: {e}")
            # ROLLBACK: Restore from checkpoint
            state = await restore_checkpoint()
            break

        # UPDATE STATE: Write to artifacts
        await update_artifacts(state)

        # UPDATE PROGRESS: Log what happened
        await append_progress_log(state)

        # COMPACTION: Summarize old context if needed
        if len(state["context"]) > MAX_CONTEXT_SIZE:
            state["context"] = await compact_context(state["context"])

        # REFRESH: Prepare for next iteration
        await ui_bridge.broadcast("WORKFLOW_PROGRESS", "orchestrator", {
            "iteration": state["iteration"],
            "agent": current_node.agent_id,
            "status": state["status"]
        })

    # STEP 6: FINAL HANDOFF
    await write_handoff_note(state)

    return state
```

---

## 🛠️ **IMPLEMENTATION ROADMAP**

### **Phase 1: Artifact System** (4-6 hours)
**Priority**: 🔴 **CRITICAL**

**Files to Create:**
1. `backend/core/memory/artifact_manager.py`
2. `backend/core/memory/state_persistence.py`
3. `backend/core/harness/checkpoint_manager.py`

**Artifacts to Track:**
- `agent_state.json`
- `progress_log.md`
- `feature_status.json`
- `context_handoff.txt`
- `decisions.log`

**Implementation:**
```python
class ArtifactManager:
    def __init__(self, workspace_dir):
        self.workspace = Path(workspace_dir)
        self.state_file = self.workspace / "agent_state.json"
        self.progress_file = self.workspace / "progress_log.md"
        self.features_file = self.workspace / "feature_status.json"
        self.handoff_file = self.workspace / "context_handoff.txt"

    async def read_state(self) -> Dict:
        """Load state from agent_state.json"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return self._default_state()

    async def write_state(self, state: Dict):
        """Save state to agent_state.json"""
        self.state_file.write_text(json.dumps(state, indent=2))

    async def append_progress(self, entry: str):
        """Add entry to progress_log.md"""
        with open(self.progress_file, 'a') as f:
            f.write(f"\n{entry}\n")

    async def write_handoff(self, last_agent, next_agent, context):
        """Create handoff note for next session"""
        handoff = f"""
SESSION HANDOFF - {datetime.now()}

LAST AGENT: {last_agent}
NEXT AGENT: {next_agent}

CONTEXT:
{context}

CONTINUE FROM: {state['current_file']}:{state['current_line']}
"""
        self.handoff_file.write_text(handoff)
```

---

### **Phase 2: Context Engine** (6-8 hours)
**Priority**: 🔴 **CRITICAL**

**Components:**
1. **Context Compactor** - Summarize old sessions
2. **Git History Reader** - Load context from commits
3. **Priority Router** - What to remember

**Implementation:**
```python
class ContextEngine:
    async def load_context(self, workspace_dir) -> str:
        """
        Loads full context from:
        1. Git log (last 10 commits)
        2. progress_log.md (last session)
        3. context_handoff.txt (explicit notes)
        4. feature_status.json (test results)
        """
        context = []

        # Git history
        git_log = await self._read_git_log(workspace_dir, n=10)
        context.append(f"## Git History\n{git_log}")

        # Progress log
        progress = (Path(workspace_dir) / "progress_log.md").read_text()
        context.append(f"## Recent Progress\n{progress}")

        # Handoff notes
        if Path(workspace_dir / "context_handoff.txt").exists():
            handoff = (Path(workspace_dir) / "context_handoff.txt").read_text()
            context.append(f"## Handoff Notes\n{handoff}")

        # Feature status
        features = json.loads((Path(workspace_dir) / "feature_status.json").read_text())
        context.append(f"## Tests: {features['tests_passing']}/{features['tests_total']} passing")

        return "\n\n".join(context)

    async def compact_context(self, old_context: str) -> str:
        """
        Use LLM to summarize old context into key points.
        Keeps context window manageable.
        """
        summary_prompt = f"""
Summarize this agent session context into key points:

{old_context}

Focus on:
- What was accomplished
- Key decisions made
- Current blockers
- Next steps

Summary:"""

        summary = await self.llm.summarize(summary_prompt)
        return summary
```

---

### **Phase 3: Enhanced Agents** (8-10 hours)
**Priority**: 🟡 **HIGH**

**Upgrade All Agents:**

#### 1. **ArchitectAgent Enhancement**
```python
class ArchitectAgent(SudoAgent):
    async def forward(self, task: str) -> Dict:
        # 1. LOAD CONTEXT
        context = await self.context_engine.load_context(self.workspace)

        # 2. READ STATE
        state = await self.artifact_mgr.read_state()

        # 3. MAKE DECISION WITH FULL CONTEXT
        prompt = f"""
You are the Architect Agent. You have access to full project context.

{context}

Current iteration: {state['iteration']}
Last agents: {state['last_agents']}

Task: {task}

Based on the above context, what should we do next?
"""

        result = await self.signature(prompt=prompt)

        # 4. LOG DECISION
        await self.artifact_mgr.append_decision(
            agent=self.agent_id,
           decision=result.decision,
            rationale=result.rationale
        )

        # 5. UPDATE STATE
        state["last_agents"].append(self.agent_id)
        state["iteration"] += 1
        await self.artifact_mgr.write_state(state)

        return result
```

#### 2. **CoderAgent Enhancement**
```python
class CoderAgent(SudoAgent):
    async def forward(self, task: str) -> Dict:
        # READ HANDOFF
        handoff = await self.artifact_mgr.read_handoff()

        # LOAD CONTEXT
        context = await self.context_engine.load_context(self.workspace)

        # CODE WITH MEMORY
        prompt = f"""
You are the Coder Agent continuing from a previous session.

{context}

Handoff Note:
{handoff}

Task: {task}

Continue from where the last agent left off. Maintain coding standards.
"""

        result = await self.signature(prompt=prompt)

        # UPDATE PROGRESS
        await self.artifact_mgr.append_progress(f"""
### Coder Agent (Iteration {state['iteration']})
- Task: {task}
- Files Modified: {result.files_modified}
- Lines Added: {result.lines_added}
""")

        return result
```

---

### **Phase 4: Checkpoint & Rollback** (4-6 hours)
**Priority**: 🟡 **MEDIUM**

**Implementation:**
```python
class CheckpointManager:
    def __init__(self, checkpoint_dir):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

    async def create_checkpoint(self, state: Dict) -> str:
        """Save checkpoint before risky operation"""
        checkpoint_id = f"checkpoint_{state['iteration']}_{int(time.time())}"
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"

        checkpoint = {
            "id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "state": state,
            "git_commit": await get_current_git_commit()
        }

        checkpoint_file.write_text(json.dumps(checkpoint, indent=2))
        logger.info(f"Created checkpoint: {checkpoint_id}")

        return checkpoint_id

    async def restore_checkpoint(self, checkpoint_id: str) -> Dict:
        """Rollback to previous checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        checkpoint = json.loads(checkpoint_file.read_text())

        # Restore git state
        await git_reset(checkpoint["git_commit"])

        # Restore agent state
        return checkpoint["state"]
```

---

## 📊 **EXPECTED IMPROVEMENTS**

### **Before (Current State)**:
- ❌ Agents forget everything between runs
- ❌ No continuity across sessions
- ❌ Repeat same mistakes
- ❌ No learning from past decisions

### **After (Harness Architecture)**:
- ✅ Agents remember all past work
- ✅ Full continuity via artifacts
- ✅ Learn from documented decisions
- ✅ Git + artifacts = complete memory
- ✅ Checkpoint/rollback safety
- ✅ Context compaction prevents overflow

---

## 🎯 **SUCCESS METRICS**

| Metric | Before | After (Goal) |
|--------|--------|--------------|
| **Context Retention** | 0% (forgets everything) | 100% (full memory) |
| **Decision Consistency** | Random | Documented & followed |
| **Error Recovery** | Manual | Automatic rollback |
| **Session Continuity** | None | Complete |
| **Agent Quality** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 **IMPLEMENTATION ORDER**

### **Week 1: Foundation**
1. ✅ Create ArtifactManager
2. ✅ Implement state persistence
3. ✅ Add progress logging
4. ✅ Test with simple workflow

### **Week 2: Context Engine**
1. ✅ ContextEngine with git integration
2. ✅ Context compaction (LLM summarization)
3. ✅ Handoff notes system

### **Week 3: Agent Upgrades**
1. ✅ Enhance ArchitectAgent
2. ✅ Enhance CoderAgent
3. ✅ Enhance TesterAgent
4. ✅ Enhance DocumenterAgent
5. ✅ Enhance ValidatorAgent

### **Week 4: Safety & Polish**
1. ✅ CheckpointManager
2. ✅ RollbackEngine
3. ✅ Full integration testing
4. ✅ Documentation

---

**Status**: 📋 **READY FOR IMPLEMENTATION**
**Expected Quality**: ⭐⭐⭐⭐⭐ **World-Class**
**Inspiration**: Karpathy's OS Metaphor + Agentic Workflow Best Practices

*_SUDOTEER Agent Harness - Nothing But The Best*
