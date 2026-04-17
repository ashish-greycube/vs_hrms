// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Overtime Request VS", {

    refresh(frm){
        console.log("---")
        frm.add_custom_button(
            __("Fetch Attendance Details"),
            function () {
                console.log("==")
                frm.trigger("fetch_data_from_attendance");
            }
        );
    },

	overtime_date(frm) {
        frm.trigger("fetch_overtime_type_based_on_date")
        frm.trigger("fetch_data_from_attendance")
	},

    from_time(frm) {
        frm.trigger("calculate_total_ot_hours")
    },

    to_time(frm) {
        frm.trigger("calculate_total_ot_hours")
    },

    fetch_overtime_type_based_on_date(frm) {
        if (frm.doc.overtime_date) {
            frm.call("get_overtime_type_based_on_date")
            .then (r => { 
                if (r.message) {
                    frm.set_value("overtime_type", r.message);
                }
            });
        }
    },

    calculate_total_ot_hours(frm) {
        if (frm.doc.from_time && frm.doc.to_time) {
            // convert from string to object(hh:mm:ss)
            let from_time = moment(frm.doc.from_time, "HH:mm:ss");
            let to_time = moment(frm.doc.to_time, "HH:mm:ss");
            let seconds = to_time.diff(from_time, 'seconds', true)
            frm.set_value("total_hours", seconds/3600);
        }
    },

    fetch_data_from_attendance(frm) {
        if (frm.doc.overtime_date) {
            frm.call("fetch_attendance_information").then(
                r => {
                    console.log(r.message,"-")
                    frm.set_value("attendance_reference",r.message[0])
                    frm.set_value("working_hours",r.message[1])
                    frm.set_value("overtime_hours",r.message[2])
                }
            )
        }
    }
});
