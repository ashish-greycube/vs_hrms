frappe.ui.form.on("Leave Allocation", {
    total_leaves_allocated(frm) {
        if (frm.doc.total_leaves_allocated > 0){
            frappe.db.get_value("Company", frm.doc.company, "custom_working_hours_per_day")
            .then(r => {
                let working_hours_per_day = r.message.custom_working_hours_per_day
                if (!working_hours_per_day) {
                    frappe.msgprint("Please set Custom Working Hours Per Day in Company master")
                    return
                }
                let total_allocated_hours = frm.doc.total_leaves_allocated * working_hours_per_day
                frm.set_value("custom_total_hours_allocated", total_allocated_hours)
            })
        }
    }
})