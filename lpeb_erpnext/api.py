import frappe, json
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

@frappe.whitelist()
def make_bom_for_item(item, boq):
    b = frappe.new_doc("BOM")
    b.item = item
    b.qty = frappe.db.get_value("BOQ Item",filters={"parent": boq, "item": item})

    print "New BOM for ", item

    children = frappe.get_all("BOQ Item", filters={"parent": boq, "parent_item": item}, fields=["*"], order_by="idx")

    print "Children: ", "None" if len(children) == 0 else [c.item for c in children]

    for child in children:
        b.append("items", {
            "item_code": child.item_code,
            "qty": child.qty
        })
        make_bom_for_item(child.item, boq)

    b.save()
    frappe.db.commit()

    return "Done"
