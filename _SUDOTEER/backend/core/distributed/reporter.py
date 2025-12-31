import time
import json
import paho.mqtt.client as mqtt
import threading
import logging

logger = logging.getLogger("_SUDOTEER.Distributed")

class GreenhouseReporter:
	"""
	Distributed Control Reporter (Edge Computing).
	Provides a 'Heartbeat' mechanism to report status to a Master Overseer via MQTT.
	"""
	def __init__(self, unit_id="GH-01", broker_address="localhost", broker_port=1883):
		self.unit_id = unit_id
		self.broker = broker_address
		self.port = broker_port

		# MQTT v5 client (using CallbackAPIVersion.VERSION2 as per paho-mqtt 2.0+ standards)
		try:
			# Use VERSION1 if VERSION2 is not available (paho-mqtt < 2.0)
			from paho.mqtt.enums import CallbackAPIVersion
			self.client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=unit_id)
		except ImportError:
			self.client = mqtt.Client(client_id=unit_id)

		self.connected = False

		# Topics
		self.topic_status = f"greenhouse/{unit_id}/status"
		self.topic_alerts = f"greenhouse/{unit_id}/alerts"
		self.topic_commands = f"greenhouse/{unit_id}/commands"

		# Setup callbacks
		self.client.on_connect = self.on_connect
		self.client.on_disconnect = self.on_disconnect
		self.client.on_message = self.on_message

		self.connect_bg()

	def connect_bg(self):
		"""Connect in background to prevent blocking main simulation."""
		try:
			logger.info(f"[MQTT] Attempting to connect to Master at {self.broker}:{self.port}")
			self.client.connect(self.broker, self.port, 60)
			self.client.loop_start()
		except Exception as e:
			logger.warning(f"[MQTT] Warning: Could not connect to Master at {self.broker}. Unit {self.unit_id} running local-only.")

	def on_connect(self, client, userdata, flags, rc, properties=None):
		# rc=0 means success for MQTT v3, but v5 uses Reason Codes
		success = (rc == 0 if isinstance(rc, int) else rc.is_failure == False)
		if success:
			self.connected = True
			logger.info(f"🛡️ [DISTRIBUTED] Local Brain GH-01 Connected to Master Overseer")
			# Subscribe to commands from master
			self.client.subscribe(self.topic_commands)
			# Announce online status
			self.client.publish(self.topic_alerts, json.dumps({
				"id": self.unit_id,
				"msg": "Edge Node Online",
				"timestamp": time.time()
			}))
		else:
			logger.error(f"[MQTT] Connection failed with result code {rc}")

	def on_disconnect(self, client, userdata, rc, properties=None):
		self.connected = False
		logger.warning(f"⚠️ [DISTRIBUTED] Disconnected from Master. Falling back to Local Isolation mode.")

	def on_message(self, client, userdata, msg):
		"""Handle commands from the Master."""
		try:
			command_data = json.loads(msg.payload.decode())
			logger.info(f"📥 [MQTT] Master Command Received: {command_data}")
			# This would be processed by the command handler in the future
		except Exception as e:
			logger.error(f"[MQTT] Error parsing master command: {e}")

	def send_heartbeat(self, sensor_data):
		"""Report current state to the master every cycle."""
		if not self.connected:
			return

		payload = {
			"id": self.unit_id,
			"timestamp": time.time(),
			"data": sensor_data,
			"status": "online"
		}

		try:
			self.client.publish(self.topic_status, json.dumps(payload))
		except Exception as e:
			logger.error(f"[MQTT] Failed to publish heartbeat: {e}")

	def stop(self):
		self.connected = False
		self.client.loop_stop()
		self.client.disconnect()
