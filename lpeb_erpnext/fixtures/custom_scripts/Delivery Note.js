
var count = 0;
frappe.ui.form.on("Delivery Note", {
    "refresh": function(frm) {
        cur_frm.add_custom_button(__('Get Memo items'), function(){
            if(!cur_frm.doc.lpeb_item_details || cur_frm.doc.lpeb_item_details.length == 0){
                frappe.call({
                    "method": "lpeb_erpnext.api.get_memo_details_for_si_items",
                    "args": { "si_items": cur_frm.doc.items, "dispatch_order": cur_frm.doc.lpeb_dispatch_order },
                    "callback": function(r) {
                        console.log(r);
                        if (r.message) {
                            console.log("looping");
                            $.each(r.message, function(index, item) {
                                console.log("parent_item",r.message[index].parent_item, "count", count)
                                /*if (cur.frm.doc.lpeb_item_details != 1) {*/
                                var row = frappe.model.add_child(cur_frm.doc, "LPEB Delivery Note Item Detail", "lpeb_item_details");
                                row.item = item.item_code;
                                row.item_name = item.item_name;
                                row.qty = item.qty;
                                row.weight = item.weight;
                                row.uom = item.uom;
                                row.parent_item = item.parent_item;
                                count=count+1;
                            /*}*/
                            });

                        }
                        cur_frm.refresh_field("lpeb_item_details");
                    }
                });
            }
        });
    }
});

