"""
Demo: Task Queue & Handoff System
Shows how long-running agents use TODO list and handoffs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.memory.task_queue import TaskQueue, Task, TaskStatus, TaskPriority

def demo_long_running_workflow():
	"""
	Simulate a long-running multi-agent workflow with handoffs.

	Scenario: Building a validation chain feature across multiple agents
	"""
	print("\n" + "="*70)
	print("DEMO: Long-Running Agent Workflow with Task Handoffs")
	print("="*70 + "\n")

	# Initialize task queue
	queue = TaskQueue(workspace_dir=".")

	# ============================================
	# Step 1: Architect creates TODO list
	# ============================================
	print("📋 STEP 1: ArchitectAgent creates TODO list\n")

	queue.add_task(
		task_id="feat_001_base_validator",
		description="Create BaseValidator class with input validation",
		category="functional",
		priority=TaskPriority.CRITICAL,
		steps=[
			"Create backend/agents/validator/base.py",
			"Implement validate() method",
			"Add error handling for null/empty inputs",
			"Write 10 unit tests"
		],
		test_command="pytest tests/test_base_validator.py"
	)

	queue.add_task(
		task_id="feat_002_compliance_checks",
		description="Add compliance checking logic",
		category="functional",
		priority=TaskPriority.HIGH,
		steps=[
			"Implement check_compliance() method",
			"Add configurable rulesets",
			"Test against sample data",
			"Achieve 95%+ coverage"
		],
		test_command="pytest tests/test_compliance.py"
	)

	queue.add_task(
		task_id="feat_003_ui_integration",
		description="Connect validator to UI",
		category="functional",
		priority=TaskPriority.MEDIUM,
		steps=[
			"Add validation button to UI",
			"Wire up websocket events",
			"Show validation results in panel",
			"E2E test with Playwright"
		],
		test_command="pytest tests/e2e/test_validator_ui.py"
	)

	queue.print_queue()

	# ============================================
	# Step 2: CoderAgent picks first task
	# ============================================
	print("💻 STEP 2: CoderAgent starts work\n")

	task1 = queue.get_next_task(agent_id="coder_01")
	print(f"Got task: {task1.id} - {task1.description}")

	# Mark as in progress
	queue.update_task(
		task_id=task1.id,
		status=TaskStatus.IN_PROGRESS,
		assigned_to="coder_01"
	)

	print("Status: IN_PROGRESS")
	print("Working... (simulated)\n")

	# Simulate partial completion (IMPRESSIVE!)
	queue.update_task(
		task_id=task1.id,
		tests_passing=9,  # A- grade!
		tests_total=10,
		agent_notes="Implemented BaseValidator class with comprehensive error handling. "
					"9/10 tests passing. One edge case for concurrent access still needs work."
	)

	# ============================================
	# Step 3: Coder hands off to Tester
	# ============================================
	print("🔄 STEP 3: CoderAgent hands off to TesterAgent\n")

	queue.create_handoff(
		from_agent="coder_01",
		to_agent="tester_01",
		current_task=queue.get_task(task1.id),
		context="Validation chain implementation in progress. "
				"Need help debugging edge case test failures.",
		continue_from="backend/agents/validator/base.py:L42"
	)

	print("Handoff created! Content:")
	print("-" * 70)
	print(queue.read_handoff())
	print("-" * 70 + "\n")

	# ============================================
	# Step 4: TesterAgent resumes work
	# ============================================
	print("🧪 STEP 4: TesterAgent resumes from handoff\n")

	# Tester reads handoff
	handoff = queue.read_handoff()
	print("TesterAgent read handoff notes:")
	print(f"  - Task: {task1.id}")
	print(f"  - Tests: {task1.tests_passing}/{task1.tests_total} passing")
	print(f"  - Continue from: backend/agents/validator/base.py:L42")
	print()

	# Tester gets the same task (resume logic)
	resumed_task = queue.get_next_task(agent_id="coder_01")  # Will return in-progress task
	print(f"Resumed task: {resumed_task.id}")
	print("Working on edge cases... (simulated)\n")

	# Tester fixes the tests
	queue.update_task(
		task_id=task1.id,
		status=TaskStatus.COMPLETED,
		passes=True,
		tests_passing=10,
		tests_total=10,
		agent_notes="Fixed edge case handling. All 10 tests now passing. ✅"
	)

	print("✅ Task completed!\n")

	# ============================================
	# Step 5: Next agent picks up next task
	# ============================================
	print("🔄 STEP 5: Next task automatically picked up\n")

	task2 = queue.get_next_task(agent_id="coder_02")
	print(f"Got next task: {task2.id} - {task2.description}")
	print(f"Priority: {task2.priority.value}")
	print()

	# ============================================
	# Step 6: Show final queue state
	# ============================================
	print("📊 STEP 6: Final Queue Status\n")
	queue.print_queue()

	summary = queue.get_progress_summary()
	print(f"Overall Progress: {summary['completion_percentage']:.1f}% complete")
	print(f"  - Completed: {summary['completed']}/{summary['total_tasks']}")
	print(f"  - In Progress: {summary['in_progress']}")
	print(f"  - Not Started: {summary['not_started']}")

	print("\n" + "="*70)
	print("✅ DEMO COMPLETE - Check task_queue.json and agent_handoff.txt")
	print("="*70 + "\n")

if __name__ == "__main__":
	demo_long_running_workflow()
