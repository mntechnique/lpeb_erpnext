# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "lpeb_erpnext"
app_title = "LPEB ERPNext"
app_publisher = "MN Technique"
app_description = "ERPNext customization for Loya PEB"
app_icon = "fa fa-industry"
app_color = "grey"
app_email = "support@mntechnique.com"
app_license = "GPLv3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lpeb_erpnext/css/lpeb_erpnext.css"
# app_include_js = "/assets/lpeb_erpnext/js/lpeb_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/lpeb_erpnext/css/lpeb_erpnext.css"
# web_include_js = "/assets/lpeb_erpnext/js/lpeb_erpnext.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "lpeb_erpnext.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "lpeb_erpnext.install.before_install"
# after_install = "lpeb_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lpeb_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
    "Project": {
        "on_update": "lpeb_erpnext.api.activate_deactivate_bom",
    }
}

# scheduler_events = {
# 	"all": [
# 		"lpeb_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"lpeb_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"lpeb_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"lpeb_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"lpeb_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "lpeb_erpnext.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "lpeb_erpnext.event.get_events"
# }

fixtures = [{"dt":"Custom Script", "filters": [["name", "in", ["Item-Client"]]]},
            {"dt":"Custom Field", "filters": [["name", "in",
                                                ["Item-lp_item_sub_category", "Item-lp_item_category"]]]},
{"dt": "Print Format", "filters": [["name", "in", 
												["Dispatch Order"]]]},
                                                "Property Setter"]

