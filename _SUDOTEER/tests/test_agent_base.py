"""
TDD Test Suite: BaseAgent and DVRModule
Tests core agent functionality, memory operations, and DVR reasoning.
Grade Target: A (full coverage of agent lifecycle)
"""
import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock


class TestDVRModuleInitialization:
	"""Test suite for DVRModule (Decompose-Validate-Recompose)."""

	def test_dvr_module_creation(self):
		"""DVRModule should initialize with role-specific configuration."""
		with patch('dspy.ChainOfThought') as mock_cot:
			from backend.core.agent_base import DVRModule

			dvr = DVRModule(role="tester")
			assert dvr.role == "tester"


class TestBaseAgentInitialization:
	"""Test suite for BaseAgent initialization."""

	def test_agent_id_and_role_set(self):
		"""Agent should store ID and role correctly."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'):
			from backend.core.agent_base import BaseAgent

			# Create concrete implementation
			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="test_01", role="tester")

			assert agent.agent_id == "test_01"
			assert agent.role == "tester"

	def test_workstation_path_created(self):
		"""Agent should create workstation directory on init."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs') as mock_makedirs:
			from backend.core.agent_base import BaseAgent

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="test_02", role="coder")

			mock_makedirs.assert_called_once()


class TestAgentLogging:
	"""Test suite for agent interaction logging."""

	def test_log_interaction_basic(self):
		"""log_interaction should record messages."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'):
			from backend.core.agent_base import BaseAgent

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="log_test", role="documenter")

			with patch.object(agent, 'remember', new_callable=AsyncMock) as mock_remember, \
				 patch('backend.core.monologue.recorder') as mock_recorder:
				agent.log_interaction("Test message", event_type="thought")
				# Should call recorder
				mock_recorder.record_event.assert_called_once()


class TestAgentMemoryOperations:
	"""Test suite for memory operations."""

	@pytest.mark.asyncio
	async def test_remember_calls_manager(self):
		"""remember() should delegate to HybridMemoryManager."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'), \
			 patch('backend.core.memory.manager.memory_manager') as mock_manager:
			from backend.core.agent_base import BaseAgent

			mock_manager.remember = AsyncMock(return_value={"memory_id": "mem_123"})

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="mem_test", role="seeker")
			result = await agent.remember("Test content")

			mock_manager.remember.assert_awaited_once()

	@pytest.mark.asyncio
	async def test_recall_returns_context(self):
		"""recall() should return semantic and relational context."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'), \
			 patch('backend.core.memory.manager.memory_manager') as mock_manager:
			from backend.core.agent_base import BaseAgent

			mock_manager.recall = AsyncMock(return_value={
				"mode": "hybrid",
				"semantic_context": [{"content": "fact"}]
			})

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="recall_test", role="architect")
			result = await agent.recall("How is X configured?")

			assert result["mode"] == "hybrid"

	@pytest.mark.asyncio
	async def test_get_context_returns_sandwich(self):
		"""get_context() should return formatted context sandwich."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'), \
			 patch('backend.core.memory.manager.memory_manager') as mock_manager:
			from backend.core.agent_base import BaseAgent

			mock_manager.get_context_sandwich = AsyncMock(return_value="Context Sandwich Content")

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="ctx_test", role="supervisor")
			result = await agent.get_context("Query text")

			assert "Context" in result


class TestAgentXPSystem:
	"""Test suite for gamification/XP system."""

	def test_gain_xp_calls_engine(self):
		"""gain_xp() should delegate to matryoshka_engine."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'), \
			 patch('backend.core.gamification.matryoshka_engine') as mock_gamification:
			from backend.core.agent_base import BaseAgent

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="xp_test", role="validator")

			with patch.object(agent, 'log_interaction'):
				agent.gain_xp(100, "Test achievement")

			mock_gamification.add_xp.assert_called_with("xp_test", 100)


class TestAgentDVROperations:
	"""Test suite for DVR (Decompose-Validate-Recompose) operations."""

	@pytest.mark.asyncio
	async def test_decompose_returns_subtasks(self):
		"""decompose() should return list of subtasks."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'), \
			 patch('asyncio.to_thread') as mock_to_thread:
			from backend.core.agent_base import BaseAgent

			mock_result = MagicMock()
			mock_result.subtasks = ["Step 1", "Step 2", "Step 3"]
			mock_to_thread.return_value = mock_result

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="dvr_test", role="coder")

			with patch.object(agent, 'get_context', new_callable=AsyncMock, return_value="context"):
				result = await agent.decompose("Complex task")

			assert len(result) == 3

	@pytest.mark.asyncio
	async def test_validate_returns_boolean(self):
		"""validate() should return True/False based on validation."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'), \
			 patch('asyncio.to_thread') as mock_to_thread:
			from backend.core.agent_base import BaseAgent

			mock_result = MagicMock()
			mock_result.is_valid = True
			mock_result.feedback = "Looks good"
			mock_to_thread.return_value = mock_result

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="validate_test", role="validator")
			result = await agent.validate("Requirements", "Result")

			assert result is True


class TestAgentA2ACommunication:
	"""Test suite for agent-to-agent communication."""

	@pytest.mark.asyncio
	async def test_send_a2a_uses_bus(self):
		"""send_a2a() should use bus to send messages."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'), \
			 patch('backend.core.bus.bus') as mock_bus:
			from backend.core.agent_base import BaseAgent

			mock_bus.send_request = AsyncMock(return_value={"status": "received"})

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="a2a_sender", role="coder")
			result = await agent.send_a2a("a2a_receiver", {"task": "help"})

			mock_bus.send_request.assert_awaited_once()


class TestAgentWisdomAssimilation:
	"""Test suite for wisdom assimilation (self-reflection)."""

	@pytest.mark.asyncio
	async def test_assimilate_wisdom_triggers_reflection(self):
		"""assimilate_wisdom() should trigger memory consolidation."""
		with patch('dspy.ChainOfThought'), \
			 patch('backend.core.agent_base.DVRModule'), \
			 patch('os.makedirs'), \
			 patch('backend.core.memory.manager.memory_manager') as mock_manager, \
			 patch('backend.core.gamification.matryoshka_engine'):
			from backend.core.agent_base import BaseAgent

			mock_manager.sifter_session_end = AsyncMock()

			class TestAgent(BaseAgent):
				async def handle_request(self, message):
					return "handled"
				async def forward(self, *args, **kwargs):
					return "forwarded"

			agent = TestAgent(agent_id="wisdom_test", role="architect")

			with patch.object(agent, 'log_interaction'), \
				 patch.object(agent, 'gain_xp'):
				await agent.assimilate_wisdom()

			mock_manager.sifter_session_end.assert_awaited_once()
