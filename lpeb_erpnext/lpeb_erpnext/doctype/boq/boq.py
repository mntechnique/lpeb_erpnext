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


    # on click submit button in boq, by default BOM create based on parent_item of BOQ Item
    def on_submit(self):
        print "test test"
        items = frappe.get_all("BOQ Item", filters={"parent": self.name }, fields=["*"], order_by="idx")
        items = [i["item"] for i in items]

        msgs = []

        for item in items:
            children = frappe.get_all("BOQ Item", filters={"parent":self.name, "parent_item": item}, fields=["*"])
            if len(children) > 0:

                if len(frappe.get_all("BOM", filters={"item": item, "project": self.project})) == 0:
                    msg = self.make_actual_bom(item, children)
                    msgs.append(msg)
                else:
                    msgs.append("BOM already created for item '{0}' under project '{1}'".format(item, project))

        return "<br>".join(msgs)

    def make_actual_bom(self, item, children):
        b = frappe.new_doc("BOM")
        b.project = self.project
        b.item = item
        b.qty = frappe.db.get_value("BOQ Item",filters={"parent": self.name, "item": item})

        for child in children:
            b.append("items", {
                "item_code": child.get("item"),
                "qty": child.qty
            })

        try:
            b.save()
            b.submit()
            frappe.db.commit()
            return "BOM '{0}' created for item '{1}'".format(b.name, b.item)

        except Exception as e:
            frappe.db.rollback()
            return ""

