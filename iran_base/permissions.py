import frappe


def can_open_desk() -> bool:
	"""Only users of the desk get the tile; website users and guests do not."""
	return frappe.session.user != "Guest" and "System Manager" in frappe.get_roles()
