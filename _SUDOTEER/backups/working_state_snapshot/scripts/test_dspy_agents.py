"""
DSPy Agent Structure Validation Suite.
Checks all 3 tiers of agents for proper DSPy integration.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_supervisor_dspy():
	"""Test Supervisor has DSPy modules."""
	print("\n[TEST] Testing Supervisor (Tier 1) DSPy Integration...")
	try:
		from backend.agents.supervisor import SupervisorAgent
		supervisor = SupervisorAgent("test_sup", "Supervisor")

		# Check DSPy modules exist
		checks = {
			'decomposer': hasattr(supervisor, 'decomposer'),
			'router': hasattr(supervisor, 'router'),
			'narrator': hasattr(supervisor, 'narrator')
		}

		for attr, ok in checks.items():
			print(f"  [{'OK' if ok else 'FAIL'}] {attr} module")

		return all(checks.values())
	except Exception as e:
		print(f"  [FAIL] Supervisor: Error - {e}")
		return False

def test_tier3_agents():
	"""Test Tier 3 Development Crew agents."""
	agents_to_test = [
		("Architect", "backend.agents.architect", "ArchitectAgent", "planner"),
		("Coder", "backend.agents.coder", "CoderAgent", "code_generator"),
		("Tester", "backend.agents.tester", "TesterAgent", "test_generator"),
		("Documenter", "backend.agents.documenter", "DocumenterAgent", "doc_generator"),
		("Validator", "backend.agents.validator", "ValidatorAgent", "auditor"),
	]

	results = {}
	print("\n[TEST] Testing Development Crew (Tier 3)...")

	for name, module_path, class_name, dspy_attr in agents_to_test:
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

def test_tier2_agents():
	"""Test Tier 2 Operational Crew agents."""
	agents_to_test = [
		("Climate", "backend.agents.climate", "ClimateAgent", "climate_analyzer"),
		("Nutrient", "backend.agents.nutrient", "NutrientAgent", "nutrient_analyzer"),
		("Crop", "backend.agents.crop", "CropAgent", "cycle_manager"),
	]

	results = {}
	print("\n[TEST] Testing Operational Crew (Tier 2)...")

	for name, module_path, class_name, dspy_attr in agents_to_test:
		try:
			module = __import__(module_path, fromlist=[class_name])
			AgentClass = getattr(module, class_name)
			agent = AgentClass(f"test_{name.lower()}", name)

			has_dspy = hasattr(agent, dspy_attr)
			if has_dspy:
				print(f"  [OK] {name}: DSPy operational")
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
	print("  _SUDOTEER AGENCY: DSPY VALIDATION SUITE")
	print("="*60)

	sup_ok = test_supervisor_dspy()
	t2_results = test_tier2_agents()
	t3_results = test_tier3_agents()

	# Summary
	print("\n" + "="*60)
	print("  FINAL SUMMARY")
	print("="*60)

	all_results = [sup_ok] + list(t2_results.values()) + list(t3_results.values())
	total_refactored = sum(all_results)
	total_agents = len(all_results)

	print(f"\n[AGENT STATUS] Online: {total_refactored}/{total_agents} agents")

	if total_refactored == total_agents:
		print("\n[SUCCESS] Entire agency is fully refactored with DSPy and ready for deployment!")
	else:
		print(f"\n[INFO] {total_agents - total_refactored} agents still pending DSPy integration.")

	print("\n" + "="*60)

if __name__ == "__main__":
	main()
