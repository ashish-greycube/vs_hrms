# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_weekday
from frappe.model.document import Document
from hrms.utils.holiday_list import get_holiday_list_for_employee
from vs_hrms.api import check_is_public_holiday
from vs_hrms.salary import get_salary_structure_assignment_of_employee


class OvertimeRequestVS(Document):

	def validate(self):
		self.calculate_overtime_amount()

	def calculate_overtime_amount(self):
		if self.total_hours and self.overtime_type:
			overtime_doc = frappe.get_doc("Overtime Type",self.overtime_type)
			if overtime_doc.applicable_for_public_holiday==1:
				multiplication_factor = overtime_doc.public_holiday_multiplier
			else:
				multiplication_factor = overtime_doc.standard_multiplier
			per_hour_rate = 10
			# latest_salary_structure_assignment = get_salary_structure_assignment_of_employee(self.employee,self.overtime_date)
			# if latest_salary_structure_assignment:
			# 	per_hour_rate = frappe.db.get_value("Salary Structure Assignment",latest_salary_structure_assignment,"custom_per_hour_rate")
			# 	if per_hour_rate:
			print(multiplication_factor,"========multiplication_factor",per_hour_rate,"=======per_hour_rate",self.total_hours,self.total_hours * multiplication_factor or 0 * per_hour_rate)
			overtime_amount = self.total_hours * (multiplication_factor or 0) * per_hour_rate 
			self.calculated_overtime_amount = overtime_amount
			self.approved_amount = overtime_amount
	
	@frappe.whitelist()
	def get_overtime_type_based_on_date(self):
		is_public_holiday = check_is_public_holiday(self.employee,False,self.overtime_date)
		print(is_public_holiday,"---------------")
		if is_public_holiday:
			overtime_type = frappe.db.get_value("Overtime Type",{"applicable_for_public_holiday":1},"name")
			self.overtime_type = overtime_type
			return
		
		overtime_day = get_weekday(self.overtime_date)
		print(overtime_day,"==")
		if overtime_day and overtime_day != "Sunday":
			overtime_type = frappe.db.get_value("Overtime Type",{"custom_applicable_for":"Mon-Sat"},"name")
			print(overtime_type,"=====================")
			self.overtime_type = overtime_type
		elif overtime_day and overtime_day == "Sunday":
			overtime_type = frappe.db.get_value("Overtime Type",{"custom_applicable_for":"Sun"},"name")
			self.overtime_type = overtime_type

	@frappe.whitelist()
	def fetch_attendance_information(self):
		if self.employee and self.overtime_date:
			attendance = frappe.db.exists("Attendance",{"employee":self.employee,"attendance_date":self.overtime_date,"docstatus":1})
			if attendance:
				working_hours, ot_hours = frappe.db.get_value("Attendance",attendance,["working_hours","custom_ot_hours"])
				return attendance, working_hours, ot_hours