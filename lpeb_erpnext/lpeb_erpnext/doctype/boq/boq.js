// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOQ', {
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
    },
    // project: function(frm){
    //     count = 0;
    //     for(var i=0;i<cur_frm.doc.items.length;i++){
    //         if(count < 1)
    //             count = cur_frm.doc.items.filter(function(i){
    //             i["parent_item"]== cur_frm.doc.items[i].parent_item && i["item"]== cur_frm.doc.items[i].item;})
    //         else
    //             frappe.msgprint("Error");
    //     }
    // }


});

/*auto fetch UOM for Item*/
cur_frm.add_fetch("item","stock_uom","uom");