# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

class LPEBDispatchOrder(Document):
	def validate(self):
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
		warehouse = ""
		item_group = ""

		for item in self.shop_floor_items:
			item_group = frappe.db.get_value("Item",{"item_code": item.item_code}, fieldname="item_group" )
			if item_group == "Raw Material":
				warehouse = frappe.db.get_value("Warehouse", filters={
							"warehouse_name": _("Raw Materials"),
							"company": frappe.defaults.get_defaults().company
						},fieldname="name")
				igm.update({item_group:warehouse})
			elif item_group == "Sub Assemblies":
				warehouse = frappe.db.get_value("Warehouse", filters={
							"warehouse_name": _("Finished Goods"),
							"company": frappe.defaults.get_defaults().company
						},fieldname ="name")

				igm.update({item_group:warehouse})
			for x in xrange(1,1000):
				print "item", igm.get("Raw Material")
			if item_group == "Raw Material" and igm.get("Raw Material") == item.warehouse:
				valid = True
			elif item_group == "Sub Assemblies" and igm.get("Finished Goods") == item.warehouse:
				valid = True
			else:
				valid = False




			if not valid:
				frappe.throw("Error")

		# item_wh_map = { }
		# item_group = None
		# valid = False

		# for item in self.shop_floor_items:
		# 	item_group = frappe.db.get_value("Item",{"item_code": item.item_code}, fieldname="item_group" )
		# 	# a = item_wh_map.append({item_group:item.warehouse})

		# 	if item_group == "Raw Materials":
		# 		if item.warehouse == "Raw Materials - L":
		# 			valid = True;

		# 	if item_group == "Sub Assemblies":
		# 		if item.warehouse == "Finished Goods - L":
		# 			valid = True;


		# 	# if a.get("Raw Materials") == item.warehouse:
		# 	# 	valid = True
		# 	# elif a.get("Finsihed Goods") == item.warehouse:
		# 	# 	valid = True
		# 	# else:
		# 	# 	Frappe.throw(_(""))








		# 	# elif item_group == "Sub Assemblies":
		# 	# 	item_wh_map.append({item_group:item.warehouse})

		# 	# if item_wh_map.get("item_group") == :

