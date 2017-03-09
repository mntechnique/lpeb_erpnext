from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Project",
					"label": "Projects",
					"description": _("List of Projects"),
				},
				{
					"type": "doctype",
					"name": "BOQ",
					"label": "Bill of Quantities",
					"description": _("List of Bills of Quantities"),
				},
				{
					"type": "doctype",
					"name": "BOM",
					"label": "BOM",
					"description": _("List of Bills of Material"),
				},
				{
					"type": "doctype",
					"name": "LPEB Dispatch Order",
					"label": "Dispatch Order",
					"description": _("List of Dispatch Orders"),
				}
			]
		},
		{
			"label": _("Settings"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "LPEB settings",
					"label": "LPEB Settings",
					"description": _("General settings for LPEB ERPNext"),
				},
			]
		}
	]
