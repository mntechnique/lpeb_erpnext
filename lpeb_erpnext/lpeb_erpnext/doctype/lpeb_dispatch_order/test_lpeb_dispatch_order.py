# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

# test_records = frappe.get_test_records('LPEB Dispatch Order')

class TestLPEBDispatchOrder(unittest.TestCase):
	def tearDown(self):
		pass
		# frappe.set_user("Administrator")
		# for rec in test_records:
		# 	new_rec = frappe.new_doc("LPEB Dispatch Order")
		# 	new_rec.name = rec.name
		# 	new_rec.project = rec.project
		# 	new_rec.shop_floor_items = rec.shop_floor_items

		# 	frappe.db.commit()

	def test_qty_available_for_dispatch(self):
		pass
		# actual_qty = 0
		# d_wh = "Finished Goods - L"
		
		# doc = frappe.get_doc("LPEB Dispatch Order", "Test-LPDO-00001")
		# for d in doc.shop_floor_items:
		# 	actual_qty = frappe.db.sql("""select actual_qty from `tabBin`
		# 			where item_code = %s and warehouse = %s""", (d.item_code, d_wh))

		# 	self.assertTrue(actual_qty >= d.qty)

"""
 {
  "additional_items": [], 
  "amended_from": null, 
  "docstatus": 0, 
  "doctype": "LPEB Dispatch Order", 
  "modified": "2017-03-07 18:36:12.743359", 
  "name": "Test-LPDO-00001", 
  "office_items": [], 
  "project": "demo_project", 
  "shop_floor_items": [
   {
    "item_code": "012", 
    "qty": 100.0, 
    "uom": "Nos"
   }
  ]
 }
"""