import frappe
from frappe import _
from hrms.hr.doctype.leave_policy_assignment.leave_policy_assignment import LeavePolicyAssignment, get_leave_type_details
from frappe.utils import getdate, add_to_date, flt, add_days, date_diff, today
from vs_hrms.api import get_tier_rate
# from vs_hrms.api import get_monthly_earned_leave

class VodafoneLeavePolicyAssignment(LeavePolicyAssignment):
    
	def grant_leave_alloc_for_employee(self):
		if self.leaves_allocated:
			frappe.throw(_("Leave already have been assigned for this Leave Policy Assignment"))
		else:
			leave_allocations = {}
			leave_type_details = get_leave_type_details()

			leave_policy = frappe.get_doc("Leave Policy", self.leave_policy)
			date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")

			for leave_policy_detail in leave_policy.leave_policy_details:
				leave_details = leave_type_details.get(leave_policy_detail.leave_type)

				if not leave_details.is_lwp:
					employee_experience = date_diff(self.effective_from, date_of_joining) / 365
					# For Annual Leave, allocate based on experience and annual allocation defined in the policy
					annual_allocation = get_tier_rate(leave_policy_detail.leave_type, employee_experience)
					leave_allocation, new_leaves_allocated = self.create_leave_allocation(
						annual_allocation,
						leave_details,
						date_of_joining,
					)
					leave_allocations[leave_details.name] = {
						"name": leave_allocation,
						"leaves": new_leaves_allocated,
					}
			self.db_set("leaves_allocated", 1)
			return leave_allocations

	# def get_earned_leave_schedule(self,annual_allocation, leave_details, date_of_joining, new_leaves_allocated):
		
	# 	print("Inside the overridden method for Leave Policy Assignment----------")
	# 	print(leave_details.earned_leave_frequency)
	# 	print(leave_details, annual_allocation, date_of_joining, new_leaves_allocated)
	# 	"""
	# 	Overriding the standard method to include Fortnightly logic.
	# 	"""
	# 	# If the frequency is NOT Fortnightly, use the standard HRMS logic
	# 	if leave_details.earned_leave_frequency != "Fortnightly":
	# 		return super().get_earned_leave_schedule(annual_allocation, leave_details, date_of_joining, new_leaves_allocated)

	# 	# Custom Fortnightly Logic
	# 	schedule = []
	# 	# annual_allocation = 0

	# 	from hrms.hr.utils import (
	# 		get_expected_allocation_date_for_period,
	# 		get_monthly_earned_leave,
	# 		get_sub_period_start_and_end,
	# 	)
	# 	today = getdate(frappe.flags.current_date) or getdate()
	# 	from_date = last_allocated_date = getdate(self.effective_from)
	# 	to_date = getdate(self.effective_to)

	# 	periodically_earned_leave = get_monthly_earned_leave(
	# 		date_of_joining,
	# 		annual_allocation,
	# 		leave_details.earned_leave_frequency,
	# 		leave_details.rounding,
	# 		self.effective_from,
	# 		self.effective_to,
	# 		pro_rated=False,
	# 	)
	# 	date = get_expected_allocation_date_for_period(
	# 		leave_details.earned_leave_frequency,
	# 		leave_details.allocate_on_day,
	# 		from_date,
	# 		date_of_joining,
	# 	)
	# 	print(new_leaves_allocated,"--------------------------new_leaves_allocated")
	# 	print(date,"--------------------------expected date")
	# 	print(periodically_earned_leave,"--------------------------periodically_earned_leave")
		
	# 	schedule = []
	# 	if new_leaves_allocated:
	# 		print(new_leaves_allocated,"--------------------------new_leaves_allocated++++++++++++++++++++")
	# 		schedule.append(
	# 			{
	# 				"allocation_date": today,
	# 				"number_of_leaves": new_leaves_allocated,
	# 				"is_allocated": 1,
	# 				"allocated_via": "Leave Policy Assignment",
	# 				"attempted": 1,
	# 			}
	# 		)
	# 		last_allocated_date = get_sub_period_start_and_end(today, leave_details.earned_leave_frequency)[1]
	# 		print(last_allocated_date,"--------------------------last_allocated_date")
		
	# 	print(date, to_date, "==============================")
	# 	while date <= to_date:
	# 		date_already_passed = today > date
	# 		if date >= last_allocated_date:
	# 			row = {
	# 				"allocation_date": date,
	# 				"number_of_leaves": periodically_earned_leave,
	# 				"is_allocated": 1 if date_already_passed else 0,
	# 				"allocated_via": "Leave Policy Assignment" if date_already_passed else None,
	# 				"attempted": 1 if date_already_passed else 0,
	# 			}
	# 			schedule.append(row)
	# 		date = get_expected_allocation_date_for_period(
	# 			leave_details.earned_leave_frequency,
	# 			leave_details.allocate_on_day,
	# 			add_to_date(date, days=14),
	# 			date_of_joining,
	# 		)
	# 		print(date, "==============================,increased date")
	# 	if from_date < getdate(date_of_joining):
	# 		pro_rated_period_start, pro_rated_period_end = get_sub_period_start_and_end(
	# 			date_of_joining, leave_details.earned_leave_frequency
	# 		)
	# 		pro_rated_earned_leave = get_monthly_earned_leave(
	# 			date_of_joining,
	# 			annual_allocation,
	# 			leave_details.earned_leave_frequency,
	# 			leave_details.rounding,
	# 			pro_rated_period_start,
	# 			pro_rated_period_end,
	# 		)
	# 		schedule[0]["number_of_leaves"] = pro_rated_earned_leave

	# 	print(schedule, "schedule==============================")
	# 	return schedule
	
	# def get_periods_passed(self, earned_leave_frequency, current_date, from_date, consider_current_period):
	# 	print("from vs hrms-----------")
	# 	# 1. Handle the standard Monthly-based frequencies
	# 	if earned_leave_frequency != "Fortnightly":
	# 		frequency_config = {
	# 			"Monthly": (12, 1),
	# 			"Quarterly": (4, 3),
	# 			"Half-Yearly": (2, 6),
	# 			"Yearly": (1, 12),
	# 		}
			
	# 		periods_per_year, months_per_period = frequency_config.get(earned_leave_frequency)

	# 		return calculate_periods_passed(
	# 			current_date, from_date, periods_per_year, months_per_period, consider_current_period
	# 		)

	# 	# 2. Handle the Custom Fortnightly Logic (Day-based)
	# 	# Calculate the total days between the start date and current date
	# 	days_diff = date_diff(current_date, from_date)
		
	# 	if days_diff < 0:
	# 		return 0

	# 	# A period is 14 days. 
	# 	# Using integer division // to get completed 14-day blocks
	# 	periods_passed = days_diff // 14

	# 	# If the system should count the period currently in progress as "passed"
	# 	if consider_current_period and (days_diff % 14 > 0):
	# 		periods_passed += 1
	# 	print(periods_passed, "periods_passed==============================")
	# 	return periods_passed
	
	# def get_sub_period_start_and_end(self, date, frequency):
	# 	print("====================================")
	# 	"""
	# 	Determines the start and end of the specific period the 'date' falls into.
	# 	For Fortnightly, this is relative to the Policy Assignment Start Date.
	# 	"""
	# 	if frequency != "Fortnightly":
	# 		# Standard Frappe HRMS logic for calendar-based periods
	# 		from frappe.utils.dateutils import (get_first_day, get_last_day, get_quarter_start, 
	# 											get_quarter_ending, get_year_start, get_year_ending)
			
	# 		# Helper functions for Half-Yearly (Semesters)
	# 		def get_semester_start(d): return getdate(f"{d.year}-07-01") if d.month > 6 else getdate(f"{d.year}-01-01")
	# 		def get_semester_end(d): return getdate(f"{d.year}-12-31") if d.month > 6 else getdate(f"{d.year}-06-30")

	# 		return {
	# 			"Monthly": (get_first_day(date), get_last_day(date)),
	# 			"Quarterly": (get_quarter_start(date), get_quarter_ending(date)),
	# 			"Half-Yearly": (get_semester_start(date), get_semester_end(date)),
	# 			"Yearly": (get_year_start(date), get_year_ending(date)),
	# 		}.get(frequency)

	# 	# --- Custom Fortnightly Logic ---
	# 	# We need the 'effective_from' as the anchor point for the 14-day cycles
	# 	anchor_date = getdate(self.effective_from)
	# 	target_date = getdate(date)
		
	# 	# Calculate days elapsed since policy start
	# 	days_since_start = date_diff(target_date, anchor_date)
		
	# 	if days_since_start < 0:
	# 		# If date is before policy start, the period is the first 14 days
	# 		return anchor_date, add_days(anchor_date, 13)

	# 	# Find how many full fortnights have passed
	# 	fortnights_passed = days_since_start // 14
		
	# 	# Calculate the start and end of the current fortnight
	# 	period_start = add_days(anchor_date, fortnights_passed * 14)
	# 	period_end = add_days(period_start, 13) # 14 days including the start day
		
	# 	return period_start, period_end