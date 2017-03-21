# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.model.document import Document

class LPEBDispatchOrder(Document):
	def before_submit(self):
		self.validate_actual_qty()

	def validate_actual_qty(self):
		dispatch_warehouses = frappe.get_doc("LPEB settings", "LPEB settings").dispatch_warehouses
		d_wh = None
		for wh in dispatch_warehouses:
			d_wh = wh.warehouse if wh.company == frappe.defaults.get_defaults().get("company") else None
	
		if not d_wh:
			frappe.throw("Please set Dispatch warehouse in LPEB Settings")

		for d in self.get('shop_floor_items'):
			if d.item_code:
				actual_qty = frappe.db.sql("""select actual_qty from `tabBin`
					where item_code = '{item_code}' and warehouse = '{warehouse}';""".format(item_code=d.item_code, warehouse=d_wh))

				if len(actual_qty) == 0 or flt(actual_qty[0][0]) < d.qty:
					frappe.throw("No Stock in Dispatch Warehouse")