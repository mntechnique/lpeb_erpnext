frappe.ui.form.on("Sales Invoice", {
    "refresh": function(frm) {
        cur_frm.add_custom_button(__('Get Memo items'), function(){
            if(!cur_frm.doc.lpeb_item_details || cur_frm.doc.lpeb_item_details.length == 0){
                frappe.call({
                    "method": "lpeb_erpnext.api.get_memo_details_for_si_items",
                    "args": { "si_items": cur_frm.doc.items, "dispatch_order": cur_frm.doc.lpeb_dispatch_order },
                    "callback": function(r) {
                    console.log("sales Invoice return",r)
                        if (r.message) {
                            $.each(r.message, function(index, item) {
                                var row = frappe.model.add_child(cur_frm.doc, "LPEB Sales Invoice Item Detail", "lpeb_item_details");
                                row.item = item.item_code;
                                row.item_name = item.item_name;
                                row.weight = item.weight;
                                row.uom = item.uom;
                                row.parent_item = item.parent_item;
                            });
                        }
                cur_frm.refresh_field("lpeb_item_details");
                    }
                });
            }
        });
    }
});
