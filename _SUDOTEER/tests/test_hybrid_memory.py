import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from backend.core.memory.manager import HybridMemoryManager

@pytest.fixture
def mock_stores():
	with patch('backend.core.memory.manager.vector_db') as mock_vdb, \
		 patch('backend.core.memory.manager.Neo4jGraphStore') as mock_graph_cls, \
		 patch('backend.core.memory.manager.memory_splitter') as mock_splitter:

		# Mock graph store instance
		mock_graph = MagicMock()
		mock_graph.create_relationship = AsyncMock()
		mock_graph.find_subgraph = AsyncMock(return_value={})
		mock_graph_cls.return_value = mock_graph

		# Mock vector db - use AsyncMock for all async methods
		mock_vdb.store_memory = AsyncMock(return_value="mem_123")
		mock_vdb.search_memories = AsyncMock(return_value=[{"content": "similar info"}])
		mock_vdb.search_knowledge = AsyncMock(return_value=[{"content": "knowledge", "metadata": {}}])
		mock_vdb.search_episodes = AsyncMock(return_value=[{"content": "episode", "metadata": {}}])

		# Mock splitter
		mock_splitter.split_storage = AsyncMock(return_value={
			"routing": "both",
			"semantic_summary": "Clean summary",
			"reasoning": "Split reasoning",
			"relationships": [{"from": "src", "to": "dst", "type": "LINK"}]
		})
		mock_splitter.sift_query = AsyncMock(return_value="hybrid")

		yield {
			"vdb": mock_vdb,
			"graph": mock_graph,
			"splitter": mock_splitter
		}

@pytest.mark.asyncio
async def test_remember_both(mock_stores):
	"""
	Test that 'remember' calls both vector and graph stores when routing is 'both'.
	"""
	manager = HybridMemoryManager()

	result = await manager.remember(
		agent_id="test_agent",
		data="A depends on B."
	)

	assert result["memory_id"] == "mem_123"
	assert result["graph_synced"] is True

	mock_stores["vdb"].store_memory.assert_awaited_once()
	mock_stores["graph"].create_relationship.assert_awaited_once()

@pytest.mark.asyncio
async def test_recall_automatic_mode(mock_stores):
	"""
	Test that 'recall' correctly uses the splitter to determine mode.
	"""
	manager = HybridMemoryManager()

	query = "How is the system configured?"
	results = await manager.recall(query)

	assert results["mode"] == "hybrid"
	assert len(results["semantic_context"]) > 0
	mock_stores["splitter"].sift_query.assert_awaited_once_with(query)
	mock_stores["vdb"].search_knowledge.assert_awaited_once()
	mock_stores["graph"].find_subgraph.assert_awaited_once()
