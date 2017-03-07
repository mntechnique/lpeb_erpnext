# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class LPEBsettings(Document):
	def validate(self):
		self.validate_warehouses()
		self.validate_repeating_companies()
	
	def validate_repeating_companies(self):
		"""Error when Same Company is entered multiple times in accounts"""
		warehouses_list = []
		for entry in self.dispatch_warehouses:
			warehouses_list.append(entry.company)

		if len(warehouses_list)!= len(set(warehouses_list)):
			frappe.throw(_("Same Company is entered more than once"))

	def validate_warehouses(self):
		for entry in self.dispatch_warehouses:
			"""Error when Company of Ledger account doesn't match with Company Selected"""
			if frappe.db.get_value("Warehouse", entry.warehouse, "company") != entry.company:
				frappe.throw(_("Warehouse does not match with Company"))
