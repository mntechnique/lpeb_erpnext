import frappe
import json
from frappe.utils import get_url
from frappe import _



# @frappe.whitelist()
# def create_bom(boq):
#     for project in frappe.get_all("BOQ Item", fields=["*"],filters={"parent": boq}):
#         # if project.parent_item:
#         # items[i['idx'] for i in items]
#         # pitems contain all parent_items
#         pitems = [i["parent_item"] for i in project if i["parent_item"] != ""]
#         unique_items = list(set(pitems))

#         #frappe.get_all("BOQ Item", fields=["*"],filters=[[parent_item]])

# @frappe.whitelist()
# def make_bom_for_item(item, boq):
#     out = ""
#     children = frappe.get_all("BOQ Item", filters={"parent": boq, "parent_item": item}, fields=["*"], order_by="idx")

#     if len(children) > 0:
#         b = frappe.new_doc("BOM")
#         b.item = item
#         b.qty = frappe.db.get_value("BOQ Item",filters={"parent": boq, "item": item})
        
#         print "New BOM for ", item
#         print "Children: ", "None" if len(children) == 0 else [c.item for c in children]

#         for child in children:
#             print "Child for ", item, ": Child: ", child

#             # b.append("items", {
#             #     "item_code": child.item_code,
#             #     "qty": child.qty
#             # })
#             c = make_bom_for_item(child.item, boq)
#             print c

#         # b.save()
#         # frappe.db.commit()
#         out = "BOM created for {0}".format(item)
#     else:
#         out = "No BOM for {0}".format(item)
    
#     return out

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

        
