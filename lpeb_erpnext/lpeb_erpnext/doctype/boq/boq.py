# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class BOQ(Document):
    def validate(self):
        self.check_active_boq()
        self.check_duplicate_items()

    def check_active_boq(self):
        if self.project:
            boq = frappe.get_all("BOQ", filters=[["project", "=", self.project], ["is_active", "=", 1], ["name", "!=", self.name]])
            if len(boq) >= 1:
                frappe.throw(_("{0} is active for this project. Cannot create new BOQ.".format(boq[0].name)))

    def check_duplicate_items(self):
        boq_items = self.items

        previtem = boq_items[0]
        for i in xrange(1,len(boq_items)):
            if boq_items[i].item == previtem.item and boq_items[i].parent_item == previtem.parent_item:
                frappe.throw("Row # {0}:  Repeating items found.".format(boq_items[i].idx))
            previtem = boq_items[i]
