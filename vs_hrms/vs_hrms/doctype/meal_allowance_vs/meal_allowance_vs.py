# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from vs_hrms.salary import create_additional_salary
from frappe.utils import get_link_to_form


class MealAllowanceVS(Document):
	def before_submit(self):
		if self.status not in ["Approved", "Rejected"]:
			frappe.throw(_("Please Approve or Reject the Request Before Submitting."))

	def on_submit(self):
		self.create_meal_additional_salary()

	def create_meal_additional_salary(self):
		meal_compo = frappe.db.get_single_value("Vodafone Samoa Settings VS", "meal_allowance_earning")
		if not meal_compo:
			frappe.throw(_("Please Set Meal Allowance Salary Earning Component In Vodafone Samoa Settings VS"))
		add_sal = create_additional_salary(self.employee, self.meal_date, meal_compo, self.meal_amount, self.name, self.doctype)
		self.additional_salary_ref = add_sal
		frappe.msgprint(_("Additional Salary {0} Created.").format(get_link_to_form("Additional Salary", add_sal)))