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
        if self.project and self.is_active == 1:
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


    #def on_submit(self):
    def on_submit(self):
        if self.is_active:
            self.submit_boms()
        else:
            frappe.throw("Cannot submit an inactive BOQ.")

    # def on_cancel(self):
    #     for x in xrange(1,10):
    #         print "on_cancel"


    #     subassemblies = [i for i in self.items if frappe.db.get_value("Item", i.item, "item_group") == "Sub Assemblies"]
    #     for sa in subassemblies:
    #         bom_sa_name = frappe.get_all("BOM", {"project": self.project, "item": sa.item})
    #         if len(bom_sa_name) > 0:
    #             print "To Cancel (SA)", bom_sa_name
    #             # bom_sa = frappe.get_doc("BOM", bom_sa_name[0]["name"])
    #             # bom_sa.cancel()
    #             # frappe.db.commit()

    #     products = [i for i in self.items if frappe.db.get_value("Item", i.item, "item_group") == "Products"]
    #     for p in products:
    #         bom_p_name = frappe.get_all("BOM", {"project": self.project, "item": p.item})
    #         if len(bom_p_name) > 0:
    #             print "To Cancel (Product)", bom_sa_name
    #             # bom_p = frappe.get_doc("BOM", {"project": self.project, "item": p.item})
    #             # bom_p.cancel()
    #             # frappe.db.commit()


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
                        b_sa.append("items", {
                            "item_code": child.item,
                            "qty": child.qty,
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
                            "bom_no": frappe.db.get_value("BOM", {"item": child.item}, "name")
                        })

                    b_fg.save()
                    b_fg.submit()
                    frappe.db.commit()


# def build_bom_submit_queue(item, boq, bom_queue):
#     children = frappe.get_all("BOQ Item", filters={"parent": boq, "parent_item": item}, fields=["item", "parent_item"]) 

#     if len(children) > 0:
#         bom_queue.append(item)

#         for c in children:
#             build_bom_submit_queue(c.item, boq, bom_queue)

    

    # b = frappe.new_doc("BOM")
    # b.item = item_name
    # b.qty = frappe.db.get_value("BOQ Item",filters={"parent": boq, "item": item})

    # print "New BOM for ", item

    # children = frappe.get_all("BOQ Item", filters={"parent": boq, "parent_item": item}, fields=["*"], order_by="idx")

    # print "Children: ", "None" if len(children) == 0 else [c.item for c in children]

    # for child in children:
    #     b.append("items", {
    #         "item_code": child.item_code,
    #         "qty": child.qty,
    #         "bom_no": make_bom_for_item(child.item_code, boq)
    #     })
        
    # b.save()
    # b.submit()
    # frappe.db.commit()

    # return b.name

    # # on click submit button in boq, by default BOM create based on parent_item of BOQ Item
    # def on_submit(self):
    #     print "test test"
    #     items = frappe.get_all("BOQ Item", filters={"parent": self.name }, fields=["*"], order_by="idx")
    #     items = [i["item"] for i in items]

    #     msgs = []

    #     for item in items:
    #         children = frappe.get_all("BOQ Item", filters={"parent":self.name, "parent_item": item}, fields=["*"])
    #         if len(children) > 0:

    #             if len(frappe.get_all("BOM", filters={"item": item, "project": self.project})) == 0:
    #                 msg = self.make_actual_bom(item, children)
    #                 msgs.append(msg)
    #             else:
    #                 msgs.append("BOM already created for item '{0}' under project '{1}'".format(item, project))

    #     return "<br>".join(msgs)

    # def make_actual_bom(self, item, children):
    #     b = frappe.new_doc("BOM")
    #     b.project = self.project
    #     b.item = item
    #     b.qty = frappe.db.get_value("BOQ Item",filters={"parent": self.name, "item": item})

    #     for child in children:
    #         b.append("items", {
    #             "item_code": child.get("item"),
    #             "qty": child.qty
    #         })

    #     try:
    #         b.save()
    #         b.submit()
    #         frappe.db.commit()
    #         return "BOM '{0}' created for item '{1}'".format(b.name, b.item)

    #     except Exception as e:
    #         frappe.db.rollback()
    #         return ""

