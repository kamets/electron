import pytest
from unittest.mock import MagicMock, patch
from backend.core.memory.splitter import MemorySplitter

@pytest.mark.asyncio
async def test_sift_query_relational():
	"""
	TDD: Test that 'sift_query' identifies relational queries correctly.
	"""
	with patch('dspy.ChainOfThought') as mock_cot:
		# Setup mock instance
		mock_sifter_instance = MagicMock()
		mock_cot.return_value = mock_sifter_instance

		# Set return value for the call
		mock_response = MagicMock()
		mock_response.strategy = "Relational Strategy"
		mock_sifter_instance.return_value = mock_response

		splitter = MemorySplitter()
		query = "How is Agent A connected to Agent B?"

		strategy = await splitter.sift_query(query)

		assert strategy == "relational"
		mock_sifter_instance.assert_called_once()

@pytest.mark.asyncio
async def test_sift_query_hybrid():
	"""
	TDD: Test that 'sift_query' identifies hybrid queries.
	"""
	with patch('dspy.ChainOfThought') as mock_cot:
		mock_sifter_instance = MagicMock()
		mock_cot.return_value = mock_sifter_instance

		mock_response = MagicMock()
		mock_response.strategy = "Hybrid search required"
		mock_sifter_instance.return_value = mock_response

		splitter = MemorySplitter()
		query = "Find all emails and how they relate to the project plan."

		strategy = await splitter.sift_query(query)

		assert strategy == "hybrid"

@pytest.mark.asyncio
async def test_split_storage_logic():
	"""
	TDD: Test that 'split_storage' returns the expected structured dictionary.
	"""
	with patch('dspy.ChainOfThought') as mock_cot:
		mock_splitter_instance = MagicMock()
		mock_cot.return_value = mock_splitter_instance

		mock_response = MagicMock()
		mock_response.routing = "BOTH"
		mock_response.semantic_summary = "Summary of data"
		mock_response.entities = ["Entity A", "Entity B"]
		mock_response.relationships = [{"from": "A", "to": "B", "type": "LINK"}]
		mock_response.reasoning = "Test reasoning"
		mock_splitter_instance.return_value = mock_response

		splitter = MemorySplitter()
		data = "A is linked to B."

		result = await splitter.split_storage(data)

		assert result["routing"] == "both"
		assert "entities" in result
		assert len(result["relationships"]) == 1
		assert result["relationships"][0]["type"] == "LINK"

@pytest.mark.asyncio
async def test_split_storage_with_facts():
	"""
	TDD: Test that 'split_storage' extracts 'facts' as key-value pairs.
	"""
	with patch('dspy.ChainOfThought') as mock_cot:
		mock_splitter_instance = MagicMock()
		mock_cot.return_value = mock_splitter_instance

		mock_response = MagicMock()
		mock_response.routing = "graph"
		mock_response.semantic_summary = "Observation"
		mock_response.entities = ["Sensor X"]
		mock_response.relationships = []
		mock_response.facts = [{"key": "status", "value": "online"}, {"key": "battery", "value": "85%"}]
		mock_response.reasoning = "Extracting sensor status"
		mock_splitter_instance.return_value = mock_response

		splitter = MemorySplitter()
		data = "Sensor X is online and its battery is 85%."

		result = await splitter.split_storage(data)

		assert "facts" in result
		assert len(result["facts"]) == 2
		assert result["facts"][0]["key"] == "status"
