
frappe.ui.form.on("Delivery Note", {
    "refresh": function(frm) {
            frappe.call({
                "method": "lpeb_erpnext.api.get_memo_details_for_si_items",
                "args": { "si_items": cur_frm.doc.items, "dispatch_order": cur_frm.doc.lpeb_dispatch_order },
                "callback": function(r) {
        console.log(r);
                    if (r.message) {
            console.log("looping");
                        $.each(r.message, function(index, item) {
                            var row =
 frappe.model.add_child(cur_frm.doc, "LPEB Delivery Note Item Detail", "lpeb_item_details");
                            row.item = item.item_code;
            row.item_name = item.item_name;
                            row.weight = item.weight;
                            row.uom = item.uom;
                        });

                    }
                    cur_frm.refresh_field("lpeb_item_details");
                }
            });
    }
});

cur_frm.add_fetch("Item", "item_name","item_name");