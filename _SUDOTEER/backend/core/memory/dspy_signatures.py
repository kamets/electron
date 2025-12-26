"""
DSPy Signatures for _SUDOTEER Agents.

These define the typed interfaces for agent reasoning steps,
following the DVR (Decompose → Validate → Recompose) framework.
"""

import dspy

# ============================================
# TIER 1: SUPERVISOR SIGNATURES
# ============================================

class DecomposeUserGoal(dspy.Signature):
	"""Decompose a high-level user goal into actionable subtasks."""

	user_goal: str = dspy.InputField(desc="The user's natural language goal or request")
	context: str = dspy.InputField(desc="Current system state and available agents")

	subtasks: list[str] = dspy.OutputField(desc="List of specific subtasks needed to achieve the goal")
	reasoning: str = dspy.OutputField(desc="Step-by-step reasoning about task decomposition")

class RouteToAgent(dspy.Signature):
	"""Determine which agent(s) should handle a specific subtask."""

	subtask: str = dspy.InputField(desc="A specific subtask to be routed")
	available_agents: str = dspy.InputField(desc="JSON of available agents and their capabilities")

	agent_id: str = dspy.OutputField(desc="The agent ID best suited for this task")
	reasoning: str = dspy.OutputField(desc="Why this agent was selected")

class NarrateResults(dspy.Signature):
	"""Convert technical agent outputs into user-friendly narrative."""

	original_goal: str = dspy.InputField(desc="The user's original goal")
	agent_results: str = dspy.InputField(desc="JSON of results from delegated agents")

	narrative: str = dspy.OutputField(desc="Natural language summary for the user")
	key_insights: list[str] = dspy.OutputField(desc="Key takeaways or action items")

class RiskAssessment(dspy.Signature):
	"""Assesses the risk of a proposed action or tool execution."""

	proposed_action: str = dspy.InputField(desc="The tool execution or action being considered")
	context: str = dspy.InputField(desc="Current environment and system state")

	risk_score: float = dspy.OutputField(desc="Risk level (0.0 to 1.0)")
	risk_factor: str = dspy.OutputField(desc="Primary reason for this risk score")
	recommendation: str = dspy.OutputField(desc="Action: PROCEED, NOTIFY_USER, or PAUSE_EXECUTION")

# ============================================
# TIER 3: ARCHITECT SIGNATURES
# ============================================

class ArchitectPlan(dspy.Signature):
	"""Create a high-level architectural plan for a system design task."""

	goal: str = dspy.InputField(desc="System design goal or feature request")
	constraints: str = dspy.InputField(desc="Technical constraints, budget, or requirements")

	architecture: str = dspy.OutputField(desc="Detailed architectural plan")
	components: list[str] = dspy.OutputField(desc="List of components to be built")
	delegation_order: list[str] = dspy.OutputField(desc="Order in which components should be developed")

# ============================================
# TIER 3: CODER SIGNATURES
# ============================================

class GenerateCode(dspy.Signature):
	"""Generate production-quality code for a specific task."""

	task_description: str = dspy.InputField(desc="What the code should accomplish")
	architecture_plan: str = dspy.InputField(desc="Architectural context and design patterns to follow")

	code: str = dspy.OutputField(desc="Complete, production-ready code")
	explanation: str = dspy.OutputField(desc="Explanation of key design decisions")

# ============================================
# TIER 3: TESTER SIGNATURES
# ============================================

class GenerateTests(dspy.Signature):
	"""Generate comprehensive test cases for code."""

	code: str = dspy.InputField(desc="The code to be tested")
	requirements: str = dspy.InputField(desc="Functional requirements and edge cases")

	test_code: str = dspy.OutputField(desc="Complete test suite")
	coverage_analysis: str = dspy.OutputField(desc="Analysis of test coverage")

class ValidateLogic(dspy.Signature):
	"""Validate the logical correctness of code."""

	code: str = dspy.InputField(desc="Code to validate")
	test_results: str = dspy.InputField(desc="Results from running tests")

	is_valid: bool = dspy.OutputField(desc="Whether the code passes validation")
	issues: list[str] = dspy.OutputField(desc="Any issues found during validation")
	recommendations: str = dspy.OutputField(desc="Recommendations for improvement")

# ============================================
# TIER 3: DOCUMENTER SIGNATURES
# ============================================

class GenerateDocumentation(dspy.Signature):
	"""Generate comprehensive technical documentation."""

	code: str = dspy.InputField(desc="Code to document")
	architecture: str = dspy.InputField(desc="Architectural context")
	test_results: str = dspy.InputField(desc="Test results and coverage")

	documentation: str = dspy.OutputField(desc="Complete technical documentation in Markdown")
	api_reference: str = dspy.OutputField(desc="API reference section")

# ============================================
# TIER 3: VALIDATOR SIGNATURES
# ============================================

class AuditCodeBundle(dspy.Signature):
	"""Perform comprehensive audit of code + tests + docs."""

	code: str = dspy.InputField(desc="Code to audit")
	tests: str = dspy.InputField(desc="Test suite")
	documentation: str = dspy.InputField(desc="Documentation")
	quality_standards: str = dspy.InputField(desc="Quality standards to enforce")

	is_valid: bool = dspy.OutputField(desc="Whether the bundle passes audit")
	audit_report: str = dspy.OutputField(desc="Detailed audit report")
	critical_issues: list[str] = dspy.OutputField(desc="Critical issues that must be fixed")
	recommendations: list[str] = dspy.OutputField(desc="Recommendations for improvement")

# ============================================
# TIER 2: OPERATIONAL SIGNATURES (Greenhouse)
# ============================================

class AnalyzeClimate(dspy.Signature):
	"""Analyze greenhouse climate and recommend adjustments."""

	current_state: str = dspy.InputField(desc="Current temperature, humidity, CO2 readings")
	target_parameters: str = dspy.InputField(desc="Ideal conditions for current growth stage")

	analysis: str = dspy.OutputField(desc="Analysis of current conditions")
	recommended_actions: list[str] = dspy.OutputField(desc="Actions to take (e.g., 'increase heat', 'open vent')")
	urgency: str = dspy.OutputField(desc="Urgency level: low, medium, high, critical")

class PredictGrowthOutcome(dspy.Signature):
	"""Predict plant growth outcomes based on current conditions."""

	current_conditions: str = dspy.InputField(desc="Current environmental parameters")
	plant_type: str = dspy.InputField(desc="Type of plant being grown")
	days_to_maturity: int = dspy.InputField(desc="Expected days until harvest")

	prediction: str = dspy.OutputField(desc="Predicted growth outcome")
	risk_factors: list[str] = dspy.OutputField(desc="Identified risk factors")
	optimization_suggestions: str = dspy.OutputField(desc="How to optimize for better outcomes")

# ============================================
# MEMORY & KNOWLEDGE SIGNATURES
# ============================================

class SiftMemoryRequest(dspy.Signature):
	"""Determine the optimal retrieval strategy (Vector vs Graph) for a query."""

	query: str = dspy.InputField(desc="The natural language query or context request")
	available_stores: str = dspy.InputField(desc="Description of available Vector and Graph stores")

	strategy: str = dspy.OutputField(desc="Strategy: 'semantic' (Vector), 'relational' (Graph), or 'hybrid' (Both)")
	reasoning: str = dspy.OutputField(desc="Why this retrieval strategy was chosen")

class SplitMemoryStorage(dspy.Signature):
	"""Analyze data to decide how to split it between Vector and Graph storage."""

	data: str = dspy.InputField(desc="The data or observation to be stored")

	routing: str = dspy.OutputField(desc="Routing: 'vector', 'graph', or 'both'")
	semantic_summary: str = dspy.OutputField(desc="Unstructured summary for Vector/Semantic storage")
	entities: list[str] = dspy.OutputField(desc="Key entities found in the data")
	relationships: list[dict] = dspy.OutputField(desc="List of relationships to store in Graph storage (e.g., {'from': 'A', 'to': 'B', 'type': 'DEPENDS_ON'})")
	facts: list[dict] = dspy.OutputField(desc="Key-value pairs as facts (e.g., {'key': 'status', 'value': 'active'})")
	reasoning: str = dspy.OutputField(desc="Reasoning for the split decision")
class LogToMemory(dspy.Signature):
	"""Converts raw logs into concise episodic summaries and extracts graph entities."""

	raw_log: str = dspy.InputField(desc="The raw conversation or action log")

	summary: str = dspy.OutputField(desc="Concisely summarized 'Episodic' memory")
	entities: list[str] = dspy.OutputField(desc="Named entities (Agents, Tools, Files)")
	what_worked: list[str] = dspy.OutputField(desc="List of successful strategies or actions")
	what_failed: list[str] = dspy.OutputField(desc="List of errors or inefficient paths")
	improvement_plan: str = dspy.OutputField(desc="Recommendations for procedural guideline updates")
	quality_score: float = dspy.OutputField(desc="Confidence in the summary quality (0-1)")

class CuriosityCheck(dspy.Signature):
	"""Decides if the agent needs to read documentation or can proceed with tool execution."""

	task: str = dspy.InputField()
	current_mastery: str = dspy.InputField()
	available_docs: list[str] = dspy.OutputField(desc="Relevant files in /docs/ to read")

	action: str = dspy.OutputField(desc="READ_DOCS or EXECUTE_TOOL")
	reasoning: str = dspy.OutputField(desc="Why reading is required or why execution is safe")

# ============================================
# DVR FRAMEWORK SIGNATURES (Lean & Fast)
# ============================================

class DecomposeTask(dspy.Signature):
	"""Break a complex agent task into specific, sequential sub-steps."""

	task: str = dspy.InputField(desc="The high-level task to perform")
	role: str = dspy.InputField(desc="The role performing the task")
	context: str = dspy.InputField(desc="Episodic, Procedural, and Semantic context (The Context Sandwich)")

	subtasks: list[str] = dspy.OutputField(desc="Sequential list of simple sub-steps")
	reasoning: str = dspy.OutputField(desc="Logical reasoning for this breakdown")

class ValidateResult(dspy.Signature):
	"""Cross-reference a result against initial requirements."""

	requirements: str = dspy.InputField(desc="The expected outcome or constraints")
	result: str = dspy.InputField(desc="The actual output to validate")

	is_valid: bool = dspy.OutputField(desc="True if results meet requirements")
	feedback: str = dspy.OutputField(desc="Specific feedback if validation fails")

class RecomposeResults(dspy.Signature):
	"""Merge multiple sub-task outputs into a durable final report."""

	original_task: str = dspy.InputField(desc="The original high-level task")
	subtask_results: list[dict] = dspy.InputField(desc="List of {'task': str, 'result': Any} results")

	final_output: str = dspy.OutputField(desc="Lean and consolidated final output")
	durability_score: float = dspy.OutputField(desc="0.0 to 1.0 score of answer reliability")
