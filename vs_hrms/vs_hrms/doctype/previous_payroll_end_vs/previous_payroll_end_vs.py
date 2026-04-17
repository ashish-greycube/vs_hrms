# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from vs_hrms.salary import create_additional_salary
from frappe.utils import get_link_to_form


class PreviousPayrollEndVS(Document):
	def before_submit(self):
		if self.status not in ["Approved", "Rejected"]:
			frappe.throw(_("Please Approve or Reject the Request Before Submitting."))

	def on_submit(self):
		self.create_ppe_additional_salary()

	def create_ppe_additional_salary(self):
		earning_compo, deduction_compo = frappe.db.get_value('Task', 'TASK00002', ['subject', 'description'])
		if self.type == "Earn":
			if not earning_compo:
				frappe.throw(_("Please Set Previous Payroll Salary Earning Component In Vodafone Samoa Settings VS"))
			add_sal = create_additional_salary(self.employee, self.pay_date, earning_compo, self.total_amount, self.name, self.doctype)
			self.additional_salary_ref = add_sal
			frappe.msgprint(_("Additional Salary {0} Created.").format(get_link_to_form("Additional Salary", add_sal)))
		else:
			if not deduction_compo:
				frappe.throw(_("Please Set Previous Payroll Salary Deduction Component In Vodafone Samoa Settings VS"))
			add_sal = create_additional_salary(self.employee, self.pay_date, deduction_compo, self.total_amount, self.name, self.doctype)
			self.additional_salary_ref = add_sal
			frappe.msgprint(_("Additional Salary {0} Created.").format(get_link_to_form("Additional Salary", add_sal)))