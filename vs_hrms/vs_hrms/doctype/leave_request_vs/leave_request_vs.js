// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Request VS", {
	from_date(frm) {
        calculate_leave_days(frm);
	},

    to_date(frm) {
        calculate_leave_days(frm);
    },

    employee(frm) {
        frm.trigger("make_dashboard");
    },

    make_dashboard: function (frm) {
		let leave_details;
		let lwps;

		if (frm.doc.employee) {
            console.log(frm.doc.employee,'========')
			frappe.call({
				method: "hrms.hr.doctype.leave_application.leave_application.get_leave_details",
				async: false,
				args: {
					employee: frm.doc.employee,
					date: frm.doc.from_date || frm.doc.posting_date,
				},
				callback: function (r) {
					if (!r.exc && r.message["leave_allocation"]) {
						leave_details = r.message["leave_allocation"];
					}
					lwps = r.message["lwps"];
				},
			});

			$("div").remove(".form-dashboard-section.custom");

			frm.dashboard.add_section(
				frappe.render_template("leave_request_vs_dashboard", {
					data: leave_details,
				}),
				__("Allocated Leaves"),
			);
			frm.dashboard.show();

			let allowed_leave_types = Object.keys(leave_details);
			// lwps should be allowed for selection as they don't have any allocation
			allowed_leave_types = allowed_leave_types.concat(lwps);

			frm.set_query("leave_type", function () {
				return {
					filters: [["leave_type_name", "in", allowed_leave_types]],
				};
			});
		}
	},
});

function calculate_leave_days(frm) {
    if (frm.doc.leave_based_on == "Day") {
        let from_date = frm.doc.from_date
        let to_date = frm.doc.to_date
        if (from_date && to_date) {
            let no_of_leave_days = frappe.datetime.get_day_diff(to_date, from_date)
            frm.set_value("leave_days", (no_of_leave_days || 0)+1)
        }
        frappe.db.get_value("Company", frm.doc.company, "custom_working_hours_per_day")
        .then(r => {
            let working_hours_per_day = r.message.custom_working_hours_per_day
            if (!working_hours_per_day) {
                frappe.msgprint("Please set Custom Working Hours Per Day in Company master")
                return
            }
            let total_leave_hours = frm.doc.leave_days * working_hours_per_day
            frm.set_value("leave_hours", total_leave_hours)
        })
    }
}