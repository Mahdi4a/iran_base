app_name = "iran_base"
app_title = "Iran Base"
app_publisher = "Mahdi"
app_description = "Shared Iran localization for Frappe apps"
app_email = "guts2day@gmail.com"
app_license = "agpl-3.0"

# Jalali helpers and Persian number formatting, loaded on the desk
app_include_js = ["/assets/iran_base/js/jalali.js", "/assets/iran_base/js/jalali_dates.js"]
app_include_css = "/assets/iran_base/css/jalali_dates.css"

extend_bootinfo = "iran_base.settings.extend_bootinfo"

after_install = "iran_base.patches.enable_jalali_dates.execute"

# A "Desk" tile on the apps screen. Frappe skips its own app there, so when the only other
# app is a separate UI (CRM at /crm) there would be no way to reach the desk from it.
add_to_apps_screen = [
	{
		"name": "iran_base",
		"logo": "/assets/frappe/images/frappe-framework-logo.svg",
		"title": "Desk",
		"route": "/app/user",
		"has_permission": "iran_base.permissions.can_open_desk",
	}
]
