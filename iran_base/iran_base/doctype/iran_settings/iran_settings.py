import frappe
from frappe.model.document import Document


class IranSettings(Document):
	def on_update(self):
		set_jalali_default(self.use_jalali_dates)


def set_jalali_default(value):
	"""The CRM page only gets frappe.defaults (as sysdefaults), so the Jalali switch is published there too."""
	frappe.db.set_default("iran_jalali_dates", "1" if int(value or 0) else "0")
