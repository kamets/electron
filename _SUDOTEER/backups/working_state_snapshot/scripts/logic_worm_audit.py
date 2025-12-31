import os
import sys
import time
import json
import asyncio
import logging
import importlib
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in path
sys.path.append(os.getcwd())

# _SUDOTEER Core Imports
from backend.core.bus import bus
from backend.core.protocol import A2AMessage
from backend.core.memory.manager import memory_manager
from backend.core.factory import agent_factory
from backend.core.boot import SudoBootstrapper

# Configure Audit Logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("LOGIC_WORM")

class LogicWorm:
	"""
	The Logic Worm: An exhaustive, recursive auditor for the _SUDOTEER codebase.
	Surges through Tier 1, 2, and 3 to find discontinuities and bottlenecks.
	"""
	def __init__(self):
		self.report = {
			"timestamp": time.time(),
			"tiers": {
				"1_platform": {"files": [], "tests": [], "status": "pending"},
				"2_intelligence": {"files": [], "tests": [], "status": "pending"},
				"3_agents": {"files": [], "tests": [], "status": "pending"}
			},
			"hotspots": [],
			"discontinuities": []
		}

	async def roll_call(self):
		"""Map every physical file to its logical Tier."""
		logger.info("🔍 Starting Roll Call...")

		# Tier 1: Core
		t1_path = Path("backend/core")
		self.report["tiers"]["1_platform"]["files"] = [str(f) for f in t1_path.glob("*.py")]

		# Tier 2: Memory
		t2_path = Path("backend/core/memory")
		self.report["tiers"]["2_intelligence"]["files"] = [str(f) for f in t2_path.glob("*.py")]

		# Tier 3: Agents
		t3_path = Path("backend/agents")
		self.report["tiers"]["3_agents"]["files"] = [str(f) for f in t3_path.rglob("agent.py")]

		logger.info(f"✓ Roll Call complete. Found {len(self.report['tiers']['1_platform']['files'])} Core files, {len(self.report['tiers']['2_intelligence']['files'])} Intelligence files, and {len(self.report['tiers']['3_agents']['files'])} Agent implementations.")

	async def audit_tier_1(self):
		"""Stress test the Platform layer (Bus, A2A, UIBridge)."""
		logger.info("🚀 Surging through Tier 1: Platform...")
		start_time = time.perf_counter()

		# Test 1: Bus Saturation
		try:
			logger.info("  Testing Bus Saturation (100 rapid A2A requests)...")
			tasks = []
			for i in range(100):
				msg = A2AMessage(from_agent="worm", to_agent="system", content=f"Burst test {i}")
				tasks.append(bus.publish("audit_burst", msg))
			await asyncio.gather(*tasks)
			self.report["tiers"]["1_platform"]["tests"].append({"name": "bus_saturation", "status": "passed"})
		except Exception as e:
			self.report["discontinuities"].append(f"Tier 1: Bus failure under load: {e}")

		elapsed = time.perf_counter() - start_time
		if elapsed > 1.0:
			self.report["hotspots"].append({"module": "Bus/IPC", "delta": elapsed, "note": "High latency under burst"})

	async def audit_tier_2(self):
		"""Recursively probe Memory and Reasoning heuristics."""
		logger.info("🧠 Surging through Tier 2: Intelligence...")

		# Test 2: Memory Splitter Edge Cases
		samples = [
			"", # Empty
			"X depends on Y" * 100, # Massive string
			"Tell me a story about a dragon", # Pure semantic
			"How is module A linked to module B?" # Pure relational
		]

		for i, sample in enumerate(samples):
			try:
				start = time.perf_counter()
				res = await memory_manager.recall(sample)
				delta = time.perf_counter() - start
				logger.info(f"  Memory recall test {i} took {delta:.4f}s")
				if delta > 2.0:
					self.report["hotspots"].append({"module": "MemorySplitter", "type": "latency", "input_size": len(sample)})
			except Exception as e:
				self.report["discontinuities"].append(f"Tier 2: Discontinuity in recall logic for sample {i}: {e}")

	async def audit_tier_3(self):
		"""Surge through Agents using the DVR logic."""
		logger.info("🤖 Surging through Tier 3: Agents...")

		# Boot subsystems for agent tests
		SudoBootstrapper.register_agency_roles()

		agent_roles = ["supervisor", "architect", "coder"]
		for role in agent_roles:
			try:
				logger.info(f"  Stress testing {role} agent...")
				start = time.perf_counter()
				agent = agent_factory.spawn_agent(role, f"worm_{role}")

				# Test Decompose logic
				tasks = await agent.decompose(f"Build a complex {role} module for high-throughput I/O")
				if not tasks or len(tasks) == 0:
					self.report["discontinuities"].append(f"Tier 3: {role} failed to decompose complex task.")

				delta = time.perf_counter() - start
				logger.info(f"  {role} DVR cycle took {delta:.4f}s")
			except Exception as e:
				self.report["discontinuities"].append(f"Tier 3: Error during {role} surge: {e}")

	def finalize(self):
		"""Save audit results to disk."""
		report_file = "docs/LOGIC_WORM_REPORT.md"
		with open(report_file, "w", encoding="utf-8") as f:
			f.write("# 📑 Logic Worm Audit Report\n\n")
			f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")

			f.write("## 🏗️ Hotspots (Bottlenecks)\n")
			if not self.report["hotspots"]: f.write("None detected. Lean status: Excellent.\n")
			for hs in self.report["hotspots"]:
				f.write(f"- **{hs.get('module')}**: {hs.get('delta', 'N/A')}s | {hs.get('note', '')}\n")

			f.write("\n## ⚠️ Discontinuities (Logic Gaps)\n")
			if not self.report["discontinuities"]: f.write("System logic is continuous. Durability: High.\n")
			for dc in self.report["discontinuities"]:
				f.write(f"- {dc}\n")

			f.write("\n## 📦 Tier Roll Call\n")
			for tier, data in self.report["tiers"].items():
				f.write(f"### {tier}\n")
				f.write(f"- **Files Scanned**: {len(data['files'])}\n")
				for file in data["files"]:
					f.write(f"  - `{file}`\n")

		logger.info(f"✨ Audit complete. View report at: {report_file}")

async def run_audit():
	# Initialize Subsystems (Crucial for Tier 2/3 logic)
	SudoBootstrapper.initialize_subsystems()

	worm = LogicWorm()
	await worm.roll_call()
	await worm.audit_tier_1()
	await worm.audit_tier_2()
	await worm.audit_tier_3()
	worm.finalize()

if __name__ == "__main__":
	from datetime import datetime
	asyncio.run(run_audit())
