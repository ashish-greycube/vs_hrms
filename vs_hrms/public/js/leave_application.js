frappe.ui.form.on("Leave Application", {

    leave_type: function (frm) {
		frm.trigger("make_dashboard");
		if (frm.doc.leave_type) {
			frappe.db.get_value("Leave Type", frm.doc.leave_type, "custom_apply_leave_in_hours")
			.then((r) => {
				if (r.message.custom_apply_leave_in_hours) {
					frm.set_value("custom_leave_based_on", "Hours");
				} else {
					frm.set_value("custom_leave_based_on", "Days");
				}
			})
		} else {
			frm.set_value("custom_leave_based_on", "");
		}
	},

    employee: function (frm) {
		frm.trigger("make_dashboard");
	},

    make_dashboard: function (frm) {
		let leave_details;
		let lwps;

		if (frm.doc.employee) {
			frappe.call({
				method: "vs_hrms.leave_application.get_leave_details",
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
				frappe.render_template("leave_application_dashboard", {
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

})