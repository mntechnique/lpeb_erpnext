// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('LPEB Dispatch Order', {
	refresh: function(frm) {
        cur_frm.set_query("item_code", "office_items", function() {
            return {
            	query: "",
                filters: [
                    ["Item", "item_group", "=", "Products"]
                ]
            }
    
        });
        cur_frm.set_query("item_code", "shop_floor_items", function() {
            return {
            	query: "",
                filters: [
                    ["Item", "item_group", "!=", "Products"]
                ]
            }
    
        });
    }
});
