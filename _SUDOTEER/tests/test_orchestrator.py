"""
TDD Test Suite: Agency Orchestrator
Tests workflow orchestration, budget enforcement, and agent coordination.
Grade Target: A (full coverage of workflow execution paths)
"""
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
from backend.core.orchestrator import AgencyOrchestrator


class TestOrchestratorInitialization:
	"""Test suite for orchestrator initialization."""

	def test_default_budget_limit(self):
		"""Verify default budget limit is set to 2 hours."""
		orch = AgencyOrchestrator()
		assert orch.budget_limit_hours == 2.0

	def test_custom_budget_limit(self):
		"""Verify custom budget limits are respected."""
		orch = AgencyOrchestrator(budget_limit_hours=5.0)
		assert orch.budget_limit_hours == 5.0

	def test_start_time_not_set_initially(self):
		"""Timer should not start until explicitly triggered."""
		orch = AgencyOrchestrator()
		assert orch.start_time is None


class TestTimerManagement:
	"""Test suite for timer and budget tracking."""

	def test_start_timer_sets_timestamp(self):
		"""start_timer should set a valid timestamp."""
		orch = AgencyOrchestrator()
		orch.start_timer()

		assert orch.start_time is not None
		assert orch.start_time <= time.time()

	def test_check_viability_before_timer_start(self):
		"""Viability should return True if timer hasn't started."""
		orch = AgencyOrchestrator()
		assert orch.check_viability() is True


class TestViabilityChecks:
	"""Test suite for ROI and budget enforcement."""

	@patch('backend.utils.finance.finance_tracker.is_stable', return_value=True)
	def test_viability_within_budget(self, mock_stable):
		"""Viability check should pass when within budget."""
		orch = AgencyOrchestrator(budget_limit_hours=2.0)
		orch.start_timer()

		# Immediately after start, should be viable
		assert orch.check_viability() is True

	@patch('backend.utils.finance.finance_tracker.is_stable', return_value=True)
	def test_viability_exceeds_budget(self, mock_stable):
		"""Viability check should fail when budget is exceeded."""
		orch = AgencyOrchestrator(budget_limit_hours=0.0001)  # ~0.36 seconds
		orch.start_time = time.time() - 3600  # Pretend 1 hour has passed

		assert orch.check_viability() is False

	@patch('backend.utils.finance.finance_tracker.is_stable', return_value=False)
	def test_viability_financial_instability(self, mock_stable):
		"""Viability check should fail when finances are unstable."""
		orch = AgencyOrchestrator()
		orch.start_timer()

		assert orch.check_viability() is False


class TestWorkflowSetup:
	"""Test suite for workflow configuration."""

	def test_default_workflows_registered(self):
		"""Default validation chain workflow should be registered."""
		with patch('backend.core.workflow.workflow_orchestrator.register_workflow') as mock_reg:
			orch = AgencyOrchestrator()
			mock_reg.assert_called_once()


class TestWorkflowExecution:
	"""Test suite for workflow execution (async)."""

	@pytest.mark.asyncio
	async def test_validation_chain_success_path(self):
		"""Test successful validation chain execution."""
		with patch('backend.core.orchestrator.workflow_orchestrator') as mock_wf, \
			 patch('backend.core.orchestrator.finance_tracker') as mock_fin:

			# Setup mocks
			mock_wf.execute_workflow = AsyncMock(return_value={
				"data": {"valid": True, "code": "test", "test_report": "pass", "docs": "done"}
			})
			mock_fin.is_stable.return_value = True
			mock_fin.get_summary_metrics.return_value = {}

			orch = AgencyOrchestrator()
			result = await orch.execute_validation_chain("Test goal")

			assert result is not None
			assert result.get("valid") is True

	@pytest.mark.asyncio
	async def test_validation_chain_failure_path(self):
		"""Test validation chain failure handling."""
		with patch('backend.core.orchestrator.workflow_orchestrator') as mock_wf, \
			 patch('backend.core.orchestrator.finance_tracker') as mock_fin:

			# Setup mocks - validation fails
			mock_wf.execute_workflow = AsyncMock(return_value={
				"data": {"valid": False}
			})
			mock_fin.is_stable.return_value = True
			mock_fin.get_summary_metrics.return_value = {}

			orch = AgencyOrchestrator()
			result = await orch.execute_validation_chain("Test goal")

			assert result is None


class TestAgentSteps:
	"""Test suite for individual agent step functions."""

	@pytest.mark.asyncio
	async def test_step_coder_integration(self):
		"""Test coder step calls the correct agent."""
		with patch('backend.core.orchestrator.bus') as mock_bus, \
			 patch('backend.core.orchestrator.ui_bridge') as mock_ui, \
			 patch('backend.core.orchestrator.finance_tracker') as mock_fin:

			mock_bus.send_request = AsyncMock(return_value={"status": "success"})
			mock_fin.is_stable.return_value = True

			orch = AgencyOrchestrator()
			orch.start_timer()

			state = {"data": {"goal": "Test task"}}
			result = await orch._step_coder(state)

			mock_bus.send_request.assert_awaited_once()

	@pytest.mark.asyncio
	async def test_step_tester_receives_code(self):
		"""Test tester step receives code from previous step."""
		with patch('backend.core.orchestrator.bus') as mock_bus, \
			 patch('backend.core.orchestrator.ui_bridge') as mock_ui, \
			 patch('backend.core.orchestrator.finance_tracker') as mock_fin:

			mock_bus.send_request = AsyncMock(return_value={"tests": "passed"})
			mock_fin.is_stable.return_value = True

			orch = AgencyOrchestrator()
			orch.start_timer()

			state = {"data": {"code": "def hello(): pass"}}
			result = await orch._step_tester(state)

			assert "test_report" in result["data"]

	@pytest.mark.asyncio
	async def test_step_documenter_receives_code_and_tests(self):
		"""Test documenter step receives code and test results."""
		with patch('backend.core.orchestrator.bus') as mock_bus, \
			 patch('backend.core.orchestrator.ui_bridge') as mock_ui, \
			 patch('backend.core.orchestrator.finance_tracker') as mock_fin:

			mock_bus.send_request = AsyncMock(return_value={"docs": "generated"})
			mock_fin.is_stable.return_value = True

			orch = AgencyOrchestrator()
			orch.start_timer()

			state = {"data": {"code": "def hello(): pass", "test_report": "passed"}}
			result = await orch._step_documenter(state)

			assert "docs" in result["data"]

	@pytest.mark.asyncio
	async def test_step_validator_receives_full_bundle(self):
		"""Test validator step receives complete artifact bundle."""
		with patch('backend.core.orchestrator.bus') as mock_bus, \
			 patch('backend.core.orchestrator.ui_bridge') as mock_ui, \
			 patch('backend.core.orchestrator.finance_tracker') as mock_fin:

			mock_bus.send_request = AsyncMock(return_value={"valid": True})
			mock_fin.is_stable.return_value = True

			orch = AgencyOrchestrator()
			orch.start_timer()

			state = {
				"data": {
					"code": "def hello(): pass",
					"test_report": "passed",
					"docs": "generated"
				}
			}
			result = await orch._step_validator(state)

			assert result["data"].get("valid") is True
