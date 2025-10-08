{
    "name": "HMS HR & Payroll",
    "version": "1.0.0",
    "summary": "HR bridge for HMS: Employees, simple Payroll, and Doctor integration",
    "description": """
Core HR bridge for HMS. Links hr.employee to HMS Departments & Doctors. Adds a minimal Payroll model when hr_payroll is not present.
    """,
    "category": "Human Resources",
    "author": "Ammar",
    "license": "LGPL-3",
    "application": False,
    "depends": ["hms_base", "hr"],
    # Works fine even if hr_payroll is absent. If you install hr_payroll later, this still works.
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
        "views/doctor_views.xml",
        "views/payroll_views.xml",
    ],
}