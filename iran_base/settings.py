from __future__ import annotations


def extend_bootinfo(bootinfo):
	"""Dates show as Jalali on the desk unless "Use Jalali Dates" is switched off in Iran Settings."""
	value = get_setting("use_jalali_dates")
	bootinfo.iran_base = {"jalali_dates": 1 if value is None else int(bool(int(value)))}


def get_setting(fieldname: str, doctype: str = "Iran Settings", password: bool = False):
	"""A value from a settings page, or from the same key in site_config.json while the field is empty.

	The settings pages are the place to set things; site_config.json keeps working for setups made
	before they existed. Zero and unticked count as values, only None and "" fall through.
	"""
	import frappe

	value = None
	try:
		if password:
			from frappe.utils.password import get_decrypted_password

			value = get_decrypted_password(doctype, doctype, fieldname, raise_exception=False)
		else:
			value = frappe.db.get_single_value(doctype, fieldname)
	except Exception:
		# The page does not exist yet (before migrate), or there is no database
		value = None

	if value is None or value == "":
		return frappe.conf.get(fieldname)
	return value
