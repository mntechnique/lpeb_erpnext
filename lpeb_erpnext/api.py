import frappe
import json
from frappe.utils import get_url
from frappe import _
from erpnext.controllers.queries import get_filters_cond

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
        b.submit()
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
            bom_id = frappe.db.get_value("BOM", filters={"item": item.item_code}, fieldname = "name")
            if bom_id:
                frappe.db.set_value("BOM Item", "item_code" ,item.item_code, "bom_no", bom_id)
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


@frappe.whitelist()
def bomitems_for_project(doctype, txt, searchfield, start, page_len, filters):
    def get_item_group_clause(filters):
        item_group_clause = filters.get("item_group")

        if not item_group_clause:
            return ""

        out = ""

        if type(item_group_clause) == list:
            item_groups = item_group_clause[1]
            out = " and B.item_group in ({0})".format(",".join("'{0}'".format(g) for g in item_groups))
        else:
            out = " and B.item_group = '{0}'".format(item_group_clause)

        print "Output", out

        return out

    conditions = []
    return frappe.db.sql("""select distinct A.item, B.item_group
            from `tabBOQ Item` as A inner join tabItem as B on A.item = B.name inner join `tabBOQ` as C on A.parent = C.name
            where C.project = '{project_name}'
            {item_group_clause} and (A.item like %(txt)s)
        order by
            if(locate(%(_txt)s, A.item), locate(%(_txt)s, A.item), 99999),
            A.idx desc,
            A.item
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'project_name': filters.get("project_name"),
            'item_group_clause': get_item_group_clause(filters)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len
        })


@frappe.whitelist()
def make_dispatch_order_from_so(so):
    if not so:
        return {"exc": "Invalid Sales Order ID"}

    oso = frappe.get_doc("Sales Order", so)

    odo = frappe.new_doc("LPEB Dispatch Order")
    odo.sales_order = so
    odo.project = oso.project

    for soi in oso.items:
        odo.append("office_items", {
            "item_code": soi.item_code
        })

    try:
        odo.save()
        frappe.db.commit()
        return "Dispatch Order #{0} created successfully".format(odo.name)
    except Exception as e:
        raise

@frappe.whitelist()
def make_dn_from_dispatch_order(do):
    if not do:
        return {"exc": "Invalid Sales Order ID"}

    odo = frappe.get_doc("LPEB Dispatch Order", do)

    odn = frappe.new_doc("Delivery Note")
    odn.customer =  frappe.db.get_value("Sales Order", odo.sales_order, "customer")

    for doi in odo.shop_floor_items:

        odoi = frappe.get_doc("Item", {"item_code": doi.item_code})

        odn.append("items", {
            "item_code": doi.item_code,
            "item_name": odoi.item_name,
            "description": odoi.description,
            "qty": frappe.db.get_value("LPEB Dispatch Order Shop Floor Item", filters={"parent": do, "item_code": doi.item_code}, fieldname="qty")
        })

    try:
        odn.save()
        frappe.db.commit()
        return "Delivery Note #{0} created successfully.".format(odn.name)
    except Exception as e:
        raise

