// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOQ', {
	refresh: function(frm) {
<<<<<<< HEAD
        frm.add_custom_button(__('Create BOM'), function(frm){
        frappe.call({
            method: "lpeb_erpnext.api.make_bom_for_item",
            args: {
                "item": cur_frm.doc.items,
                "boq": cur_frm.doc.name
            },
            callback: function(r) {
                // if(!r.exc) {
                //     frappe.msgprint(r);
                //     console.log(r);
                // } else {
                //     frappe.msgprint(__("not fetched."));
                // }

            }
=======
        frm.add_custom_button(__('Create BOMs'), function(frm){
            frappe.call({
                method: "lpeb_erpnext.api.make_boms",
                args: {
                    "boq": cur_frm.doc.name,
                    "project": cur_frm.doc.project
                },
                callback: function(r) {
                    console.log(r);
                    frappe.msgprint(r.message);
                }
            });
>>>>>>> 9192124cdd6568cbd9677c7d9b9a775a82f5b8f5
        });
	},
    onload: function(frm) {
        cur_frm.set_query("parent_item", "items", function(doc, cdt, cdn) {
            return {
                filters: [
                    ["item_group", "in", ["Products", "Sub Assemblies"]]
                ]
            }
        }); 
    }
});



