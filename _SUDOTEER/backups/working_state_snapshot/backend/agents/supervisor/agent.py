import logging
import json
import dspy
import asyncio
from typing import Any, Dict, List, Optional
from backend.core.agent_base import BaseAgent
from backend.core.protocol import A2AMessage
from backend.core.memory.dspy_signatures import (
	DecomposeUserGoal,
	RouteToAgent,
	NarrateResults,
	RiskAssessment
)
from backend.core.agent_challenges import trigger_level_up
from backend.core.gamification import matryoshka_engine
from backend.core.memory.dspy_modules.calibration import confidence_monitor
from backend.core.memory.manager import memory_manager

logger = logging.getLogger("_SUDOTEER")

class SupervisorAgent(BaseAgent):
	"""
	Tier 1: The Supervisor (The Front Man).
	User's single point of contact.
	Processes goals → delegates tasks → explains results.
	Acts as the narrator and central router for all operations.

	USES DSPY: ChainOfThought with typed signatures for reasoning.
	"""
	def __init__(self, agent_id: str = "supervisor_01", role: str = "Supervisor"):
		super().__init__(agent_id, role)
		self.active_delegations: Dict[str, Any] = {}

		# DSPy Modules - Using Predict for faster, direct responses
		self.decomposer = dspy.Predict(DecomposeUserGoal)
		self.router = dspy.Predict(RouteToAgent)
		self.narrator = dspy.Predict(NarrateResults)
		self.risk_assessor = dspy.Predict(RiskAssessment)

	async def perform_risk_assessment(self, action: str) -> Dict[str, Any]:
		"""Mechanical Humility: Hard check before high-stakes actions."""
		if not matryoshka_engine.check_unlocked("risk_assessment", self.agent_id):
			return {"recommendation": "PROCEED", "risk_score": 0.0}

		context = await self.get_context(action, extra_context=self._get_system_context())
		result = await asyncio.to_thread(self.risk_assessor, proposed_action=action, context=context)

		score = float(result.risk_score)
		recommendation = result.recommendation

		self.log_interaction(f"Risk Assessment for '{action}': {score} ({recommendation})", "thought")

		if recommendation == "PAUSE_EXECUTION" or score > 0.8:
			self.log_interaction("🛑 HIGH RISK DETECTED. Execution Paused. Requiring User ACK.", "escalation")
			return {"recommendation": "PAUSE", "score": score, "factor": result.risk_factor}

		return {"recommendation": "PROCEED", "score": score}

	async def forward(self, user_goal: str) -> Dict[str, Any]:
		"""
		Main reasoning path for the Supervisor using DSPy.
		1. Check for DIRECT COMMANDS first (instant response)
		2. Risk Assessment (Human Gavel)
		3. Calibration (Ambiguity Check)
		4. Decompose & Route
		"""
		self.log_interaction(f"Supervisor starting mission: {user_goal}", event_type="thought")

		# FAST PATH: Handle simple commands directly without DSPy
		direct_result = await self._handle_direct_command(user_goal.lower())
		if direct_result:
			return direct_result

		# 1. Risk Assessment (Level 2+)
		assessment = await self.perform_risk_assessment(user_goal)
		if assessment["recommendation"] == "PAUSE":
			return {
				"status": "paused",
				"reason": "HIGH_RISK",
				"details": assessment["factor"],
				"score": assessment["score"]
			}

		# 2. Confidence Calibration (Level 3+)
		if matryoshka_engine.check_unlocked("confidence_calibration", self.agent_id):
			context = await self.get_context(user_goal, extra_context=self._get_system_context())
			draft = await asyncio.to_thread(self.decomposer, user_goal=user_goal, context=context)

			calibration = await confidence_monitor.verify_plan(user_goal, str(draft.subtasks))
			if not calibration["is_confident"]:
				self.log_interaction(f"Hubris Detected! Ambiguity: {calibration['ambiguity_score']}", "thought")
				return {
					"status": "clarification_required",
					"question": calibration["clarification"],
					"assumptions": calibration["assumptions"]
				}

		# 3. Standard DSPy Decomposition with Context Sandwich
		context = await self.get_context(user_goal, extra_context=self._get_system_context())

		decompose_result = await asyncio.to_thread(
			self.decomposer,
			user_goal=user_goal,
			context=context
		)

		subtasks = decompose_result.subtasks if isinstance(decompose_result.subtasks, list) else [decompose_result.subtasks]
		self.log_interaction(
			f"DSPy Decomposed: {len(subtasks)} subtasks",
			event_type="thought"
		)

		# Step 4: DSPy Routing
		delegation_plan = await self._dspy_route_tasks(subtasks)

		# Step 5: Execute delegations
		results = {}
		for agent_id, task_data in delegation_plan.items():
			self.log_interaction(f"Delegating to {agent_id}", event_type="action")
			result = await self.send_a2a(agent_id, task_data, message_type="request")
			results[agent_id] = result

		# Step 6: DSPy Narration
		narrative_result = await asyncio.to_thread(
			self.narrator,
			original_goal=user_goal,
			agent_results=json.dumps(results, indent=2)
		)

		self.log_interaction(f"Supervision complete.", event_type="observation")

		# Call the Sifter to archive this mission into episodic memory
		await memory_manager.sifter_session_end(self.agent_id)

		# Mastery Loop: Trigger Level Up challenge if mission complete
		final_status = "complete"
		await trigger_level_up(self.agent_id)

		return {
			"status": final_status,
			"goal": user_goal,
			"narrative": narrative_result.narrative,
			"key_insights": narrative_result.key_insights,
			"raw_results": results
		}

	def _get_system_context(self) -> str:
		"""Get current system state for DSPy decomposition."""
		available_agents = {
			"tier_1": ["supervisor_01"],
			"tier_2_operational": [
				"climate_agent (temperature, heating, cooling)",
				"nutrient_agent (water, pH, EC, irrigation)",
				"photoperiod_agent (lights, day/night cycles)",
				"predictive_agent (growth forecasting)",
				"anomaly_agent (sensor drift detection)"
			],
			"tier_3_development": [
				"architect_01 (system design, planning)",
				"coder_01 (code generation)",
				"tester_01 (testing, validation)",
				"documenter_01 (documentation)",
				"validator_01 (audit, quality assurance)"
			]
		}

		return json.dumps({
			"available_agents": available_agents,
			"system_status": "online",
			"current_focus": "greenhouse seed production and development workflow"
		}, indent=2)

	async def _dspy_route_tasks(self, subtasks: List[str]) -> Dict[str, Any]:
		"""
		Use DSPy to intelligently route subtasks to agents.
		This replaces the hardcoded keyword matching with LLM reasoning.
		"""
		plan = {}
		available_agents_json = self._get_system_context()

		for subtask in subtasks:
			try:
				# DSPy decides the routing
				route_result = await asyncio.to_thread(
					self.router,
					subtask=subtask,
					available_agents=available_agents_json
				)

				# Handle both Prediction objects and raw strings
				if hasattr(route_result, 'agent_id'):
					agent_id = route_result.agent_id
					reasoning = getattr(route_result, 'reasoning', 'No reasoning provided')
				elif isinstance(route_result, str):
					# Fallback: extract agent from response text
					agent_id = "nutrient_agent" if "water" in subtask.lower() or "pump" in subtask.lower() else "climate_agent"
					reasoning = f"Fallback routing (raw response): {route_result[:100]}"
				else:
					agent_id = "supervisor_01"
					reasoning = "Unable to parse routing result"

				self.log_interaction(
					f"Routed '{subtask}' -> {agent_id}\nReasoning: {reasoning}",
					event_type="thought"
				)

				# Store in delegation plan
				if agent_id not in plan:
					plan[agent_id] = {"goals": []}
				plan[agent_id]["goals"].append(subtask)

			except Exception as e:
				logger.warning(f"Routing failed for '{subtask}': {e}")
				# Default to supervisor handling
				if "supervisor_01" not in plan:
					plan["supervisor_01"] = {"goals": []}
				plan["supervisor_01"]["goals"].append(subtask)

		return plan

	async def handle_request(self, message: A2AMessage) -> Any:
		"""
		Handle peer-to-peer requests from other agents.
		The Supervisor can receive status updates or escalations.
		"""
		self.log_interaction(f"Supervisor received request from {message.from_agent}", event_type="thought")

		content = message.content
		if isinstance(content, dict):
			if "escalation" in content:
				# Handle escalations from lower-tier agents
				return await self._handle_escalation(content["escalation"], message.from_agent)
			elif "status_update" in content:
				# Log status updates
				self.log_interaction(f"Status from {message.from_agent}: {content['status_update']}", event_type="observation")
				return {"acknowledged": True}

		return {"response": "Supervisor acknowledges your message."}

	async def _handle_escalation(self, escalation_data: Dict, from_agent: str) -> Dict:
		"""
		Handle escalations from Tier 2/3 agents.
		E.g., when an agent hits an issue or needs human-in-the-loop approval.
		"""
		logger.warning(f"ESCALATION from {from_agent}: {escalation_data}")

		# In production, this would trigger a UI notification or voice alert
		self.log_interaction(
			f"Escalation received: {escalation_data.get('reason', 'Unknown')}",
			event_type="escalation"
		)

		return {
			"escalation_acknowledged": True,
			"action": "Flagged for human review",
			"from_agent": from_agent
		}

	async def _handle_direct_command(self, goal: str) -> Dict[str, Any] | None:
		"""
		FAST PATH: Handle simple greenhouse commands directly without LLM.
		Returns None if the command requires full DSPy processing.
		"""
		from backend.sandbox.simulations.greenhouse import greenhouse_sim

		state = greenhouse_sim.state
		actuators = greenhouse_sim.actuators
		env = greenhouse_sim.environment

		# Time queries
		if any(kw in goal for kw in ["time", "what time", "clock", "day"]):
			hour = int(env["sim_hour"])
			minute = int((env["sim_hour"] % 1) * 60)
			day = env["sim_day"]
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Day {day}, {hour:02d}:{minute:02d} (simulation time).",
				"key_insights": [f"Day: {day}", f"Time: {hour:02d}:{minute:02d}"],
				"raw_results": {"day": day, "hour": hour, "minute": minute}
			}

		# Weather queries
		if any(kw in goal for kw in ["weather", "outside", "ambient", "forecast"]):
			weather = env["weather"]
			outside_temp = env["outside_temp"]
			inside_temp = state["temperature"]
			weather_emoji = {"sunny": "☀️", "overcast": "☁️", "rain": "🌧️"}.get(weather, "")
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Weather: {weather.capitalize()} {weather_emoji}. Outside: {outside_temp:.1f}°C, Inside: {inside_temp:.1f}°C.",
				"key_insights": [
					f"Weather: {weather.capitalize()} {weather_emoji}",
					f"Outside: {outside_temp:.1f}°C",
					f"Inside: {inside_temp:.1f}°C"
				],
				"raw_results": {"weather": weather, "outside_temp": outside_temp, "inside_temp": inside_temp}
			}

		# Crop/Plant queries
		if any(kw in goal for kw in ["what are we growing", "what plant", "current crop", "what crop"]):
			crop = greenhouse_sim.crop
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Currently growing: {crop['plant_name']}. Stage: {crop['stage'].capitalize()}. Day {env['sim_day'] - crop['day_planted'] + 1} since planting.",
				"key_insights": [
					f"Crop: {crop['plant_name']}",
					f"Stage: {crop['stage'].capitalize()}",
					f"Days growing: {env['sim_day'] - crop['day_planted'] + 1}"
				],
				"raw_results": crop
			}

		# List available plants
		if any(kw in goal for kw in ["list plants", "available plants", "what can we grow", "plant menu"]):
			from backend.sandbox.simulations.plant_profiles import list_available_plants
			plants = list_available_plants()
			plant_list = ", ".join([p["name"] for p in plants])
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Available plants: {plant_list}",
				"key_insights": [f"{p['name']} ({p['days']} days)" for p in plants],
				"raw_results": {"plants": plants}
			}

		# Check optimal conditions for current crop
		if any(kw in goal for kw in ["optimal", "target", "ideal", "should be"]):
			from backend.sandbox.simulations.plant_profiles import check_condition_optimal
			crop = greenhouse_sim.crop
			results = check_condition_optimal(crop["plant_id"], crop["stage"], state)
			score = results.get("overall_score", 0) * 100

			status_items = []
			for key, val in results.items():
				if isinstance(val, dict) and "status" in val:
					emoji = "✅" if val["status"] == "optimal" else "⚠️"
					status_items.append(f"{emoji} {key.upper()}: {val['status']}")

			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Condition check for {crop['plant_name']} ({crop['stage']}): {score:.0f}% optimal. {results.get('notes', '')}",
				"key_insights": status_items[:6],
				"raw_results": results
			}

		# Temperature queries
		if any(kw in goal for kw in ["temperature", "temp", "how hot", "how cold"]):
			temp = state["temperature"]
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"The current greenhouse temperature is {temp:.1f}°C ({temp * 9/5 + 32:.1f}°F).",
				"key_insights": [f"Temperature: {temp:.1f}°C", "Within normal range" if 18 <= temp <= 28 else "Outside optimal range"],
				"raw_results": {"temperature": temp}
			}

		# Humidity queries
		if any(kw in goal for kw in ["humidity", "humid", "moisture"]):
			humidity = state["humidity"]
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"The current humidity level is {humidity:.1f}%.",
				"key_insights": [f"Humidity: {humidity:.1f}%", "Optimal" if 40 <= humidity <= 70 else "Needs adjustment"],
				"raw_results": {"humidity": humidity}
			}

		# Water pressure queries
		if any(kw in goal for kw in ["water pressure", "pressure", "psi"]):
			pressure = state["water_pressure"]
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Water pressure is currently {pressure:.1f} PSI.",
				"key_insights": [f"Pressure: {pressure:.1f} PSI", "Pump active" if actuators["pump_active"] else "Pump inactive"],
				"raw_results": {"water_pressure": pressure}
			}

		# Plant health/condition queries
		if any(kw in goal for kw in ["plant", "health", "condition", "crop", "yield"]):
			health = state["plant_health"]
			stress = state["stress_index"]
			yield_pot = state["yield_potential"]
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Plant health is at {health*100:.0f}%. Stress index: {stress:.2f}. Yield potential: {yield_pot:.1f} kg.",
				"key_insights": [
					f"Health: {health*100:.0f}%",
					f"Stress: {'Low' if stress < 0.3 else 'Medium' if stress < 0.6 else 'High'}",
					f"Yield: {yield_pot:.1f} kg"
				],
				"raw_results": {"health": health, "stress": stress, "yield": yield_pot}
			}

		# pH queries
		if any(kw in goal for kw in ["ph", "acidity", "alkaline"]):
			ph = state["ph_level"]
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"pH level is {ph:.2f}.",
				"key_insights": [f"pH: {ph:.2f}", "Optimal" if 5.5 <= ph <= 7.0 else "Needs adjustment"],
				"raw_results": {"ph_level": ph}
			}

		# Pump control - START
		if any(kw in goal for kw in ["start pump", "turn on pump", "pump on", "start the pump"]):
			greenhouse_sim.actuators["pump_active"] = True
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Water pump activated. Irrigation system is now running.",
				"key_insights": ["Pump: ON", "Water pressure building"],
				"raw_results": {"pump_active": True}
			}

		# Pump control - STOP
		if any(kw in goal for kw in ["stop pump", "turn off pump", "pump off"]):
			greenhouse_sim.actuators["pump_active"] = False
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Water pump deactivated. Irrigation system stopped.",
				"key_insights": ["Pump: OFF"],
				"raw_results": {"pump_active": False}
			}

		# Heater control
		if any(kw in goal for kw in ["turn on heat", "heater on", "start heater"]):
			greenhouse_sim.actuators["heater"] = True
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Heater activated. Temperature will rise.",
				"key_insights": ["Heater: ON"],
				"raw_results": {"heater": True}
			}

		if any(kw in goal for kw in ["turn off heat", "heater off", "stop heater"]):
			greenhouse_sim.actuators["heater"] = False
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Heater deactivated.",
				"key_insights": ["Heater: OFF"],
				"raw_results": {"heater": False}
			}

		# Lights control
		if any(kw in goal for kw in ["lights on", "turn on lights", "start lights"]):
			greenhouse_sim.actuators["lights"] = True
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Grow lights activated.",
				"key_insights": ["Lights: ON"],
				"raw_results": {"lights": True}
			}

		if any(kw in goal for kw in ["lights off", "turn off lights", "stop lights"]):
			greenhouse_sim.actuators["lights"] = False
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Grow lights deactivated.",
				"key_insights": ["Lights: OFF"],
				"raw_results": {"lights": False}
			}

		# Fan control
		if any(kw in goal for kw in ["fan on", "turn on fan", "start fan"]):
			greenhouse_sim.actuators["fan"] = True
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Ventilation fan activated.",
				"key_insights": ["Fan: ON"],
				"raw_results": {"fan": True}
			}

		if any(kw in goal for kw in ["fan off", "turn off fan", "stop fan"]):
			greenhouse_sim.actuators["fan"] = False
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Ventilation fan deactivated.",
				"key_insights": ["Fan: OFF"],
				"raw_results": {"fan": False}
			}

		# O2 Pump control
		if any(kw in goal for kw in ["o2 on", "oxygen on", "start o2", "o2 pump on"]):
			greenhouse_sim.actuators["o2_pump"] = True
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Oxygen pump activated. Adding dissolved O2 to reservoir.",
				"key_insights": ["O2 Pump: ON"],
				"raw_results": {"o2_pump": True}
			}

		if any(kw in goal for kw in ["o2 off", "oxygen off", "stop o2", "o2 pump off"]):
			greenhouse_sim.actuators["o2_pump"] = False
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Oxygen pump deactivated.",
				"key_insights": ["O2 Pump: OFF"],
				"raw_results": {"o2_pump": False}
			}

		# Nutrient A pump
		if any(kw in goal for kw in ["nutrient a on", "nutrition a on", "start nutrient a"]):
			greenhouse_sim.actuators["nutrient_a"] = True
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Nutrient A (Grow/Micro) pump activated.",
				"key_insights": ["Nutrient A: Dosing"],
				"raw_results": {"nutrient_a": True}
			}

		if any(kw in goal for kw in ["nutrient a off", "nutrition a off", "stop nutrient a"]):
			greenhouse_sim.actuators["nutrient_a"] = False
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Nutrient A pump stopped.",
				"key_insights": ["Nutrient A: OFF"],
				"raw_results": {"nutrient_a": False}
			}

		# Nutrient B pump
		if any(kw in goal for kw in ["nutrient b on", "nutrition b on", "start nutrient b"]):
			greenhouse_sim.actuators["nutrient_b"] = True
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Nutrient B (Bloom) pump activated.",
				"key_insights": ["Nutrient B: Dosing"],
				"raw_results": {"nutrient_b": True}
			}

		if any(kw in goal for kw in ["nutrient b off", "nutrition b off", "stop nutrient b"]):
			greenhouse_sim.actuators["nutrient_b"] = False
			return {
				"status": "complete",
				"goal": goal,
				"narrative": "Nutrient B pump stopped.",
				"key_insights": ["Nutrient B: OFF"],
				"raw_results": {"nutrient_b": False}
			}

		# EC level queries
		if any(kw in goal for kw in ["ec", "electrical conductivity", "nutrient level"]):
			ec = state["ec_level"]
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"EC level is {ec:.2f} mS/cm.",
				"key_insights": [f"EC: {ec:.2f} mS/cm", "Optimal" if 1.2 <= ec <= 2.5 else "Needs adjustment"],
				"raw_results": {"ec_level": ec}
			}

		# Light level queries
		if any(kw in goal for kw in ["lux", "light level", "brightness", "light intensity"]):
			lux = state["lux"]
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Light intensity is {lux:.0f} lux.",
				"key_insights": [f"Lux: {lux:.0f}", "Lights: " + ("ON" if actuators["lights"] else "OFF")],
				"raw_results": {"lux": lux}
			}

		# System status
		if any(kw in goal for kw in ["status", "how is", "overview", "report"]):
			return {
				"status": "complete",
				"goal": goal,
				"narrative": f"Greenhouse Status: Temp {state['temperature']:.1f}°C, Humidity {state['humidity']:.1f}%, pH {state['ph_level']:.2f}, EC {state['ec_level']:.2f} mS/cm. Pump: {'ON' if actuators['pump_active'] else 'OFF'}, Lights: {'ON' if actuators['lights'] else 'OFF'}.",
				"key_insights": [
					f"Temp: {state['temperature']:.1f}°C",
					f"Humidity: {state['humidity']:.1f}%",
					f"pH: {state['ph_level']:.2f}",
					f"EC: {state['ec_level']:.2f} mS/cm",
					f"Pump: {'Active' if actuators['pump_active'] else 'Inactive'}",
					f"Lights: {'ON' if actuators['lights'] else 'OFF'}"
				],
				"raw_results": {"state": state, "actuators": actuators}
			}

		# Not a direct command - needs full DSPy processing
		return None
