import frappe
import datetime
from frappe import _
from frappe.utils import flt, cint, getdate, nowdate
from hrms.hr.doctype.leave_application.leave_application import (LeaveApplication,
																 get_leave_allocation_records, get_leaves_pending_approval_for_period, 
																 get_leave_approver, get_number_of_leave_days, get_allocation_expiry_for_cf_leaves, 
																 get_remaining_leaves,get_manually_expired_leaves, is_lwp, get_leave_entries)

class VodafoneLeaveApplicationMixin(LeaveApplication):
	### This function is copied from standard hrms.leave_application file.
	def validate_balance_leaves(self):
		# if self.custom_leave_based_on and self.custom_leave_based_on == "Hours":
		precision = cint(frappe.db.get_single_value("System Settings", "float_precision")) or 2
		
		# If application is based on hours, calculate total_leave_days based on custom_total_leave_hours and working hours per day of the company
		if self.custom_total_leave_hours:
			total_leave_days = flt(self.custom_total_leave_hours) / (frappe.db.get_value("Company", self.company, "custom_working_hours_per_day") or 8)
			self.total_leave_days = flt(total_leave_days)


		if self.total_leave_days <= 0:
			frappe.throw(
				_(
					"The day(s) on which you are applying for leave are holidays. You need not apply for leave."
				)
			)

		if not is_lwp(self.leave_type):
			### changes in standard function is..use get_leave_balance_on function from this file instead of standard hrms.leave_application file. 
			leave_balance = get_leave_balance_on(
				self.employee,
				self.leave_type,
				self.from_date,
				self.to_date,
				consider_all_leaves_in_the_allocation_period=True,
				for_consumption=True,
			)
			### Chnages end here, rest of the code is standard code from hrms.leave_application file
			leave_balance_for_consumption = flt(
				leave_balance.get("leave_balance_for_consumption"), precision
			)
			print(leave_balance_for_consumption,"============leave_balance_for_consumption")
			if self.status != "Rejected" and (
				leave_balance_for_consumption < self.total_leave_days or not leave_balance_for_consumption
			):
				self.show_insufficient_balance_message(leave_balance_for_consumption)

### This function is copied from standard hrms.leave_application file.
@frappe.whitelist()
def get_leave_details(employee, date, for_salary_slip=False):
	allocation_records = get_leave_allocation_records(employee, date)
	leave_allocation = {}
	precision = cint(frappe.db.get_single_value("System Settings", "float_precision")) or 2

	for d in allocation_records:
		allocation = allocation_records.get(d, frappe._dict())
		to_date = date if for_salary_slip else allocation.to_date
		remaining_leaves = get_leave_balance_on(
			employee,
			d,
			date,
			to_date=to_date,
			consider_all_leaves_in_the_allocation_period=False if for_salary_slip else True,
		)

		### changes starts here. get_leaves_for_period is custom function created in this file which is used to fetch leaves taken for the given periods.
		leaves_taken = get_leaves_for_period(employee, d, allocation.from_date, to_date) * -1
		### customization ends here, rest of the code is standard code from hrms.leave_application
		leaves_pending = get_leaves_pending_approval_for_period(employee, d, allocation.from_date, to_date)
		expired_leaves = allocation.total_leaves_allocated - (remaining_leaves + leaves_taken)

		leave_allocation[d] = {
			"total_leaves": flt(allocation.total_leaves_allocated, precision),
			"expired_leaves": flt(expired_leaves, precision) if expired_leaves > 0 else 0,
			"leaves_taken": flt(leaves_taken, precision),
			"leaves_pending_approval": flt(leaves_pending, precision),
			"remaining_leaves": flt(remaining_leaves, precision),
		}

	# is used in set query
	lwp = frappe.get_list("Leave Type", filters={"is_lwp": 1}, pluck="name")

	return {
		"leave_allocation": leave_allocation,
		"leave_approver": get_leave_approver(employee),
		"lwps": lwp,
	}

### This is copied from standard hrms.leave_application file with a custom function get_leaves_for_period created in this file to fetch leaves taken for the given period, rest of the code is standard code from hrms.leave_application file
def get_leaves_for_period(
	employee: str,
	leave_type: str,
	from_date: datetime.date,
	to_date: datetime.date,
	skip_expired_leaves: bool = True,
) -> float:
	leave_entries = get_leave_entries(employee, leave_type, from_date, to_date)
	leave_days = 0

	for leave_entry in leave_entries:
		inclusive_period = leave_entry.from_date >= getdate(from_date) and leave_entry.to_date <= getdate(
			to_date
		)

		if inclusive_period and leave_entry.transaction_type == "Leave Encashment":
			leave_days += leave_entry.leaves

		elif (
			inclusive_period
			and leave_entry.transaction_type == "Leave Allocation"
			and leave_entry.is_expired
			and not skip_expired_leaves
		):
			leave_days += leave_entry.leaves

		elif leave_entry.transaction_type == "Leave Application":
			if leave_entry.from_date < getdate(from_date):
				leave_entry.from_date = from_date
			if leave_entry.to_date > getdate(to_date):
				leave_entry.to_date = to_date

			### changes start here
			# half_day = 0
			# half_day_date = None

			# fetch half day date for leaves with half days
			# half_day, half_day_date = frappe.db.get_value(
			# 	"Leave Application", leave_entry.transaction_name, ["half_day", "half_day_date"])
			
			# if leave_entry.leaves % 1:
			# 	half_day = 1
			# 	half_day_date = frappe.db.get_value(
			# 		"Leave Application", leave_entry.transaction_name, "half_day_date"
			# 	)

			# if half_day and half_day_date:
			# 	print(half_day, half_day_date,"============half_day, half_day_date")
			# 	leave_days += (
			# 		get_number_of_leave_days(
			# 			employee,
			# 			leave_type,
			# 			leave_entry.from_date,
			# 			leave_entry.to_date,
			# 			half_day,
			# 			half_day_date,
			# 			holiday_list=leave_entry.holiday_list,
			# 		)
			# 		* -1
			# 	)
			# else:
			leave_days += leave_entry.leaves
			### changes end here

	return leave_days

@frappe.whitelist()
### This function is standard hrms function, copied here to use custom function get_leave_for_period 
def get_leave_balance_on(
	employee: str,
	leave_type: str,
	date: datetime.date,
	to_date: datetime.date | None = None,
	consider_all_leaves_in_the_allocation_period: bool = False,
	for_consumption: bool = False,
):
	"""
	Returns leave balance till date
	:param employee: employee name
	:param leave_type: leave type
	:param date: date to check balance on
	:param to_date: future date to check for allocation expiry
	:param consider_all_leaves_in_the_allocation_period: consider all leaves taken till the allocation end date
	:param for_consumption: flag to check if leave balance is required for consumption or display
			eg: employee has leave balance = 10 but allocation is expiring in 1 day so employee can only consume 1 leave
			in this case leave_balance = 10 but leave_balance_for_consumption = 1
			if True, returns a dict eg: {'leave_balance': 10, 'leave_balance_for_consumption': 1}
			else, returns leave_balance (in this case 10)
	"""

	if not to_date:
		to_date = nowdate()

	allocation_records = get_leave_allocation_records(employee, date, leave_type)
	allocation = allocation_records.get(leave_type, frappe._dict())
	end_date = (
		allocation.to_date if (allocation and cint(consider_all_leaves_in_the_allocation_period)) else date
	)
	cf_expiry = get_allocation_expiry_for_cf_leaves(employee, leave_type, to_date, allocation.from_date)

	### get_leaves_for_period is custom function created in this file which is used to fetch leaves taken for the given periods.
	leaves_taken = get_leaves_for_period(employee, leave_type, allocation.from_date, end_date)
	### customization ends here, rest of the code is standard code from hrms.leave_application
	manually_expired_leaves = get_manually_expired_leaves(
		employee, leave_type, allocation.from_date, end_date
	)

	remaining_leaves = get_remaining_leaves(
		allocation, leaves_taken, date, cf_expiry, manually_expired_leaves
	)

	if for_consumption:
		return remaining_leaves
	else:
		return remaining_leaves.get("leave_balance")