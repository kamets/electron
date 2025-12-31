"""
MEWTOCOL Protocol Utilities for NAiS/Panasonic PLC Communication.
Includes BCC (Block Check Code) checksum calculation for industrial reliability.
"""

class MewtocolFrame:
	@staticmethod
	def calculate_bcc(payload: str) -> str:
		"""
		Calculates the BCC (Block Check Code) for a MEWTOCOL payload.
		XORs every character's ASCII value.
		"""
		bcc = 0
		for char in payload:
			bcc ^= ord(char)

		# Return 2-character uppercase Hex code
		return f"{bcc:02X}"

	@staticmethod
	def build_frame(unit_no: int, command: str, data: str) -> str:
		"""
		Builds a complete MEWTOCOL command frame.
		Format: % + UnitNo + # + Command + Data + BCC + CR
		"""
		unit_str = f"{unit_no:02d}"
		payload = f"{unit_str}#{command}{data}"
		bcc = MewtocolFrame.calculate_bcc(payload)

		return f"%{payload}{bcc}\r"

	@staticmethod
	def verify_frame(frame: str) -> bool:
		"""
		Verifies if a received frame has a valid BCC.
		"""
		if not frame.startswith('%') or not frame.endswith('\r'):
			return False

		# Extract payload and BCC
		# Format: % [Payload] [BCC (2 chars)] \r
		payload_with_bcc = frame[1:-1]
		if len(payload_with_bcc) < 2:
			return False

		payload = payload_with_bcc[:-2]
		received_bcc = payload_with_bcc[-2:]

		calculated_bcc = MewtocolFrame.calculate_bcc(payload)
		return calculated_bcc == received_bcc
