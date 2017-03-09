# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

# test_records = frappe.get_test_records('BOQ')

class TestBOQ(unittest.TestCase):
	def make_boq(self):
		create_boq()	
	

def create_boq(**args):
	boq = frappe.new_doc("BOQ")
	boq.project = args.project or "P1400"
	boq.is_active = args.is_active or 1

	if not args.items:
		items = []
		items.append({"item": "RFC", "parent_item": None, "qty":1, "uom": "Nos"})
		items.append({"item": "C1", "parent_item": "RFC", "qty":3, "uom": "Nos"})
		items.append({"item": "C2", "parent_item": "RFC", "qty":1, "uom": "Nos"})
		items.append({"item": "G1", "parent_item": "C1", "qty":3, "uom": "Nos"})
		items.append({"item": "B1", "parent_item": "C1", "qty":3, "uom": "Nos"})
		items.append({"item": "B2", "parent_item": "C1", "qty":5, "uom": "Nos"})
		items.append({"item": "B1", "parent_item": "C2", "qty":4, "uom": "Nos"})
		items.append({"item": "B2", "parent_item": "C2", "qty":7, "uom": "Nos"})

		boq.append("items", items)
	else:
		boq.append("items", args.items)

	boq.save()
	frappe.db.commit()

