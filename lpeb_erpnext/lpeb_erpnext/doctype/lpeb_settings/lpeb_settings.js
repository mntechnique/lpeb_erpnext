// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('LPEB settings', {
	refresh: function(frm) {
		frm.set_query("warehouse", "dispatch_warehouses", function(doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return{
				filters: [
					['Warehouse', 'is_group', '=', 0],
					['Warehouse', 'company', '=', d.company]
				]
			}
		});
	}
});
