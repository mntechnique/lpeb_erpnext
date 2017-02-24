import frappe
import json
from frappe.utils import get_url
from frappe import _


@frappe.whitelist()
def make_boms(boq, project):
    items = frappe.get_all("BOQ Item", filters={"parent": boq }, fields=["*"], order_by="idx")
    items = [i["item"] for i in items]

    msgs = []

    for item in items:
        children = frappe.get_all("BOQ Item", filters={"parent":boq, "parent_item": item}, fields=["*"])
        if len(children) > 0:

            if len(frappe.get_all("BOM", filters={"item": item, "project": project})) == 0:
                msg = make_actual_bom(boq, project, item, children)
                msgs.append(msg)
            else:
                msgs.append("BOM already created for item '{0}' under project '{1}'".format(item, project))

    return "<br>".join(msgs)

def make_actual_bom(boq, project, item, children):
    b = frappe.new_doc("BOM")
    b.project = project
    b.item = item
    b.qty = frappe.db.get_value("BOQ Item",filters={"parent": boq, "item": item})

    for child in children:
        b.append("items", {
            "item_code": child.get("item"),
            "qty": child.qty
        })

    try:
        b.save()
        frappe.db.commit()
        return "BOM '{0}' created for item '{1}'".format(b.name, b.item)

    except Exception as e:
        frappe.db.rollback()
        return ""


def update_child_bom_links(project):
    boms = frappe.get_all("BOM", filters={"project": project}, fields=["name"])
    for bom in boms:
        bom_items = frappe.get_all("BOM Item", filters={"parent": bom.name},fields=["*"])
        for item in bom_items:
            bom_id = frappe.db.get_value("BOM", filters={"item": item.name}, fieldname = "name")
            if bom_id:
                frappe.db.set_value("BOM Item", {"item_code": item.item_code,"parent":bom.name}, "bom_no", bom_id)
                frappe.db.commit()




def activate_deactivate_bom(self, method):
    project_boqs = frappe.get_all("BOQ", fields=["*"], filters={"project": self.name})
    boq_boms = frappe.get_all("BOM", fields=["*"], filters={"project": self.name})
    # bom = frappe.get
    for b in project_boqs:
        if self.is_active == "Yes":
            frappe.db.set_value("BOQ", b.name, "is_active", 1)
        else:
            frappe.db.set_value("BOQ", b.name, "is_active", 0)

        frappe.db.commit()
    for i in boq_boms:
        if self.is_active == "Yes":
            frappe.db.set_value("BOM", i.name, "is_active", 1)
        else:
            frappe.db.set_value("BOM", i.name, "is_active", 0)

        frappe.db.commit()
