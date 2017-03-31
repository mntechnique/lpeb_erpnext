//Copyright (c) 2016, MN Technique and contributors
//For license information, please see license.txt

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

frappe.ui.form.on("LPEB Dispatch Order Office Item", {
    qty: function(doc, cdt, cdn) {
        var row = locals[cdt][cdn];

        if (row["qty"] > row["max_qty"]) {
            frappe.msgprint("Qty cannot exceed " + row["max_qty"])
            row["qty"] = 0
        }
    }

});

function add_custom_buttons(frm) {
    if (cur_frm.doc.docstatus == 1) {
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
    
    if (cur_frm.doc.docstatus == 0) {
        frm.add_custom_button(__('Fetch Shop Floor items'), function(){
            if ([undefined, "", null].indexOf(cur_frm.doc.project) != -1) {
                frappe.msgprint("Please select Project before fetching items.")
            } else if (cur_frm.doc.sales_order == "") {
                frappe.msgprint("Please select Sales Order before fetching items.")
            } else {
                for (var i = 0; i<cur_frm.doc.office_items.length; i++){
                    fetch_shop_item(cur_frm, cur_frm.doc.office_items[i].item_code);
                }
            }
        });
    }
}

function fetch_shop_item(frm,item_code) {
    frappe.call({
        method: "lpeb_erpnext.api.get_child_items_from_bom",
        args: {
            "item_code": item_code,
            "project": cur_frm.doc.project
        },
        callback: function(r) {
            $.each(r.message, function(i, d) {
                var existing_items = [];
                if (cur_frm.doc.shop_floor_items) {
                    existing_items = cur_frm.doc.shop_floor_items.filter(function(x) { return x["item_code"] == d["item_code"]});
                }

                if (existing_items.length == 0) {
                    var row = frappe.model.add_child(cur_frm.doc, "LPEB Dispatch Order Shop Floor Item", "shop_floor_items");
                    row.item_code = d.item_code;
                    row.qty = d.qty;
                    row.uom = d.uom;
                    row.warehouse = d.warehouse;
                    row["max_qty"] = d.qty;
                }
            });
            refresh_field("shop_floor_items");
        }
    });
}



function set_shop_floor_items(r){
    cur_frm.set_value("item_code", "shop_floor_items", r.item_code);
}

cur_frm.add_fetch("item_code", "stock_uom", "uom");
