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
        if (!frm.doc.__islocal) {
            add_custom_buttons(frm);
        }
        cur_frm.set_query("item_code", "additional_items", function() {
            return {
                query: "lpeb_erpnext.api.bomitems_for_project",
                filters: {                   
                    "item_group": "Consumable",
                    "project_name": cur_frm.doc.project
                }
            }
        });
    }, 
});


cur_frm.add_fetch("item_code", "stock_uom", "uom");

function add_custom_buttons(frm) {
    frm.add_custom_button(__('Delivery Note'), function(){
        frappe.call({
            method: "lpeb_erpnext.api.make_dn_from_dispatch_order",
            args: {"do": frm.doc.name},
            freeze: true,
            freeze_message: __("Creating Delivery Note"),
            callback: function(r){
                if(!r.exc) {
                    frappe.msgprint(__(r.message));
                } else {
                    frappe.msgprint(__("Delivery Note could not be created. <br /> " + r.exc));
                }
            }
        });
    }, __("Make"));
}