// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('LPEB Dispatch Order', {
	refresh: function(frm) {
        cur_frm.set_query("item_code", "office_items", function() {
            return {
            	query: "lpeb_erpnext.api.bomitems_for_project",
                filters: {                   
                    "item_group": "Products",
                    "project_name": cur_frm.doc.project
                }
            }
        });
        cur_frm.set_query("item_code", "shop_floor_items", function() {
            // filter_list = ["Raw Materials","Sub Assemblies","Consumables"]
            return {
            	query: "lpeb_erpnext.api.bomitems_for_project",
                filters: {
                    "item_group": ["in", ["Raw Material", "Sub Assemblies"]],
                    "project_name": cur_frm.doc.project
                }
            }
        });
    }
});