
let event_list = ["leave_policy", "employment_type", "branch", "department", "designation", "employee_grade", "from_date", "to_date", "leave_period", "allocate_based_on_leave_policy", "leave_type"]

event_list.forEach((event) => {
    frappe.ui.form.off("Leave Control Panel", event);
    })

frappe.ui.form.on("Leave Control Panel", {

    refresh: function (frm) {
        frm.trigger("get_employees");
    },

    leave_policy(frm) {
        frm.trigger("get_employees")
    },

    company: function (frm) {
        frm.trigger("get_employees");
    },

    employment_type(frm) {
		frm.trigger("get_employees");
	},

	branch(frm) {
		frm.trigger("get_employees");
	},

	department(frm) {
		frm.trigger("get_employees");
	},

	designation(frm) {
		frm.trigger("get_employees");
	},

	employee_grade(frm) {
		frm.trigger("get_employees");
	},

	dates_based_on(frm) {
		frm.trigger("get_employees");
	},

	from_date(frm) {
		frm.trigger("get_employees");
	},

	to_date(frm) {
		frm.trigger("get_employees");
	},

	leave_period(frm) {
		frm.trigger("get_employees");
	},

	allocate_based_on_leave_policy(frm) {
		frm.trigger("get_employees");
	},

	leave_type(frm) {
		frm.trigger("get_employees");
	},

    get_employees(frm) {
        frappe.call({
			method: "vs_hrms.api.get_employee_for_bulk_leave_policy_assignment",
			args: {
                doc: frm.doc,
				advanced_filters: frm.advanced_filters || [],
                leave_policy: frm.doc.leave_policy || "",
			},
		}).then((r) => {
			const columns = frm.events.get_employees_datatable_columns();
			hrms.render_employees_datatable(frm, columns, r.message);
		});
    }
})