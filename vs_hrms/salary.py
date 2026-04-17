import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months, get_weekday

def create_payroll_week(payroll_period, week_start_date, week_end_date):
	pw = frappe.new_doc("Payroll Week VS")
	pw.payroll_period = payroll_period
	pw.week_start_date = week_start_date
	pw.week_end_date = week_end_date
	pw.save(ignore_permissions=True)
	return pw.name

def create_additional_salary(employee, payroll_date, salary_component, amount, ref_doc=None, refdoc_doctype=None):
	add_sal = frappe.new_doc("Additional Salary")
	add_sal.employee = employee
	add_sal.payroll_date = payroll_date
	add_sal.salary_component = salary_component
	add_sal.amount = amount
	add_sal.ref_doc = ref_doc or ''
	add_sal.refdoc_doctype = refdoc_doctype or ''
	add_sal.save(ignore_permissions=True)
	
	return add_sal.name

def get_salary_structure_assignment_of_employee(employee, from_date):
	salary_assignment = frappe.db.get_all("Salary Structure Assignment",
								  fields=["name", "salary_structure", "base"], filters={"from_date": ["<=", from_date], "employee":employee, "docstatus":1},
								  order_by = "from_date desc", limit=1)
	if len(salary_assignment) > 0:
		return salary_assignment[0].name
	else:
		frappe.throw(_("For {0} date No Salary Structure Assignment Found for {1} Employee").format(from_date, employee))


def validate_per_hour_rate_in_salary_assignment(self, method):
	if self.custom_per_hour_rate <= 0:
		frappe.throw(_("Per Hour Rate must be greater than zero."))
