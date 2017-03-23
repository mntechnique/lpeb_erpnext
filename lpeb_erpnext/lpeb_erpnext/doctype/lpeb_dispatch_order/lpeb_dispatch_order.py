# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

class LPEBDispatchOrder(Document):
	def on_submit(self):
		self.validate_actual_qty()
		self.validate_warehouse()

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


	def validate_warehouse(self):

		valid = False
		igm = {}
		warehouse1 = ""
		item_group = ""

		for item in self.shop_floor_items:
			item_group = frappe.db.get_value("Item",{"item_code": item.item_code}, fieldname="item_group" )

			if item_group == "Sub Assemblies":
				warehouse1 = frappe.db.get_value("Warehouse", filters={
							"warehouse_name": "Finished Goods",
							"company": frappe.defaults.get_defaults().company
						},fieldname="name")
				igm.update({item_group:warehouse1})
				if igm.get("Sub Assemblies") == item.warehouse:
					valid = True
			elif item_group == "Raw Material":
				warehouse1 = frappe.db.get_value("Warehouse", filters={
							"warehouse_name": "Raw Materials",
							"company": frappe.defaults.get_defaults().company
						},fieldname="name")
				igm.update({item_group:warehouse1})
				if igm.get("Raw Material") == item.warehouse:
					valid = True

			else:
				valid = False

			if not valid:
				frappe.throw("Enter valid warehouse in shop floor item")

