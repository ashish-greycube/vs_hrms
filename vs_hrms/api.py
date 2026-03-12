import frappe

def calculate_allocated_hours(self, method):
    if self.total_leaves_allocated > 0:
        working_hours_per_day = frappe.db.get_value("Company", self.company, "custom_working_hours_per_day")
        total_allocated_hours = self.total_leaves_allocated * working_hours_per_day
        self.custom_total_hours_allocated = total_allocated_hours