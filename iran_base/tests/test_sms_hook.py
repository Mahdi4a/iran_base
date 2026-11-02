import unittest
from unittest.mock import patch

from iran_base import sms_hook
from iran_base.utils.sms import SMSError, SMSNotConfigured


class TestSmsHook(unittest.TestCase):
	def test_receivers_come_as_a_list_a_json_list_or_one_number(self):
		self.assertEqual(sms_hook.receivers_of(["0912", "", "0935"]), ["0912", "0935"])
		self.assertEqual(sms_hook.receivers_of('["0912", "0935"]'), ["0912", "0935"])
		self.assertEqual(sms_hook.receivers_of("09121234567"), ["09121234567"])

	def test_a_wrong_number_does_not_stop_the_others(self):
		def fake_send(number, message):
			if number == "bad":
				raise SMSError("Invalid mobile number")

		with (
			patch.object(sms_hook.sms, "send_sms", side_effect=fake_send) as send,
			patch.object(sms_hook, "create_sms_log") as log,
			patch.object(sms_hook.frappe, "msgprint") as msgprint,
			patch.object(sms_hook.frappe, "log_error"),
			patch.object(sms_hook.frappe, "safe_decode", side_effect=lambda text: text),
			patch.object(sms_hook.frappe, "_", side_effect=lambda text: text),
		):
			sms_hook.send(["09121234567", "bad", "09351234567"], "hello")

		self.assertEqual(send.call_count, 3)
		log.assert_called_once_with("hello", ["09121234567", "bad", "09351234567"], ["09121234567", "09351234567"])
		self.assertEqual(msgprint.call_count, 2)

	def test_missing_provider_keys_stop_with_one_message(self):
		with (
			patch.object(sms_hook.sms, "send_sms", side_effect=SMSNotConfigured("signalads_token and signalads_sender are not set")) as send,
			patch.object(sms_hook, "create_sms_log") as log,
			patch.object(sms_hook.frappe, "msgprint") as msgprint,
			patch.object(sms_hook.frappe, "safe_decode", side_effect=lambda text: text),
			patch.object(sms_hook.frappe, "_", side_effect=lambda text: text),
		):
			sms_hook.send(["09121234567", "09351234567"], "hello")

		send.assert_called_once()
		log.assert_not_called()
		msgprint.assert_called_once()
