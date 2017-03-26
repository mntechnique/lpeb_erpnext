# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class BOQ(Document):
	def validate(self):
		#self.check_active_boq()
		self.check_duplicate_items()

	def check_active_boq(self):
		if self.project and self.is_active == 1:
			boq = frappe.get_all("BOQ", filters=[["project", "=", self.project], ["is_active", "=", 1], ["name", "!=", self.name]])
			if len(boq) >= 1:

				frappe.throw(_("{0} is active for this project. Cannot create new BOQ.".format(boq[0].name)))
		#pass

	def check_duplicate_items(self):
		boq_items = self.items
		previtem = boq_items[0]
		for i in xrange(1,len(boq_items)):
			if boq_items[i].item == previtem.item and boq_items[i].parent_item == previtem.parent_item:
				frappe.throw("Row # {0}:  Repeating items found.".format(boq_items[i].idx))
			previtem = boq_items[i]


	#def on_submit(self):
	def on_submit(self):
		if self.is_active:
			self.submit_boms()
		else:
			frappe.throw("Cannot submit an inactive BOQ.")

	def on_cancel(self):
	    for x in xrange(1,10):
	        print "on_cancel"

	    self.cancel_boms()

	def submit_boms(self):
		subassemblies = [i for i in self.items if frappe.db.get_value("Item", i.item, "item_group") == "Sub Assemblies"]
		
		for sa in subassemblies:
			children = [i for i in self.items if i.parent_item == sa.item]
			if len(children) > 0:
				existing_sa_bom = frappe.db.get_value("BOM", {"project": self.project, "item": sa.item}, "name")
				if not existing_sa_bom:
					b_sa = frappe.new_doc("BOM")
					b_sa.item = sa.item
					b_sa.project = self.project

					print "BOM for ", sa.item, "project: ", self.project

					for child in children:

						print "BOM Item for ", child

						b_sa.append("items", {
							"item_code": child.item,
							"qty": child.qty,
							"stock_uom": child.uom
						})
					
					b_sa.save()
					b_sa.submit()
					frappe.db.commit()


		products = [i for i in self.items if frappe.db.get_value("Item", i.item, "item_group") == "Products"]

		for p in products:
			children = [i for i in self.items if i.parent_item == p.item]

			if len(children) > 0:
				existing_pr_bom = frappe.db.get_value("BOM", {"project":self.project, "item": p.item}, "name")
				if not existing_pr_bom:
					b_fg = frappe.new_doc("BOM")
					b_fg.item = p.item
					b_fg.project = self.project

					print "BOM for ", sa.item, "project: ", self.project

					for child in children:
						b_fg.append("items", {
							"item_code": child.item,
							"qty": child.qty,
							"bom_no": frappe.db.get_value("BOM", {"project": self.project, "item": child.item}, "name")
						})

					b_fg.save()
					b_fg.submit()
					frappe.db.commit()

	def cancel_boms(self):		
		products = [i for i in self.items if frappe.db.get_value("Item", i.item, "item_group") == "Products"]
		for p in products:
			print "Fetching BOM for cancelling: Project", self.project, "Item", p.item
			bom_p_name = frappe.get_all("BOM", {"project": self.project, "item": p.item, "docstatus": 1})
			print "Fetched?: ", bom_p_name
			if len(bom_p_name) > 0:
				print "Cancelling ", bom_p_name
				bom_p = frappe.get_doc("BOM", bom_p_name[0].name)
				bom_p.cancel()
				frappe.db.commit()

		subassemblies = [i for i in self.items if frappe.db.get_value("Item", i.item, "item_group") == "Sub Assemblies"]
		for sa in subassemblies:
			bom_sa_name = frappe.get_all("BOM", {"project": self.project, "item": sa.item, "docstatus": 1})
			if len(bom_sa_name) > 0:
				print "Cancelling ", bom_sa_name
				bom_sa = frappe.get_doc("BOM", bom_sa_name[0].name)
				bom_sa.cancel()
				frappe.db.commit()
