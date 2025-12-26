"""
_SUDOTEER Core Bootstrapper
Handles system initialization, agent registration, and environment setup.
"""

import logging
from backend.core.factory import agent_factory
from backend.core.dspy_config import initialize_dspy
from backend.core.memory.vector_db import initialize_vector_db
from backend.core.industrial_bridge import industrial_bridge
from backend.core.ui_bridge import ui_bridge

# Agent Imports
from backend.agents.supervisor import SupervisorAgent
from backend.agents.architect import ArchitectAgent
from backend.agents.coder import CoderAgent
from backend.agents.tester import TesterAgent
from backend.agents.documenter import DocumenterAgent
from backend.agents.validator import ValidatorAgent
from backend.agents.seeker import SeekerAgent

logger = logging.getLogger("_SUDOTEER")

class SudoBootstrapper:
	"""Encapsulates all logic required to start the _SUDOTEER engine."""

	@staticmethod
	def initialize_subsystems():
		"""Initialize all core backend subsystems."""
		logger.info("Initializing _SUDOTEER Subsystems...")

		# 1. DSPy
		if not initialize_dspy(auto=True):
			logger.error("DSPy initialization failed!")

		# 2. Vector DB
		if not initialize_vector_db(backend="auto"):
			logger.warning("Vector DB initialization failed.")

		# 3. UI Bridge
		ui_bridge.start_heartbeat(interval_seconds=2.0)

		# 4. Constitution (Neo4j)
		try:
			from backend.core.memory.manager import memory_manager
			import asyncio
			asyncio.create_task(SudoBootstrapper.setup_constitution(memory_manager))
		except Exception as e:
			logger.warning(f"Constitution setup deferred: {e}")

		logger.info("Subsystems online.")

	@staticmethod
	async def setup_constitution(manager):
		"""
		Initialize the Prime Directive, Persona, and Tool Breadcrumbs in Neo4j.
		HANDBOOK: Phase 1 - Foundation.
		"""
		# 1. Core Tenets
		tenets = [
			"Do not assume user intent if the prompt is ambiguous.",
			"Preserve existing user data above all else.",
			"Ask for clarification rather than guessing on destructive actions."
		]

		# 2. Persona: Jaxon
		persona = {
			"name": "Jaxon",
			"style": "Technical, precise, slightly cynical but highly efficient hunter of bugs.",
			"catchphrase": "Let's find the ghost in the machine."
		}

		try:
			# Link Constitution to Agency
			await manager.graph_store.create_relationship(
				"Constitution", "Agency", "GOVERNS",
				{"id": "core_values", "tenets": tenets}
			)

			# Link Persona to Agency
			await manager.graph_store.create_relationship(
				"Persona", "Agency", "ADOPTS",
				persona
			)

			# 3. Tool Breadcrumbs (Fog of War Foundation)
			# Tiered DocChunks: Breadcrumb -> Basic -> Advanced
			tools = ["FileWrite", "TerminalExec", "GitCommit"]
			for tool in tools:
				# Breadcrumb node (Level 1)
				await manager.graph_store.create_relationship(
					f"Breadcrumb_{tool}", tool, "DESCRIBES",
					{"level": 1, "brief": f"Basic existence of {tool}. Access /docs/{tool}.md to unlock."}
				)
				# Basic node (Level 3)
				await manager.graph_store.create_relationship(
					f"Basic_{tool}", f"Breadcrumb_{tool}", "EXTENDS",
					{"level": 3, "brief": f"Standard usage patterns for {tool}."}
				)

			logger.info("✓ Foundation (Tenets, Jaxon, Breadcrumbs) established in Graph.")
		except Exception as e:
			logger.error(f"Failed to setup foundation in Graph: {e}")

	@staticmethod
	def register_agency_roles():
		"""Register all available agent roles in the factory."""
		roles = {
			"supervisor": SupervisorAgent,
			"architect": ArchitectAgent,
			"coder": CoderAgent,
			"tester": TesterAgent,
			"documenter": DocumenterAgent,
			"validator": ValidatorAgent,
			"seeker": SeekerAgent
		}
		for role, agent_class in roles.items():
			agent_factory.register_role(role, agent_class)
		logger.info(f"Agency roles registered: {list(roles.keys())}")

	@staticmethod
	async def spawn_baseline_agents():
		"""Spawn the initial set of agents required for session operation."""
		baseline_agents = [
			("supervisor", "supervisor_01"),
			("architect", "architect_01"),
			("coder", "coder_01"),
			("tester", "tester_01"),
			("documenter", "documenter_01"),
			("validator", "validator_01"),
			("seeker", "seeker_01")
		]
		for role, agent_id in baseline_agents:
			agent_factory.spawn_agent(role, agent_id)
		logger.info("Baseline agency spawned.")

	@staticmethod
	async def connect_industrial_io():
		"""Establish connections to industrial hardware/bridges."""
		await industrial_bridge.connect()
		logger.info("Industrial bridge connected.")
