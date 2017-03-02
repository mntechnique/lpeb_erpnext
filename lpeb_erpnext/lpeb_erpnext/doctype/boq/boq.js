// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOQ', {
	refresh: function(frm) {
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
    },

    validate: function(frm){
        frappe.call({
            method:"check_active_boq",
            doc:frm.doc,
            callback: function(r) {
            }
        });
    }

});
/*
frappe.ui.form.on("BOQ Item", "onload", function(frm) {
    frappe.call({
        method:"lpeb_erpnext.lpeb_erpnext.doctype.boq.boq.check_active_boq",
        args: {
            "project": frm.doc.project,
        },
});
*/

/*auto fetch UOM for Item*/
cur_frm.add_fetch("item","stock_uom","uom");



