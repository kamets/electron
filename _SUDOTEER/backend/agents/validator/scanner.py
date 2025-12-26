import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger("_SUDOTEER")

class SecurityScanner:
	"""
	_SUDOTEER Security Scanner.
	Uses patterns from OWASP and Bandit to identify vulnerabilities.
	"""
	def __init__(self):
		self.vuln_patterns = [
			(r"eval\(", "Critical: Use of eval() is a high-risk security vulnerability."),
			(r"exec\(", "Critical: Use of exec() is a high-risk security vulnerability."),
			(r"os\.system\(", "High: os.system() is prone to shell injection."),
			(r"pickle\.load", "High: Unsafe deserialization with pickle."),
			(r"input\(", "Medium: Unvalidated user input via input().")
		]

	def scan(self, code: str) -> List[Dict[str, Any]]:
		"""Scan code for security vulnerabilities."""
		findings = []
		for pattern, message in self.vuln_patterns:
			matches = re.finditer(pattern, code)
			for match in matches:
				line_num = code[:match.start()].count('\n') + 1
				findings.append({
					"type": "security",
					"line": line_num,
					"message": message,
					"severity": message.split(':')[0]
				})
		return findings
