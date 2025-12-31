import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.memory.vector_db import vector_db
from backend.core.memory.splitter import memory_splitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("_SUDOTEER_INGEST")

async def ingest_documentation_directory(docs_dir: str):
	logger.info(f"--- 📚 STARTING CORE DOCUMENTATION INGESTION: {docs_dir} ---")

	doc_path = Path(docs_dir)
	if not doc_path.exists():
		logger.error(f"Docs directory not found: {docs_dir}")
		return

	md_files = list(doc_path.rglob("*.md"))
	logger.info(f"Found {len(md_files)} markdown files for ingestion.")

	total_chunks = 0

	for md_file in md_files:
		logger.info(f"Processing: {md_file.relative_to(doc_path)}")

		try:
			with open(md_file, "r", encoding="utf-8") as f:
				content = f.read()

			if not content.strip():
				continue

			# Chunking via Protocol Alpha (200 tokens / 20 overlap)
			chunks = memory_splitter.chunk_text(content, protocol="alpha")

			metadatas = []
			for i, _ in enumerate(chunks):
				metadatas.append({
					"source": md_file.name,
					"rel_path": str(md_file.relative_to(doc_path.parent)),
					"chunk_index": i,
					"total_chunks": len(chunks),
					"category": "core_documentation",
					"ingested_at": datetime.now().isoformat()
				})

			# Committing to Vector DB
			await vector_db.add_to_knowledge(chunks, metadatas)
			total_chunks += len(chunks)
			logger.info(f"✓ Committed {len(chunks)} chunks from {md_file.name}")

		except Exception as e:
			logger.error(f"Error processing {md_file.name}: {e}")

	logger.info(f"--- ✅ INGESTION COMPLETE: {total_chunks} chunks added to Knowledge Collection ---")

if __name__ == "__main__":
	# Ingest current docs
	asyncio.run(ingest_documentation_directory("docs"))
