"""
_SUDOTEER Core Bootstrapper
Handles system initialization, agent registration, and environment setup.
"""

import logging
import asyncio
from backend.core.factory import agent_factory
from backend.core.dspy_config import initialize_dspy
from backend.core.memory.vector_db import initialize_vector_db
from backend.core.industrial_bridge import industrial_bridge
from backend.core.ui_bridge import ui_bridge
from backend.core.sudoteer_engine import sudoteer_engine

# Agent Imports
from backend.agents.supervisor import SupervisorAgent
from backend.agents.architect import ArchitectAgent
from backend.agents.coder import CoderAgent
from backend.agents.tester import TesterAgent
from backend.agents.documenter import DocumenterAgent
from backend.agents.validator import ValidatorAgent
from backend.agents.seeker import SeekerAgent
from backend.agents.climate import ClimateAgent
from backend.agents.nutrient import NutrientAgent
from backend.agents.crop import CropAgent
from backend.agents.financial.agent import FinancialAgent
from backend.agents.forensic.agent import ForensicAgent

logger = logging.getLogger("_SUDOTEER")

class SudoBootstrapper:
	"""Encapsulates all logic required to start the _SUDOTEER engine."""

	@staticmethod
	async def initialize_subsystems():
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

		# 4. Sudoteer Engine (The Heart)
		await sudoteer_engine.initialize()

		# 5. Industrial I/O (The Nervous System)
		await industrial_bridge.connect()

		# 5.1 MCP (Universal Tool Connectivity)
		try:
			from backend.core.mcp_manager import mcp_manager
			await mcp_manager.start_internal_server()
		except Exception as e:
			logger.warning(f"MCP Server failed to start: {e}")

		# 6. Constitution (Neo4j)
		try:
			from backend.core.memory.manager import memory_manager
			asyncio.create_task(SudoBootstrapper.setup_constitution(memory_manager))
		except Exception as e:
			logger.warning(f"Constitution setup deferred: {e}")

		logger.info("✓ All Subsystems online.")

	@staticmethod
	async def setup_constitution(manager):
		"""
		Initialize the Prime Directive, Persona, and Tool Breadcrumbs in Neo4j.
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
			if manager.graph_store:
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
				tools = ["FileWrite", "TerminalExec", "GitCommit"]
				for tool in tools:
					await manager.graph_store.create_relationship(
						f"Breadcrumb_{tool}", tool, "DESCRIBES",
						{"level": 1, "brief": f"Basic existence of {tool}."}
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
			"seeker": SeekerAgent,
			"climate": ClimateAgent,
			"nutrient": NutrientAgent,
			"crop": CropAgent,
			"financial": FinancialAgent,
			"forensic": ForensicAgent
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
			("seeker", "seeker_01"),
			("climate", "climate_01"),
			("nutrient", "nutrient_01"),
			("crop", "crop_01"),
			("financial", "financial_01"),
			("forensic", "forensic_01")
		]
		for role, agent_id in baseline_agents:
			agent = agent_factory.spawn_agent(role, agent_id)
			if hasattr(agent, "initialize"):
				await agent.initialize()

		logger.info("Baseline agency spawned and initialized.")
