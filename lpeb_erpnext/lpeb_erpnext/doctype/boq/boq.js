// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOQ', {
	refresh: function(frm) {
        frm.add_custom_button(__('Create BOM'), function(frm){
        frappe.call({
            method: "lpeb_erpnext.api.make_bom_for_item",
            args: {
                "item": cur_frm.doc.items[0]["item"],
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
        });
    });
	}
});



