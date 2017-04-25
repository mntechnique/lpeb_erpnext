frappe.ui.form.on("BOM", {
	"item_code": function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row["bom_no"] == "ABC123";
		console.log("Tried setting BOMNO", "ABC123");
	}
});