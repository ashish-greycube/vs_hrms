# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"fieldname": "employee",
			"fieldtype": "Link", 
			"label": _("Employee"),
			"options": "Employee",
			"width": 150
		},
		{
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": _("Employee Name"),
			"width": 150
		},
		{
			"fieldname": "regular_hours",
			"fieldtype": "Data",
			"label": _("Regular Hours"),
			"width": 150
		},
		{
			"fieldname": "ot1",
			"fieldtype": "Data",
			"label": _("OT1"),
			"width": 150
		},
		{
			"fieldname": "ot2",
			"fieldtype": "Data",
			"label": _("Special/OT2"),
			"width": 150
		},
		{
			"fieldname": "vacation_hours",
			"fieldtype": "Data",
			"label": _("Vacation Hours"),
			"width": 150
		},
		{
			"fieldname": "sick_hours",
			"fieldtype": "Data",
			"label": _("Sick Hours"),
			"width": 150
		},
		{
			"fieldname": "maternity",
			"fieldtype": "Data",
			"label": _("Maternity/Paternity"),
			"width": 150
		},
		{
			"fieldname": "bareavement",
			"fieldtype": "Data",
			"label": _("Bareavement"),
			"width": 150
		},
		{
			"fieldname": "commision",
			"fieldtype": "Data",
			"label": _("Commision"),
			"width": 150
		},
		{
			"fieldname": "previous_ppe",
			"fieldtype": "Data",
			"label": _("Previous PPE(Missed Hrs)"),
			"width": 150
		},
		{
			"fieldname": "observe_public_holidays",
			"fieldtype": "Data",
			"label": _("Observe Public Holidays"),
			"width": 150
		},
		{
			"fieldname": "total_regular_hrs",
			"fieldtype": "Data",
			"label": _("Total Regular Hrs"),
			"width": 150
		},
		{
			"fieldname": "holiday_worked",
			"fieldtype": "Data",
			"label": _("Holiday Worked"),
			"width": 150
		},
		{
			"fieldname": "night_meal_allowance",
			"fieldtype": "Data",
			"label": _("Night/Meal Allowance"),
			"width": 150
		},
		{
			"fieldname": "phone_allowance",
			"fieldtype": "Data",
			"label": _("Phone Allowance"),
			"width": 150
		},
		{
			"fieldname": "other_allowance",
			"fieldtype": "Data",
			"label": _("Other Allowance"),
			"width": 150
		},
		{
			"fieldname": "m_tala_transfer",
			"fieldtype": "Data",
			"label": _("M-Tala Transfer"),
			"width": 150
		},
		{
			"fieldname": "total_hours",
			"fieldtype": "Data",
			"label": _("Total Hours"),
			"width": 150
		},
	]



def get_data() -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	return [
		["Row 1", 1],
		["Row 2", 2],
	]
