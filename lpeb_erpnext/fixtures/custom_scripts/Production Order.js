frappe.ui.form.on("Production Order", {
    "project": function(frm) {
        frappe.call({
            method: "lpeb_erpnext.api.get_warehouses_for_project",
            args: { project_name: cur_frm.doc.project},
            callback: function(r) {
                if (r.message) {
                    cur_frm.set_value("fg_warehouse", r.message.qc_warehouse.name);
                }
            }
        })
    }
});