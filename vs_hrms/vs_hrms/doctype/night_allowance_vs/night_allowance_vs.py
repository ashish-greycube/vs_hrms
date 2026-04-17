# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from vs_hrms.salary import create_additional_salary
from frappe.utils import get_link_to_form


class NightAllowanceVS(Document):
	def before_submit(self):
		if self.status not in ["Approved", "Rejected"]:
			frappe.throw(_("Please Approve or Reject the Request Before Submitting."))

	def on_submit(self):
		self.create_night_additional_salary()

	def create_night_additional_salary(self):
		night_compo = frappe.db.get_single_value("Vodafone Samoa Settings VS", "night_allowance_earning")
		if not night_compo:
			frappe.throw(_("Please Set Night Allowance Salary Earning Component In Vodafone Samoa Settings VS"))
		add_sal = create_additional_salary(self.employee, self.allowance_date, night_compo, self.amount, self.name, self.doctype)
		self.additional_salary_ref = add_sal
		frappe.msgprint(_("Additional Salary {0} Created.").format(get_link_to_form("Additional Salary", add_sal)))
