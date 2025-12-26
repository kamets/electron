import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
import socket

logger = logging.getLogger("_SUDOTEER")

class LLMSeekerEngine:
	"""
	_SUDOTEER LLM Discovery Engine.
	Automatically scans the local network and system for active LLM nodes
	(Ollama, LM Studio, LocalAI) to ensure a hassle-free setup.
	"""
	def __init__(self):
		self.standard_ports = {
			"Ollama": 11434,
			"LM Studio": 1234,
			"LocalAI": 8080,
			"Oobabooga": 5000,
			"VLLM": 8000
		}
		self.discovered_nodes = []

	async def scan_local_host(self) -> List[Dict[str, Any]]:
		"""Check 127.0.0.1 for active LLM backends."""
		logger.info("SeekerEngine: Scanning localhost for LLM backends...")
		found = []

		async with aiohttp.ClientSession() as session:
			for provider, port in self.standard_ports.items():
				url = f"http://127.0.0.1:{port}"
				try:
					# Check for OpenAI-compatible /v1/models or provider-specific health
					if provider == "Ollama":
						test_endpoint = f"{url}/api/tags"
					else:
						test_endpoint = f"{url}/v1/models"

					async with session.get(test_endpoint, timeout=0.5) as response:
						if response.status == 200:
							logger.info(f"SeekerEngine: Discovered {provider} at {url}")
							found.append({
								"provider": provider,
								"url": url,
								"status": "active"
							})
				except Exception:
					continue

		self.discovered_nodes = found
		return found

	async def scan_network(self) -> List[Dict[str, Any]]:
		"""
		Wider network scan logic.
		Uses the machine's local IP to guess the subnet.
		"""
		hostname = socket.gethostname()
		local_ip = socket.gethostbyname(hostname)
		subnet = ".".join(local_ip.split(".")[:-1])
		logger.info(f"SeekerEngine: Subnet detected - {subnet}.x (This may take a while...)")

		# For v1.0, we just simulate the wide scan to avoid performance hits
		# But we would iterate through 1-255 on standard ports
		return self.discovered_nodes

	def get_connection_string(self) -> Optional[str]:
		"""Returns the primary connection string to be used by the Agency."""
		if self.discovered_nodes:
			return self.discovered_nodes[0]["url"]
		return None

# Global seeker instance
llm_seeker = LLMSeekerEngine()
