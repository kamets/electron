The project structure and the **CoALA (Cognitive Architectures for Language Agents)** model, here is the direct mapping of the theoretical "Proposal" and "Evaluation" steps to your specific code files.

This mapping reveals exactly where the "Thinking" happens inside your `backend/` directory.


|**CoALA Step**|**Theoretical Function**|**Your Project File**|**Specific Function / Logic**|
|---|---|---|---|
|**1. Proposal**|_Generating options/plans based on current state._|**`backend/core/memory/manager.py`**|**The Context Assembler.**<br><br>  <br><br>This script constructs the "Context Sandwich." By combining the User Input with available tools (`tools_registry.json`), it sets the stage for the LLM to "Propose" the next move (e.g., "I should read the file").|
|**2. Evaluation**|_Checking the plan against rules, risks, and memory._|**`backend/core/memory/dspy_modules/calibration.py`**|**The Hubris Detector.**<br><br>  <br><br>Before acting, this module runs the `CalibrationCheck` signature. It calculates an `ambiguity_score`. If the score is > 0.5, it evaluates the proposal as "Too Risky" and halts execution.|
|**"**|_Checking against Permission/Skill Constraints._|**`backend/db/neo4j_ops.py`**|**The Rule Enforcer.**<br><br>  <br><br>This file executes the Cypher queries to fetch `[:MUST_OBEY]` rules. It evaluates if the agent _can_ technically perform the action based on its constraints.|
|**"**|_Checking against Past Experience._|**`backend/db/chroma_ops.py`**|**The History Check.**<br><br>  <br><br>Fetches "What Failed" from ChromaDB. If a similar plan failed previously, the evaluation context (System Prompt) is updated to warn against it.|
|**"**|_Checking against Mastery Level._|**`backend/core/memory/manager.py`**|**Fog of War Logic.**<br><br>  <br><br>Inside the manager, the code evaluates `if Tool_XP < Required_XP`. If true, the proposal to "Execute Tool" is rejected and replaced with "Read Docs".|
|**3. Selection**|_Choosing the final action to execute._|**`backend/core/middleware/bus.py`**|**The Bus / Executor.**<br><br>  <br><br>Once a proposal passes all evaluations, this script actually executes the tool or returns the response to the user.|


---


### 🧩 Visualizing the Code Flow

Here is the flow diagram showing how a single "Thought" moves through your specific files during the CoALA cycle.


```mermaid
flowchart TD
    %% Visual Style: File Mapping
    classDef file fill:#232F3E,stroke:#fff,stroke-width:2px,color:#fff;
    classDef step fill:#F5A623,stroke:#333,stroke-width:2px,color:#fff;
    classDef logic fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff;

    User(User Input) --> Mgr["manager.py"]:::file
    
    subgraph Proposal_Phase [Step 1: Proposal]
        Mgr --> Ctx{Assemble Context}:::logic
        Ctx --> Tools["tools_registry.json"]:::file
        Tools --> Plan[LLM Generates Plan]:::step
    end

    Plan --> Eval_Gate

    subgraph Evaluation_Phase [Step 2: Evaluation]
        direction TB
        Eval_Gate{Evaluation Gate}:::logic
        
        %% Check 1: Risk
        Eval_Gate --> Calib["dspy_modules/calibration.py"]:::file
        Calib -- "Risk Score" --> Check1{Is Safe?}
        
        %% Check 2: Rules
        Check1 -- "Yes" --> Neo["neo4j_ops.py"]:::file
        Neo -- "Constraints" --> Check2{Is Allowed?}
        
        %% Check 3: Mastery
        Check2 -- "Yes" --> Fog["manager.py (Fog Logic)"]:::logic
        Fog -- "XP Level" --> Check3{Is Skilled?}
    end

    subgraph Selection_Phase [Step 3: Selection]
        Check3 -- "Yes" --> Bus["middleware/bus.py"]:::file
        Bus --> Exec[Execute Action]:::step
    end

    %% Rejections
    Check1 -- "No" --> Clarify[Return: Ask Clarification]
    Check3 -- "No" --> Read[Return: Read Docs]
```


---


### 💡 Implementation Takeaway

To strictly adhere to CoALA, ensure that your **`calibration.py` (The Hubris Detector)** runs _after_ the user input but _before_ any tool is actually touched.

- **Wrong Way:** User says "Delete file" -> Agent tries to delete -> Error catches it.
    
- **CoALA Way:** User says "Delete file" -> `calibration.py` sees "Delete" + High Ambiguity -> **Evaluates** as Unsafe -> Agent asks "Which file?" (Proposal rejected).