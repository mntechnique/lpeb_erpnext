# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document
from lpeb_erpnext.api import get_warehouses_for_project
from erpnext import get_default_company

class LPEBDispatchOrder(Document):

	def on_submit(self):
		self.validate_warehouse()
		self.validate_actual_qty()
		self.pre_submit_validation()
		self.make_repack_entries()

	def validate(self):
		self.validate_office_items()
		self.validate_shop_floor_items()

	def validate_actual_qty(self):
		for d in self.get('shop_floor_items'):
			if d.item_code:
				actual_qty = frappe.db.sql("""select actual_qty from `tabBin`
					where item_code = '{item_code}' and warehouse = '{warehouse}';""".format(item_code=d.item_code, warehouse=d.warehouse))

				if len(actual_qty) == 0 or flt(actual_qty[0][0]) < d.qty:
					frappe.throw("Insufficient stock for '{0}' in {1}".format(d.item_code, d.warehouse))

	def validate_warehouse(self):
		valid = False
		igm = {}
		warehouse1 = ""
		item_group = ""

		for item in self.shop_floor_items:
			item_group = frappe.db.get_value("Item",{"item_code": item.item_code}, fieldname="item_group")

			if item_group == "Sub Assemblies":
				fg_wh = self.project + " - FG"
				warehouse1 = frappe.db.get_value("Warehouse", filters={
							"warehouse_name": fg_wh,
							"company": frappe.defaults.get_defaults().company
						}, fieldname="name")
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

	def validate_office_items(self):
		#Duplicates
		if len(self.office_items) != len(set(self.office_items)):
			frappe.throw("Please remove duplicate office items.")

		so = frappe.get_doc("Sales Order", self.sales_order)
		for oi in self.office_items:
			#Item not set in Office Item
			if not oi.item_code:
				frappe.throw("Office Details #{0}: Please select an item, or delete the row.".format(oi.idx))

			#Item does not belong to SO
			so_item = [soi for soi in so.items if soi.item_code == oi.item_code]
			if len(so_item) == 0:
				frappe.throw("Item '{0}' does not belong to Sales Order '{1}'.".format(oi.item_code, self.sales_order))


	def validate_shop_floor_items(self):
		#Duplicates
		if len(self.shop_floor_items) != len(set(self.shop_floor_items)):
			frappe.throw("Please remove duplicate shop floor items.")


		for sfi in self.shop_floor_items:
			#Item code not set in SFI
			if not sfi.item_code:
				frappe.throw("Shop Floor Details #{0}: Please select an item, or delete the row.".format(sfi.idx))

	def pre_submit_validation(self):
		if (len(self.office_items) == 0):
			frappe.throw("Please enter at least one item under Office Details Details.")

		if (len(self.shop_floor_items) == 0):
			frappe.throw("Please enter at least one item under Shop Floor Details.")

		if (len([oi for oi in self.office_items if not oi.weight]) > 0):
			frappe.throw("All items under Office Details must have valid weights.")

	def make_repack_entries(self):
		project_warehouses = get_warehouses_for_project(self.project)

		fg_warehouse = project_warehouses["fg_warehouse"]

		for oi in self.office_items:
			sfi_list = [sfi for sfi in self.shop_floor_items if sfi.parent_item == oi.item_code]

			re = frappe.new_doc("Stock Entry")
			re.purpose = "Repack"
			re.lpeb_dispatch_order = self.name
			re.project = self.project

			re.posting_date = frappe.utils.getdate()
			re.posting_time = frappe.utils.get_time(frappe.utils.get_datetime())
			re.company = get_default_company()

			for sfi in sfi_list:
				re.append("items", {
					"item_code": sfi.item_code,
					"qty": sfi.qty,
					"uom": sfi.uom,
					"conversion_factor": 1.0,
					"s_warehouse": fg_warehouse.name
				})

			re.append("items", {
				"item_code": oi.item_code,
				"qty": oi.weight,
				"uom": oi.weight_uom,
				"conversion_factor": 1.0,
				"t_warehouse": fg_warehouse.name
			})

			re.save()
			re.submit()
			frappe.db.commit()


	def create_si(self):
		from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

		si = make_sales_invoice(self.sales_order)
		si.lpeb_dispatch_order = self.name

		for sfi in self.shop_floor_items:
			si.append("lpeb_item_details", {
				"item": sfi.item_code,
				"qty": sfi.qty,
				"uom": sfi.uom,
				"parent_item": sfi.parent_item
			})

		try:
			si.save()
			frappe.db.commit()
		except Exception as e:
			return "Could not create Sales Invoice. <br>{0}".format(e.message)
		else:
			return "Sales Invoice #{0} created successfully.".format(si.name)


