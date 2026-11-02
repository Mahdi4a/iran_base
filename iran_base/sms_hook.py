"""Frappe's own SMS (Notification with the SMS channel, SMS Center, Send SMS on a Contact) goes
through the `send_sms` hook when an app sets one, instead of SMS Settings. This one sends through
the provider chosen in Iran Settings."""

from __future__ import annotations

import json

import frappe
from frappe import _

from iran_base.utils import sms


def receivers_of(receiver_list) -> list[str]:
	"""A list, a JSON list or a single number, as Frappe passes them."""
	if isinstance(receiver_list, str):
		try:
			receiver_list = json.loads(receiver_list)
		except ValueError:
			pass
	if not isinstance(receiver_list, list | tuple):
		receiver_list = [receiver_list]
	return [str(number) for number in receiver_list if number]


def send(receiver_list, msg: str, sender_name: str = "", success_msg: bool = True):
	"""Every receiver is tried, so one wrong number does not stop the rest."""
	receivers = receivers_of(receiver_list)
	if not receivers:
		frappe.throw(_("Please enter valid mobile nos"))

	message = frappe.safe_decode(msg)
	sent, failed = [], []
	for number in receivers:
		try:
			sms.send_sms(number, message)
			sent.append(number)
		except sms.SMSNotConfigured:
			frappe.msgprint(_("Please update Iran Settings with the keys of the SMS provider"))
			return
		except sms.SMSError as error:
			failed.append(number)
			frappe.log_error(title=f"SMS to {number} failed", message=str(error))
		except Exception:
			failed.append(number)
			frappe.log_error(title=f"SMS to {number} failed")

	if sent:
		create_sms_log(message, receivers, sent)
		if success_msg:
			frappe.msgprint(_("SMS sent successfully"))
	if failed:
		frappe.msgprint(
			_("SMS could not be sent to: {0}").format(", ".join(failed)), indicator="orange", alert=bool(sent)
		)


def create_sms_log(message: str, requested: list[str], sent: list[str]):
	"""Newer Frappe has no SMS Log, then nothing is kept."""
	if not frappe.db.exists("DocType", "SMS Log"):
		return
	log = frappe.new_doc("SMS Log")
	log.sent_on = frappe.utils.nowdate()
	log.message = message
	log.no_of_requested_sms = len(requested)
	log.requested_numbers = "\n".join(requested)
	log.no_of_sent_sms = len(sent)
	log.sent_to = "\n".join(sent)
	log.flags.ignore_permissions = True
	log.save()
