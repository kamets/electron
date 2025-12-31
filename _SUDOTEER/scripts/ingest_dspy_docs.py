"""
Ingest DSPy documentation into vector memory for agent learning.
This seeds the knowledge base with architectural patterns.
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.memory.vector_db import vector_db

DSPY_DOCS_DIR = Path("docs/DSpy")

async def ingest_dspy_docs():
	print("[INGEST] DSPy Documentation -> Vector Memory")
	print("=" * 50)

	if not DSPY_DOCS_DIR.exists():
		print(f"   [ERROR] {DSPY_DOCS_DIR} not found")
		return

	doc_files = list(DSPY_DOCS_DIR.glob("*.md"))
	print(f"   Found {len(doc_files)} documentation files")

	chunks = []
	metadatas = []

	for doc_path in doc_files:
		try:
			content = doc_path.read_text(encoding="utf-8")

			# Skip very short files
			if len(content) < 100:
				continue

			# Create chunks from content (simple paragraph split)
			paragraphs = content.split("\n\n")

			for i, para in enumerate(paragraphs):
				if len(para.strip()) > 50:  # Skip tiny paragraphs
					chunks.append(para.strip()[:1000])  # Limit chunk size
					metadatas.append({
						"type": "dspy_documentation",
						"source_file": doc_path.name,
						"chunk_index": i,
						"source": "dspy_docs"
					})

			print(f"   [OK] {doc_path.name}: {len(paragraphs)} paragraphs")

		except Exception as e:
			print(f"   [WARN] {doc_path.name}: {e}")

	if chunks:
		print(f"\n   Ingesting {len(chunks)} chunks into knowledge base...")
		await vector_db.add_to_knowledge(chunks, metadatas)
		print("   [OK] Ingestion complete!")

	# Test search
	print("\n[TEST] Searching for 'Context Sandwich'...")
	results = await vector_db.search_knowledge("Context Sandwich episodic memory", top_k=3)

	if results:
		print(f"   Found {len(results)} results:")
		for r in results:
			preview = r['content'][:100].replace('\n', ' ')
			print(f"   - {preview}...")
	else:
		print("   No results found")

	print("\n" + "=" * 50)
	print("[DONE] DSPy docs ingested for agent learning!")

if __name__ == "__main__":
	asyncio.run(ingest_dspy_docs())
