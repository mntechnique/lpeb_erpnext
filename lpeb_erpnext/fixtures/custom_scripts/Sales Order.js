frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        frm.set_query("item_code", "items", function(doc, cdt, cdn) {
            return {
                filters: { "item_group": "Products" }
            };
        });
        if (cur_frm.doc.docstatus == 1) {
            add_dispatch_order_button(frm);
        }
    },
});


function add_dispatch_order_button(frm) {
    frm.add_custom_button(__('Dispatch Order'), function(){
        frappe.call({
            method: "lpeb_erpnext.api.make_dispatch_order_from_so",
            args: {"so": frm.doc.name},
            freeze: true,
            freeze_message: __("Creating Dispatch Order"),
            callback: function(r){
                if(!r.exc) {
                    frappe.msgprint(__(r.message));
                } else {
                    frappe.msgprint(__("Dispatch Order could not be created. <br /> " + r.exc));
                }
            }
        });
    }, __("Make"));
}