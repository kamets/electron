import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger("_SUDOTEER")

class FinancialTracker:
	"""
	Advanced Financial Intelligence Engine.
	Tracks 'Money In / Money Out', Token Usage, and Operational Effectiveness.
	"""
	def __init__(self):
		self.ledger: List[Dict[str, Any]] = []
		self.total_in = 0.0
		self.total_out = 0.0

		# Token Metrics
		self.tokens = {
			"prompt": 0,
			"completion": 0,
			"total": 0,
			"estimated_cost": 0.0
		}

		# Effectiveness Metrics
		self.effectiveness = {
			"total_tasks": 0,
			"first_time_pass": 0,
			"second_time_pass": 0,
			"failures": 0
		}

		# Utilization Metrics
		self.utilization: Dict[str, int] = {} # AgentID -> Call Count

	def log_tokens(self, prompt: int, completion: int, model: str = "gpt-4o-mini"):
		"""Record token usage and estimated costs."""
		self.tokens["prompt"] += prompt
		self.tokens["completion"] += completion
		self.tokens["total"] += (prompt + completion)

		# Mock cost logic (0.15 / 1M input, 0.60 / 1M output)
		cost = (prompt * 0.00000015) + (completion * 0.0000006)
		self.tokens["estimated_cost"] += cost
		self.log_transaction(-cost, "token_cost", f"Tokens for {model}")

	def log_effectiveness(self, task_id: str, attempts: int, success: bool):
		"""Track how many attempts were needed for a task."""
		self.effectiveness["total_tasks"] += 1
		if success:
			if attempts == 1:
				self.effectiveness["first_time_pass"] += 1
			elif attempts == 2:
				self.effectiveness["second_time_pass"] += 1
		else:
			self.effectiveness["failures"] += 1

	def log_utilization(self, agent_id: str):
		"""Track which agents are being utilized most."""
		self.utilization[agent_id] = self.utilization.get(agent_id, 0) + 1

	def log_transaction(self, amount: float, category: str, description: str):
		"""Log a financial event."""
		transaction = {
			"timestamp": datetime.now().isoformat(),
			"amount": amount,
			"category": category,
			"description": description
		}
		self.ledger.append(transaction)

		if amount > 0:
			self.total_in += amount
		else:
			self.total_out += abs(amount)

		logger.info(f"Financial Event: {category} | {amount} | {description}")

	def get_project_health(self) -> Dict[str, Any]:
		"""Calculate the work-to-spend ratio and overall system health."""
		total_tasks = self.effectiveness["total_tasks"]
		total_spent = self.total_out

		# Work vs Spend Efficiency
		# Assuming each successful task is 'valuable'.
		work_efficiency = (total_tasks * 10.0) / max(0.1, total_spent) # Arbitrary value score

		return {
			"health_score": f"{min(100, work_efficiency * 100):.1f}%",
			"efficiency_ratio": f"{work_efficiency:.2f} tasks/$",
			"first_pass_yield": f"{(self.effectiveness['first_time_pass'] / max(1, total_tasks)):.1%}",
			"token_efficiency": f"{(self.tokens['total'] / max(1, total_tasks)):.0f} tokens/task"
		}

	def get_summary_metrics(self) -> Dict[str, Any]:
		"""Return a high-level overview of efficiency and stability."""
		completion_rate = (self.effectiveness["first_time_pass"] + self.effectiveness["second_time_pass"]) / max(1, self.effectiveness["total_tasks"])
		return {
			"financial": {"net": self.get_profitability(), "total_spent": self.total_out},
			"tokens": self.tokens,
			"effectiveness": {
				"completion_rate": f"{completion_rate:.1%}",
				"ftp_rate": f"{(self.effectiveness['first_time_pass'] / max(1, self.effectiveness['total_tasks'])):.1%}"
			},
			"utilization": self.utilization,
			"health": self.get_project_health()
		}

	def get_profitability(self) -> float:
		"""Calculate current net stability."""
		return self.total_in - self.total_out

	def is_stable(self) -> bool:
		"""Check if the operation is financially viable."""
		if self.total_out > (self.total_in * 10 + 100):
			return False
		return True

# Global finance tracker
finance_tracker = FinancialTracker()
