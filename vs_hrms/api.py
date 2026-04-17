import frappe
import datetime
from frappe.utils import flt, getdate, date_diff, add_days, add_years, get_last_day, get_first_day, today, cint, nowdate
from hrms.hr.doctype.leave_policy_assignment.leave_policy_assignment import calculate_pro_rated_leaves
from erpnext.accounts.utils import get_fiscal_year
from hrms.hr.utils import round_earned_leaves
from hrms.utils.holiday_list import get_holiday_list_for_employee

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

from hrms.hr.utils import get_monthly_earned_leave as original_get_monthly_earned_leave
@frappe.whitelist()
def custom_get_monthly_earned_leave(
	date_of_joining,
	annual_leaves,
	frequency,
	rounding,
	period_start_date=None,
	period_end_date=None,
	pro_rated=True,
):
	print(frappe.get_installed_apps(),"--------------------------installed apps")
	# Check if the custom app is installed on the CURRENT site
	if "vs_hrms" in frappe.get_installed_apps():
		# RUN YOUR CUSTOM LOGIC
		print("Executing custom logic for this site")
		return my_new_calculation_logic(date_of_joining,
										annual_leaves,
										frequency,
										rounding,
										period_start_date=None,
										period_end_date=None,
										pro_rated=True,
										)
	else:
		# RUN THE ORIGINAL CORE LOGIC
		return original_get_monthly_earned_leave(date_of_joining,
												annual_leaves,
												frequency,
												rounding,
												period_start_date=None,
												period_end_date=None,
												pro_rated=True,
												)

def my_new_calculation_logic(date_of_joining, annual_leaves, frequency, rounding, period_start_date=None, period_end_date=None, pro_rated=True):
	earned_leaves = 0.0
	divide_by_frequency = {"Yearly": 1, "Half-Yearly": 2, "Quarterly": 4, "Monthly": 12, "Fortnightly": 26}
	if annual_leaves:
		earned_leaves = flt(annual_leaves) / divide_by_frequency[frequency]

		if pro_rated:
			if not (period_start_date or period_end_date):
				today_date = frappe.flags.current_date or getdate()
				period_start_date, period_end_date = get_sub_period_start_and_end(today_date, frequency)

			earned_leaves = calculate_pro_rated_leaves(
				earned_leaves, date_of_joining, period_start_date, period_end_date, is_earned_leave=True
			)

		earned_leaves = round_earned_leaves(earned_leaves, rounding)

	return earned_leaves

def get_sub_period_start_and_end(self, date, frequency, period_start_date=None, period_end_date=None):
	"""
	Determines the start and end of the specific period the 'date' falls into.
	For Fortnightly, this is relative to the Policy Assignment Start Date.
	"""
	if frequency != "Fortnightly":
		# Standard Frappe HRMS logic for calendar-based periods
		from frappe.utils.dateutils import (get_first_day, get_last_day, get_quarter_start, 
											get_quarter_ending, get_year_start, get_year_ending)
		
		# Helper functions for Half-Yearly (Semesters)
		def get_semester_start(d): return getdate(f"{d.year}-07-01") if d.month > 6 else getdate(f"{d.year}-01-01")
		def get_semester_end(d): return getdate(f"{d.year}-12-31") if d.month > 6 else getdate(f"{d.year}-06-30")

		return {
			"Monthly": (get_first_day(date), get_last_day(date)),
			"Quarterly": (get_quarter_start(date), get_quarter_ending(date)),
			"Half-Yearly": (get_semester_start(date), get_semester_end(date)),
			"Yearly": (get_year_start(date), get_year_ending(date)),
		}.get(frequency)

	# --- Custom Fortnightly Logic ---
	# We need the 'effective_from' as the anchor point for the 14-day cycles
	if not (period_start_date and period_end_date):
		frappe.throw("For Fortnightly frequency, 'period_start_date' and 'period_end_date' must be provided.")
	anchor_date = getdate(period_start_date)
	target_date = getdate(date)
	
	# Calculate days elapsed since policy start
	days_since_start = date_diff(target_date, anchor_date)
	
	if days_since_start < 0:
		# If date is before policy start, the period is the first 14 days
		return anchor_date, add_days(anchor_date, 13)

	# Find how many full fortnights have passed
	fortnights_passed = days_since_start // 14
	
	# Calculate the start and end of the current fortnight
	period_start = add_days(anchor_date, fortnights_passed * 14)
	period_end = add_days(period_start, 13) # 14 days including the start day
	
	return period_start, period_end

def check_doj_and_allocate_annual_leave_based_on_experince(self, method):
	if not self.get("earned_leave_schedule"):
		return
	
	is_annual_leave = frappe.db.get_value("Leave Type", self.leave_type, "custom_is_annual_leave")
	if is_annual_leave:
		# 1. Get Employee Date of Joining
		date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")
		if not date_of_joining:
			return
		
		if len(self.earned_leave_schedule) > 0:
			for schedule in self.earned_leave_schedule:
				allocation_date = getdate(schedule.allocation_date)
				# experience_in_years = date_diff(allocation_date, date_of_joining) / 365

				# Define the full month boundaries for the current row
				month_start = get_first_day(allocation_date)
				month_end = get_last_day(allocation_date)
				days_in_month = get_last_day(allocation_date).day

				# Determine specific anniversary milestones
				anniversaries = [add_years(date_of_joining, 2), add_years(date_of_joining, 5), add_years(date_of_joining, 10)]

				split_date = None
				for anniv_date in anniversaries:
					# Does the 2, 5, or 10-year mark hit DURING this month?
					if month_start < anniv_date <= month_end:
						split_date = anniv_date
						break

				if split_date:
					# Calculate allocation for the first part of the month
					days_in_old_tier = date_diff(split_date, month_start) + 1
					days_in_new_tier = days_in_month - days_in_old_tier

					experience_years_first_part = date_diff(month_start, date_of_joining) / 365
					experience_years_second_part = date_diff(month_end, date_of_joining) / 365

					print("experience_years_first_part-------------", experience_years_first_part)
					# Fetching the annual allocation for the first part of the month based on experience years
					annual_allocation_first_part = get_tier_rate(self.leave_type, experience_years_first_part)
					annual_allocation_second_part = get_tier_rate(self.leave_type, experience_years_second_part)

					current_allocation_first_part = (annual_allocation_first_part / (12 * days_in_month)) * days_in_old_tier
					current_allocation_second_part = (annual_allocation_second_part / (12 * days_in_month)) * days_in_new_tier

					schedule.number_of_leaves = current_allocation_first_part + current_allocation_second_part
				
				else:
					# --- Standard Calculation ---
					# If no split, use the rate applicable on the 'for_date'
					experience_on_allocation_date = date_diff(allocation_date, date_of_joining) / 365
					schedule.number_of_leaves = get_tier_rate(self.leave_type, experience_on_allocation_date) / 12


def get_tier_rate(leave_type,experience_years):
	if experience_years <= 2: 
		annual_allocation = frappe.db.get_value("Leave Type", leave_type, "custom_allocation_for_02_years") or 0
	if 2 < experience_years <= 5: 
		annual_allocation = frappe.db.get_value("Leave Type", leave_type, "custom_allocation_for_35_years") or 0
	if 5 < experience_years <= 10:
		annual_allocation = frappe.db.get_value("Leave Type", leave_type, "custom_allocation_for_610_years") or 0
	if experience_years > 10:
		annual_allocation = frappe.db.get_value("Leave Type", leave_type, "custom_allocation_for_11_years_and_more") or 0
	return annual_allocation

def set_leave_dates_for_hourly_leave_application(self, method):
	if self.custom_leave_based_on == "Hours" and self.custom_leave_date:
		self.from_date = self.custom_leave_date
		self.to_date = self.custom_leave_date
		self.half_day = 1

def validate_applicable_after_probation_period(self, method):
	# return
	if self.leave_type and self.employee:
		date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")
		experience_in_months = date_diff(getdate(self.from_date), date_of_joining) / 30
		allow_application_after = frappe.db.get_value("Leave Type", self.leave_type, "custom_allow_leave_application_after")
		if allow_application_after and experience_in_months < cint(allow_application_after):
			frappe.throw("This leave type is only applicable after completion of {0} months of service.".format(allow_application_after))
			
def validate_once_in_a_year_leave_application(self, method):
	if self.leave_type and self.employee:
		once_in_a_year = frappe.db.get_value("Leave Type", self.leave_type, "custom_allow_once_per_year")
		if once_in_a_year:
			current_fiscal_year = get_fiscal_year(self.from_date, as_dict=True)
			existing_leaves = frappe.db.get_all("Leave Application", 
										filters={
											"employee": self.employee,
											"leave_type": self.leave_type,
											"docstatus": 1,
											"from_date": ['between',[current_fiscal_year.year_start_date, current_fiscal_year.year_end_date]]
										})
			if existing_leaves:
				frappe.throw("You have already applied for this leave type once in the current year.")

def validate_leave_application_for_casual_employees(self, method):
	if self.employee:
		employment_type = frappe.db.get_value("Employee", self.employee, "employment_type")
		if employment_type == "Casual" and self.leave_type:
			frappe.throw("You are not allowed to apply for leave as you are a Casual employee.")

@frappe.whitelist()
def get_employee_for_bulk_leave_policy_assignment(doc,advanced_filters,leave_policy):
	doc = frappe.parse_json(doc)
	advanced_filters = frappe.parse_json(advanced_filters)
	from_date, to_date = get_from_to_date(doc)
	if leave_policy:
		applicable_based_on_years_of_experience = frappe.db.get_value("Leave Policy", leave_policy, "custom_applicable_based_on_years_of_experience")
		# experience_years_first_part = date_diff(month_start, date_of_joining) / 365
		if all_employees := frappe.get_list(
				"Employee",
				filters=get_filters(doc) + advanced_filters,
				fields=["name", "employee", "employee_name", "company", "department", "date_of_joining"],
			):

			employee_eligiable_based_on_experience = []
			if len(all_employees) > 0:
				for emp in all_employees:
					if applicable_based_on_years_of_experience:
						employee_experience = date_diff(getdate(today()), emp.date_of_joining) / 365
						if applicable_based_on_years_of_experience == "0-2 years":
							if employee_experience <= 2:
								employee_eligiable_based_on_experience.append(emp)
						elif applicable_based_on_years_of_experience == "3-5 years":
							if 2 < employee_experience <= 5:
								employee_eligiable_based_on_experience.append(emp)
						elif applicable_based_on_years_of_experience == "6-10 years":
							if 5 < employee_experience <= 10:
								employee_eligiable_based_on_experience.append(emp)
						elif applicable_based_on_years_of_experience == "10+ years":
							if employee_experience > 10:
								employee_eligiable_based_on_experience.append(emp)
					else:
						employee_eligiable_based_on_experience.append(emp)
				
				if len(employee_eligiable_based_on_experience) == 0:
					frappe.msgprint("No employees found with the given filters and experience criteria.")
					return []
				else:
					return get_employees_without_allocations(doc, employee_eligiable_based_on_experience, from_date, to_date)
	return []

def get_filters(doc):
	filter_fields = [
		"company",
		"employment_type",
		"branch",
		"department",
		"designation",
		"employee_grade",
	]
	filters = [["status", "=", "Active"]]

	for d in filter_fields:
		if doc.get(d):
			if d == "employee_grade":
				filters.append(["grade", "=", doc.get(d)])
			else:
				filters.append([d, "=", doc.get(d)])
	return filters

def get_employees_without_allocations(doc, all_employees: list, from_date: str, to_date: str) -> list:
	Allocation = frappe.qb.DocType("Leave Allocation")
	Employee = frappe.qb.DocType("Employee")

	query = (
		frappe.qb.from_(Allocation)
		.join(Employee)
		.on(Allocation.employee == Employee.name)
		.select(Employee.name)
		.distinct()
		.where((Allocation.docstatus == 1) & (Allocation.employee.isin([d.name for d in all_employees])))
	)

	if doc.dates_based_on == "Joining Date":
		from_date = Employee.date_of_joining

	query = query.where(
		(Allocation.from_date[from_date:to_date] | Allocation.to_date[from_date:to_date])
		| (
			(Allocation.from_date <= from_date)
			& (Allocation.from_date <= to_date)
			& (Allocation.to_date >= from_date)
			& (Allocation.to_date >= to_date)
		)
	)

	if doc.allocate_based_on_leave_policy and doc.leave_policy:
		leave_types = frappe.get_all(
			"Leave Policy Detail", {"parent": doc.leave_policy}, pluck="leave_type"
		)
		query = query.where(Allocation.leave_type.isin(leave_types))

	elif not doc.allocate_based_on_leave_policy and doc.leave_type:
		query = query.where(Allocation.leave_type == doc.leave_type)

	employees_with_allocations = query.run(pluck=True)
	return [d for d in all_employees if d.name not in employees_with_allocations]

def get_from_to_date(doc):
	if doc.dates_based_on == "Joining Date":
		return None, doc.to_date
	elif doc.dates_based_on == "Leave Period" and doc.leave_period:
		return frappe.db.get_value("Leave Period", doc.leave_period, ["from_date", "to_date"])
	else:
		return doc.from_date, doc.to_date
	
def set_leave_hours_and_regular_hours_for_attendance(self, method):
	if self.leave_application and self.leave_type:
		leave_hours = frappe.db.get_value("Leave Application", self.leave_application, "custom_total_leave_hours")
		self.custom_leave_hours = leave_hours
		if self.working_hours:
			self.custom_regular_hours = self.working_hours

def calculate_overtime_hours_and_set_if_attendance_on_holiday(self, method):
	per_day_hour = frappe.db.get_value("Company", self.company, "custom_working_hours_per_day") or 8
	if per_day_hour and self.working_hours and self.working_hours > per_day_hour:
		self.custom_ot_hours = self.working_hours - per_day_hour
		self.custom_regular_hours = per_day_hour
	else:
		self.custom_ot_hours = 0
		self.custom_regular_hours = self.working_hours

	if self.attendance_date :
		is_public_holiday = check_is_public_holiday(self.employee,raise_exception=False, date=self.attendance_date)
		if is_public_holiday:
			self.custom_is_public_holiday = 1
		else:
			self.custom_is_public_holiday = 0

def check_is_public_holiday(employee,raise_exception,date):
	holiday_list = get_holiday_list_for_employee(employee, raise_exception=raise_exception, as_on=date)
	if holiday_list:
		is_holiday = frappe.db.exists("Holiday", {"parent": holiday_list, "holiday_date": date, "is_half_day": 0, "weekly_off": 0}, cache=True)
		if is_holiday:
			return True
		else :
			return False