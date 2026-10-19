import frappe


def can_open_desk() -> bool:
	"""The Desk tile for System Managers, unless ERPNext is installed: its own tile opens the same desk."""
	if "erpnext" in frappe.get_installed_apps():
		return False
	return frappe.session.user != "Guest" and "System Manager" in frappe.get_roles()
