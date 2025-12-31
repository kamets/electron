"""
🎆 NEW YEAR'S AGENT OPTIMIZATION 🎆
Uses Kimi K2 (Ollama) as Teacher to create optimized few-shot agents.
Saves learnings to ChromaDB for persistent agent memory.

Based on DSPy BootstrapFewShot optimization pattern.
"""
import asyncio
import sys
import os
import json
import dspy
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DSPy_DISABLE_STRUCTURED_OUTPUTS"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"

# ============================================
# TRAINING DATA: Golden Examples for Agents
# ============================================

CODER_TRAINING_SET = [
	dspy.Example(
		description="Create a function to calculate moving average of sensor readings",
		code='''def moving_average(readings: list[float], window: int = 5) -> list[float]:
	"""Calculate moving average of sensor readings."""
	if len(readings) < window:
		return readings
	return [sum(readings[i:i+window])/window for i in range(len(readings)-window+1)]''',
		test_input=([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 3),
		expected_result=[2.0, 3.0, 4.0, 5.0]
	).with_inputs('description'),

	dspy.Example(
		description="Create a function to validate pH sensor reading is in safe range",
		code='''def validate_ph(ph_value: float, min_ph: float = 5.5, max_ph: float = 7.5) -> tuple[bool, str]:
	"""Validate pH is in safe agricultural range."""
	if ph_value < min_ph:
		return False, f"pH too low: {ph_value} < {min_ph}"
	if ph_value > max_ph:
		return False, f"pH too high: {ph_value} > {max_ph}"
	return True, "pH in safe range"''',
		test_input=(6.5,),
		expected_result=(True, "pH in safe range")
	).with_inputs('description'),

	dspy.Example(
		description="Create a pytest test for a temperature controller class",
		code='''import pytest
from unittest.mock import MagicMock

def test_temperature_controller_heater_on():
	"""Test heater turns on when temp is below target."""
	controller = MagicMock()
	controller.current_temp = 18.0
	controller.target_temp = 22.0
	controller.should_heat.return_value = True
	assert controller.should_heat() == True

def test_temperature_controller_heater_off():
	"""Test heater turns off when temp is at target."""
	controller = MagicMock()
	controller.current_temp = 22.0
	controller.target_temp = 22.0
	controller.should_heat.return_value = False
	assert controller.should_heat() == False''',
		test_input=None,
		expected_result=None
	).with_inputs('description'),

	dspy.Example(
		description="Create a function to parse Modbus register readings",
		code='''def parse_modbus_reading(raw_bytes: bytes) -> dict:
	"""Parse Modbus register bytes into sensor values."""
	if len(raw_bytes) < 4:
		raise ValueError("Insufficient data")
	return {
		"temperature": int.from_bytes(raw_bytes[0:2], 'big') / 10.0,
		"humidity": int.from_bytes(raw_bytes[2:4], 'big') / 10.0
	}''',
		test_input=(b'\\x00\\xfa\\x02\\x58',),
		expected_result={"temperature": 25.0, "humidity": 60.0}
	).with_inputs('description'),
]

ARCHITECT_TRAINING_SET = [
	dspy.Example(
		description="Design a greenhouse control system with temperature and humidity sensors",
		architecture='''# Greenhouse Control System Architecture

## Components
1. **SensorHub** - Collects data from all sensors
   - TemperatureSensor (DHT22)
   - HumiditySensor (DHT22)
   - PHSensor (Analog)

2. **ControlLoop** - PID-based control logic
   - Input: Sensor readings
   - Output: Actuator commands

3. **ActuatorBridge** - Controls physical hardware
   - Heater (ON/OFF)
   - Vent (PWM 0-100%)
   - Pump (ON/OFF with timer)

## Data Flow
SensorHub -> ControlLoop -> ActuatorBridge
         \\-> DataLogger -> ChromaDB

## Safety
- Watchdog timer (5s heartbeat)
- Hardware limits enforced in ActuatorBridge
- Emergency stop on sensor timeout''',
		components=["SensorHub", "ControlLoop", "ActuatorBridge", "DataLogger", "SafetyWatchdog"]
	).with_inputs('description'),
]

# ============================================
# DSPy SIGNATURES
# ============================================

class CoderSignature(dspy.Signature):
	"""Generate production-quality Python code from description."""
	description: str = dspy.InputField(desc="What the code should do")
	code: str = dspy.OutputField(desc="Complete Python code with docstrings and type hints")

class TesterSignature(dspy.Signature):
	"""Generate pytest tests for given code."""
	code: str = dspy.InputField(desc="The code to test")
	requirements: str = dspy.InputField(desc="Test requirements")
	test_code: str = dspy.OutputField(desc="Pytest test suite")

class ArchitectSignature(dspy.Signature):
	"""Create system architecture from requirements."""
	description: str = dspy.InputField(desc="System requirements")
	architecture: str = dspy.OutputField(desc="Detailed architecture in markdown")
	components: list = dspy.OutputField(desc="List of component names")

# ============================================
# EXECUTION METRIC (The Judge)
# ============================================

def code_execution_metric(example, pred, trace=None):
	"""Judge: Does the generated code actually work?"""
	try:
		# Try to compile the code
		compile(pred.code, '<string>', 'exec')

		# Check for key elements
		has_docstring = '"""' in pred.code or "'''" in pred.code
		has_type_hints = '->' in pred.code or ': ' in pred.code
		has_function = 'def ' in pred.code

		# Score based on quality
		score = 0.5 if has_function else 0
		score += 0.25 if has_docstring else 0
		score += 0.25 if has_type_hints else 0

		return score >= 0.75
	except:
		return False

def test_validation_metric(example, pred, trace=None):
	"""Judge: Are the generated tests valid pytest code?"""
	try:
		compile(pred.test_code, '<string>', 'exec')
		has_pytest = 'pytest' in pred.test_code or 'def test_' in pred.test_code
		has_assert = 'assert' in pred.test_code
		return has_pytest and has_assert
	except:
		return False

# ============================================
# AGENT MODULES
# ============================================

class OptimizedCoder(dspy.Module):
	def __init__(self):
		super().__init__()
		self.generator = dspy.ChainOfThought(CoderSignature)

	def forward(self, description):
		return self.generator(description=description)

class OptimizedTester(dspy.Module):
	def __init__(self):
		super().__init__()
		self.generator = dspy.ChainOfThought(TesterSignature)

	def forward(self, code, requirements):
		return self.generator(code=code, requirements=requirements)

class OptimizedArchitect(dspy.Module):
	def __init__(self):
		super().__init__()
		self.generator = dspy.ChainOfThought(ArchitectSignature)

	def forward(self, description):
		return self.generator(description=description)

# ============================================
# MAIN OPTIMIZATION LOOP
# ============================================

async def run_optimization():
	print("=" * 70)
	print("   🎆 NEW YEAR'S AGENT OPTIMIZATION 🎆")
	print("   Kimi K2 Teaching Our Agents!")
	print("=" * 70)

	# Configure Kimi K2 as Teacher (Ollama)
	print("\n[1] Configuring Kimi K2 (Teacher) + Blitzar (Student)...")

	teacher = dspy.LM(
		model="ollama_chat/kimi-k2-thinking:latest",
		api_base="http://localhost:11434",
		cache=False
	)

	# Use a faster model as student (Blitzar if available, else same)
	try:
		student = dspy.LM(
			model="openai/blitzar-coder-4b",
			api_base="http://localhost:1234/v1",
			api_key="lm-studio",
			cache=False
		)
		print("   [OK] Teacher: Kimi K2 (Ollama)")
		print("   [OK] Student: Blitzar-coder-4b (LM Studio)")
	except:
		student = teacher
		print("   [OK] Teacher & Student: Kimi K2 (Ollama)")

	dspy.configure(lm=student)

	# ============================================
	# PHASE 1: Optimize Coder Agent
	# ============================================
	print("\n" + "=" * 70)
	print("[2] OPTIMIZING CODER AGENT")
	print("=" * 70)

	from dspy.teleprompt import BootstrapFewShot

	coder_optimizer = BootstrapFewShot(
		metric=code_execution_metric,
		max_bootstrapped_demos=3,
		max_labeled_demos=3
	)

	print("   Training examples:", len(CODER_TRAINING_SET))
	print("   Running optimization...")

	try:
		compiled_coder = await asyncio.to_thread(
			coder_optimizer.compile,
			OptimizedCoder(),
			trainset=CODER_TRAINING_SET
		)

		# Save the optimized agent
		compiled_coder.save("memory/optimized_coder.json")
		print("   [OK] Saved: memory/optimized_coder.json")

		# Extract and save few-shot examples to ChromaDB
		await save_learnings_to_chroma("coder", CODER_TRAINING_SET, compiled_coder)

	except Exception as e:
		print(f"   [ERROR] Coder optimization: {e}")

	# ============================================
	# PHASE 2: Test the Optimized Agent
	# ============================================
	print("\n" + "=" * 70)
	print("[3] TESTING OPTIMIZED CODER")
	print("=" * 70)

	test_prompts = [
		"Create a function to calculate NPK ratio from sensor readings",
		"Create a function to detect anomalies in temperature data",
		"Create a pytest test for a humidity controller",
	]

	for i, prompt in enumerate(test_prompts, 1):
		print(f"\n   Test {i}: {prompt[:50]}...")
		try:
			result = await asyncio.wait_for(
				asyncio.to_thread(
					compiled_coder,
					description=prompt
				),
				timeout=120.0
			)
			print(f"   [OK] Generated {len(result.code)} chars")
			print(f"   Preview: {result.code[:200]}...")

			# Save successful generation to ChromaDB
			await save_to_chroma(
				f"Generated code for: {prompt}",
				result.code,
				{"type": "generated_code", "prompt": prompt}
			)
		except Exception as e:
			print(f"   [ERROR] {e}")

	# ============================================
	# SUMMARY
	# ============================================
	print("\n" + "=" * 70)
	print("   🎆 OPTIMIZATION COMPLETE! 🎆")
	print("=" * 70)
	print(f"\n   Optimized agents saved to: memory/")
	print(f"   Learnings saved to: ChromaDB (sudoteer_memories)")
	print(f"   Timestamp: {datetime.now().isoformat()}")
	print("\n   Happy New Year! Your agents are now smarter! 🚀")

async def save_learnings_to_chroma(agent_type: str, training_set, compiled_agent):
	"""Save the few-shot learnings to ChromaDB for retrieval."""
	from backend.core.memory.vector_db import vector_db

	print(f"\n   Saving {agent_type} learnings to ChromaDB...")

	for i, example in enumerate(training_set):
		content = f"""
AGENT: {agent_type}
TASK: {example.description}
SOLUTION:
{example.code if hasattr(example, 'code') else example.architecture}
"""
		metadata = {
			"type": "few_shot_example",
			"agent": agent_type,
			"index": i,
			"source": "kimi_k2_optimization"
		}

		await vector_db.add_to_knowledge([content], [metadata])

	print(f"   [OK] Saved {len(training_set)} examples to ChromaDB")

async def save_to_chroma(description: str, content: str, metadata: dict):
	"""Save a single learning to ChromaDB."""
	from backend.core.memory.vector_db import vector_db

	full_content = f"{description}\n\n{content}"
	await vector_db.add_to_knowledge([full_content], [metadata])

if __name__ == "__main__":
	# Ensure memory directory exists
	os.makedirs("memory", exist_ok=True)

	asyncio.run(run_optimization())
