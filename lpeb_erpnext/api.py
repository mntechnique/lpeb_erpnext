import frappe
import json
from frappe.utils import get_url
from frappe import _
from erpnext.controllers.queries import get_filters_cond



# def update_child_bom_links(project):
# 	boms = frappe.get_all("BOM", filters={"project": project}, fields=["name"])
# 	for bom in boms:
# 		bom_items = frappe.get_all("BOM Item", filters={"parent": bom.name},fields=["*"])
# 		for item in bom_items:
# 			bom_id = frappe.db.get_value("BOM", filters={"item": item.item_code}, fieldname = "name")
# 			if bom_id:
# 				frappe.db.set_value("BOM Item", "item_code" ,item.item_code, "bom_no", bom_id)
# 				frappe.db.commit()


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
			"item_code": soi.item_code,
			"weight": soi.qty,
			"weight_uom": soi.stock_uom
		})

	try:
		odo.save()
		frappe.db.commit()
		return "Dispatch Order #{0} created successfully".format(odo.name)
	except Exception as e:
		raise


@frappe.whitelist()
def get_shop_floor_items(item_code=None, project=None):
	"""
		For supplied item_code, get children from BOM of supplied project.
	"""
	project_bom = frappe.get_all("BOM", filters={"project": project, "item": item_code})
	project_boq = frappe.db.get_value("BOQ", filters={"project":project})
	boq = frappe.get_doc("BOQ", project_boq)

	# if not project_bom:
	# 	frappe.throw("BOM for '{0}' not found.".format(item_code))

	project_bom_children = frappe.get_all("BOM Item", filters={"parent": project_bom[0].name}, fields=["*"])

	dispatch_orders_for_project = frappe.get_all("LPEB Dispatch Order", filters={"project": project})
	dispatch_order_names = [do["name"] for do in dispatch_orders_for_project]
	do_shop_floor_items = frappe.get_all("LPEB Dispatch Order Shop Floor Item", filters=[["parent", "in", dispatch_order_names]], fields=["*"])

	out_items = []

	for bom_child in project_bom_children:
		dispatched_qty = 0.0
		for sfi in do_shop_floor_items:
			if sfi.item_code == bom_child.item_code:
				dispatched_qty += sfi.qty

		item_group = frappe.db.get_value("Item",{"item_code": bom_child.item_code}, fieldname="item_group")
		abbr = frappe.db.get_value("Company",frappe.defaults.get_defaults().company, fieldname="abbr")

		warehouse = ""

		if item_group == "Raw Material":
			warehouse = frappe.db.get_value("Warehouse", filters={
						"warehouse_name": _("Raw Materials"),
						"company": frappe.defaults.get_defaults().company
					},fieldname="name")
		elif item_group == "Sub Assemblies":
			wh_name = project + " - FG"
			warehouse = frappe.db.get_value("Warehouse", filters={
						"warehouse_name": wh_name,
						"company": frappe.defaults.get_defaults().company
					},fieldname ="name")



		if bom_child.qty - dispatched_qty > 0:
			boq_item = [i for i in boq.items if i.item == bom_child.item_code ]
			print "unit weight", boq_item[0].unit_weight
			boq_weight= boq_item[0].unit_weight
			out_items.append({
				"item_code": bom_child.item_code,
				"qty": bom_child.qty - dispatched_qty,
				"uom": bom_child.stock_uom,
				"warehouse": warehouse,
				"unit_weight": boq_weight,
				"weight": boq_weight * (bom_child.qty - dispatched_qty),
				"parent_item": item_code
			})

	return out_items


@frappe.whitelist()
def lpeb_project_after_insert(self,method):
	abbr = frappe.db.get_value("Company",frappe.defaults.get_defaults()["company"],"abbr")

	def make_warehouse(name, project_name, parent_warehouse_name="", is_group=0):
		project_warehouse = frappe.new_doc("Warehouse")
		project_warehouse.warehouse_name = name
		project_warehouse.lpeb_project = project_name

		if parent_warehouse_name:
			project_warehouse.parent_warehouse = parent_warehouse_name

		if is_group == 1:
			project_warehouse.is_group = is_group

		project_warehouse.save()
		frappe.db.commit()

	make_warehouse(self.name, self.name, "", is_group=1)
	make_warehouse(self.name + " - QC", self.name, self.name + " - " + abbr)
	make_warehouse(self.name + " - FG", self.name, self.name + " - " + abbr)

@frappe.whitelist()
def lpeb_bom_autoname(self, method):
	if self.project:
		self.name = self.name.replace("BOM", "BOM-" + self.project)

@frappe.whitelist()
def create_qi_for_se(stock_entry_name):
	se_items = frappe.get_all("Stock Entry Item", filters={"parent": stock_entry_name}, fields=["*"])

	try:
		for se_item in se_items:
			se_item = frappe.get_doc("Stock Entry Item", {"name", se_item.name})

			if frappe.db.get_value("Item", se_item.item_code, "inspection_required_before_delivery") == 1:
				print "Adding QI for ", se_item.item_code
				qi = frappe.new_doc("Quality Inspection")
				qi.inspection_type = "In Process"
				qi.item_code = se_item.item_code
				qi.description = "Autogenerated QI"
				qi.sample_size = se_item.qty
				qi.inspected_by = frappe.session.user #Should be the Quality Inspector.
				qi.insert()
				frappe.db.commit()

	except Exception as e:
		frappe.db.rollback()
		frappe.throw("Quality Inspection entries were not created. <br><br> {0}".format(ex))

@frappe.whitelist()
def get_warehouses_for_project(project_name):
	warehouses = frappe.get_all("Warehouse",
		filters={"lpeb_project": project_name},
		fields=["*"])

	if len(warehouses) > 4:
		frappe.throw("There may be only 3 warehouses for a project. (Parent, FG, QC)<br> There appear to be {0}".format(len(warehouses)))

	fg_warehouse = [wh for wh in warehouses if "FG" in wh.name]
	#wip_warehouse = [wh for wh in warehouses if "WIP" in wh.name]
	qc_warehouse = [wh for wh in warehouses if "QC" in wh.name]

	#print "FG:", fg_warehouse, "WIP:", wip_warehouse

	return {
		"fg_warehouse": fg_warehouse[0],
		#"wip_warehouse": wip_warehouse[0],
		"qc_warehouse": qc_warehouse[0]
	}

@frappe.whitelist()
def get_memo_details_for_si_items(si_items, dispatch_order):
	si_items = json.loads(si_items)

	child_item_list = []
	do = frappe.get_doc("LPEB Dispatch Order", dispatch_order)

	for si_item in si_items:
		child_item_list = child_item_list + [sfi for sfi in do.shop_floor_items if sfi.parent_item == si_item.get("item_code")]

	print "Child Item List", child_item_list
	return child_item_list

# def get_dispatched_qty_for_so(so_name):
# 	so = frappe.get_doc("Sales Order", so_name)
# 	existing_dispatch_orders = frappe.get_all("LPEB Dispatch Order", filters={"sales_order": so_name})

# 	total_dispatched_qty = 0.0
	
# 	for soi in so.items:
