"""
Quick DSPy agent structure validation.
Non-async test to check DSPy integration.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_supervisor_dspy():
	"""Test Supervisor has DSPy modules."""
	print("\n[TEST] Testing Supervisor DSPy Integration...")

	from backend.agents.supervisor import SupervisorAgent
	supervisor = SupervisorAgent("test_sup", "Supervisor")

	# Check DSPy modules exist
	assert hasattr(supervisor, 'decomposer'), "ERROR: Missing decomposer"
	assert hasattr(supervisor, 'router'), "ERROR: Missing router"
	assert hasattr(supervisor, 'narrator'), "ERROR: Missing narrator"

	print("  [OK] decomposer module")
	print("  [OK] router module")
	print("  [OK] narrator module")
	print("  [PASS] Supervisor")
	return True

def test_architect_structure():
	"""Test Architect agent structure."""
	print("\n[TEST] Testing Architect...")

	try:
		from backend.agents.architect import ArchitectAgent
		architect = ArchitectAgent("test_arch", "Architect")

		has_planner = hasattr(architect, 'planner')
		if has_planner:
			print("  [OK] Architect: DSPy refactored")
			return True
		else:
			print("  [WARN] Architect: NOT YET refactored")
			return False
	except Exception as e:
		print(f"  [FAIL] Architect: Error - {e}")
		return False

def test_remaining_agents():
	"""Test remaining Tier 3 agents."""
	agents_to_test = [
		("Coder", "backend.agents.coder", "CoderAgent", "code_generator"),
		("Tester", "backend.agents.tester", "TesterAgent", "test_generator"),
		("Documenter", "backend.agents.documenter", "DocumenterAgent", "doc_generator"),
		("Validator", "backend.agents.validator", "ValidatorAgent", "auditor"),
	]

	results = {}

	for name, module_path, class_name, dspy_attr in agents_to_test:
		print(f"\n[TEST] Testing {name}...")
		try:
			module = __import__(module_path, fromlist=[class_name])
			AgentClass = getattr(module, class_name)
			agent = AgentClass(f"test_{name.lower()}", name)

			has_dspy = hasattr(agent, dspy_attr)
			if has_dspy:
				print(f"  [OK] {name}: DSPy refactored")
				results[name] = True
			else:
				print(f"  [WARN] {name}: NOT YET refactored")
				results[name] = False

		except Exception as e:
			print(f"  [FAIL] {name}: Error - {e}")
			results[name] = False

	return results

def main():
	print("="*60)
	print("  DSPY AGENT VALIDATION")
	print("="*60)

	# Test refactored agent
	supervisor_ok = test_supervisor_dspy()

	# Test not-yet-refactored agents
	architect_ok = test_architect_structure()
	remaining = test_remaining_agents()

	# Summary
	print("\n" + "="*60)
	print("  SUMMARY")
	print("="*60)

	total_refactored = sum([supervisor_ok, architect_ok] + list(remaining.values()))
	total_agents = 6  # Supervisor + 5 Tier 3 agents

	print(f"\n[OK] Refactored: {total_refactored}/{total_agents} agents")
	print(f"[WARN] Remaining:  {total_agents - total_refactored}/{total_agents} agents")

	if supervisor_ok:
		print("\n[SUCCESS] Supervisor (Tier 1) is fully DSPy-refactored and ready!")

	print("\n" + "="*60)

if __name__ == "__main__":
	main()
