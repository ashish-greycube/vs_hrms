import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months, get_weekday


def validate_first_payroll_start_date(self, method):
	if self.custom_first_payroll_start_date and self.start_date:
		weekday = get_weekday(getdate(self.custom_first_payroll_start_date))

		print(getdate(self.custom_first_payroll_start_date).weekday(), "=========weekdayyyy=============")
		print(weekday, "=========weekdayyyy=============")

		if weekday != "Sunday":
			frappe.throw(_("Payroll start day must be <b>Sunday</b>."))

		first_payroll_date_month_year = getdate(self.custom_first_payroll_start_date).strftime("%B %Y")
		payroll_start_date_month_year = getdate(self.start_date).strftime("%B %Y")

		prev_month_date = add_months(getdate(self.start_date), -1)
		prev_date_month_year = getdate(prev_month_date).strftime("%B %Y")

		print(first_payroll_date_month_year, "===first_payroll_date_month_year===", payroll_start_date_month_year, "===payroll_start_date_month_year===", prev_date_month_year, "==prev_date_month_year==")

		if first_payroll_date_month_year not in [payroll_start_date_month_year, prev_date_month_year]:
			frappe.throw(_("Invalid First Payroll Start Date. <br> <b>Allowed Months: {0}, {1} </b>".format(prev_date_month_year, payroll_start_date_month_year)))

def set_payroll_period_weeks(self, method):
	print("=======after_insert=========")
	print(self.name, "======name")

	payroll_start_date = self.custom_first_payroll_start_date
	payroll_end_date = self.end_date

	week_start_date = payroll_start_date
	week_end_date = add_days(week_start_date, 13)
	
	self.custom_payroll_periods = []
	while payroll_end_date >= week_start_date and week_end_date < self.end_date:
		# print(week_start_date, "====week_start_date===", week_end_date, "===week_end_date====")
		
		### creating payroll week docs ###
		# week_name = create_payroll_week(self.name, week_start_date, week_end_date)

		### add payroll weeks in childtable ###
		self.append("custom_payroll_periods", {
			"payroll_week_start_date" : week_start_date,
			"payroll_week_end_date" : week_end_date,
			# "week_name" : week_name
		})

		week_start_date = add_days(week_end_date, 1)
		week_end_date = add_days(week_start_date, 13)


def create_payroll_week(payroll_period, week_start_date, week_end_date):
	pw = frappe.new_doc("Payroll Week VS")
	pw.payroll_period = payroll_period
	pw.week_start_date = week_start_date
	pw.week_end_date = week_end_date
	pw.save(ignore_permissions=True)
	return pw.name

def create_additional_salary(employee, payroll_date, salary_component, amount):
	add_sal = frappe.new_doc("Additional Salary")
	add_sal.employee = employee
	add_sal.payroll_date = payroll_date
	add_sal.salary_component = salary_component
	add_sal.amount = amount
	add_sal.save(ignore_permissions=True)

def get_salary_structure_assignment_of_employee(employee, from_date):
	salary_assignment = frappe.db.get_all("Salary Structure Assignment",
								  fields=["name", "salary_structure", "base"], filters={"from_date": ["<=", from_date], "employee":employee, "docstatus":1},
								  order_by = "from_date desc", limit=1)
	if len(salary_assignment) > 0:
		return salary_assignment[0].name
	else:
		frappe.throw(_("For {0} date No Salary Structure Assignment Found for {1} Employee").format(from_date, employee))

def calculate_ot_hours(employee, from_date, to_date):
	pass

def calculate_tax_based_on_total_salary(total_pay_till_day, current_month_salary):
	if total_pay_till_day > 25000:
		pass
	elif total_pay_till_day < 25000 and total_pay_till_day > 20000:
		pass
	elif total_pay_till_day > 20000:
		pass
	else:
		pass

