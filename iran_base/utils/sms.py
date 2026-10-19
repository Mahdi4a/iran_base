from __future__ import annotations

from iran_base.utils.numbers import to_latin_digits

SIGNALADS_URL = "https://transmitor.signalads.com"
KAVENEGAR_URL = "https://api.kavenegar.com/v1"
TIMEOUT = 15


class SMSError(Exception):
	pass


def try_normalize_mobile(mobile) -> str | None:
	"""An Iranian mobile as 09XXXXXXXXX, or None. Accepts +98 / 0098 / 98 / 9 prefixes and Persian digits."""
	digits = "".join(ch for ch in to_latin_digits(mobile) if ch.isdigit())
	if digits.startswith("0098"):
		digits = digits[4:]
	elif digits.startswith("98") and len(digits) == 12:
		digits = digits[2:]
	if len(digits) == 10 and digits.startswith("9"):
		digits = "0" + digits
	if len(digits) == 11 and digits.startswith("09"):
		return digits
	return None


def normalize_mobile(mobile) -> str:
	if (normalized := try_normalize_mobile(mobile)) is None:
		raise SMSError("Invalid mobile number")
	return normalized


def _setting(key: str):
	import frappe

	return frappe.conf.get(key)


def send_sms(mobile, message: str) -> dict:
	"""Send a plain SMS through the provider named by `iran_sms_provider` (default: signalads)."""
	import requests

	number = normalize_mobile(mobile)
	provider = _setting("iran_sms_provider") or "signalads"

	if provider == "signalads":
		token, sender = _setting("signalads_token"), _setting("signalads_sender")
		if not (token and sender):
			raise SMSError("signalads_token and signalads_sender are not set")
		response = requests.post(
			f"{SIGNALADS_URL}/api_v1/sms/send",
			headers={"Authorization": f"Bearer {token}"},
			json={"from": sender, "message": message, "numbers": [number]},
			timeout=TIMEOUT,
		)
	elif provider == "kavenegar":
		key = _setting("kavenegar_api_key")
		if not key:
			raise SMSError("kavenegar_api_key is not set")
		response = requests.post(
			f"{KAVENEGAR_URL}/{key}/sms/send.json",
			data={"receptor": number, "message": message, "sender": _setting("kavenegar_sender") or ""},
			timeout=TIMEOUT,
		)
	else:
		raise SMSError(f"Unknown SMS provider {provider!r}")

	if not response.ok:
		raise SMSError(f"{provider} returned {response.status_code}")
	return response.json()
