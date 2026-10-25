import frappe


def execute():
	"""Dates are Jalali from the start. A single that was never saved reads an unticked box as 0, not as its default."""
	from iran_base.iran_base.doctype.iran_settings.iran_settings import set_jalali_default

	if not frappe.db.exists("Singles", {"doctype": "Iran Settings", "field": "use_jalali_dates"}):
		frappe.db.set_single_value("Iran Settings", "use_jalali_dates", 1)
	set_jalali_default(frappe.db.get_single_value("Iran Settings", "use_jalali_dates"))
