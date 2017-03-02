# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class BOQ(Document):
    def check_active_boq(self):
        if self.project:
            boq = frappe.get_all("BOQ", filters={"project": self.project, "is_active": 1})
            if len(boq) >= 1:
                frappe.throw(_("Currently BOQ {0} is active. can't create new BOQ".format(boq[0].name)))

    def validate(self):
        self.check_duplicate_item()


    def check_duplicate_item(self):
        boq_items = frappe.get_all("BOQ Item",filters={"parent": self.name}, fields=["item, parent_item"])
        item = []
        for i in boq_items:
            item =i



