import frappe

def calculate_allocated_hours(self, method):
    if self.total_leaves_allocated > 0:
        working_hours_per_day = frappe.db.get_value("Company", self.company, "custom_working_hours_per_day")
        total_allocated_hours = self.total_leaves_allocated * working_hours_per_day
        self.custom_total_hours_allocated = total_allocated_hours

def get_total_working_hours_between_dates(employee, from_date, to_date):
    attendance_list = frappe.db.get_all("Attendance",
                            fields=[{"COUNT": "working_hours", "as": "total_working_hours"}],
                            filters={
                                "employee": employee, 
                                "attendance_date" : ['between', [from_date, to_date]],
                                "status": "Present"
                            },
                            group_by="employee"
                        )
    
    if len(attendance_list) > 0:
        return attendance_list[0].total_working_hours
    
    return None

def get_total_leave_hours_based_on_leave_type_between_dates(employee, leave_type, from_date, to_date):
    attendance_list = frappe.db.get_all("Attendance",
                            fields=[{"COUNT": "working_hours", "as": "total_working_hours"}],
                            filters={
                                "employee": employee, 
                                "attendance_date" : ['between', [from_date, to_date]],
                                "status": "On Leave",
                                "leave_type" : leave_type
                            },
                            group_by="employee"
                        )
    
    if len(attendance_list) > 0:
        return attendance_list[0].total_working_hours
    
    return None