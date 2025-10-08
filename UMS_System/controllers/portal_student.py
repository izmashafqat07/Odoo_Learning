# controllers/portal_student.py
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class UMSCustomerPortal(CustomerPortal):

    def _get_editable_partner_fields(self):
        """Allow portal user to edit these extra fields on /my/account."""
        fields = super()._get_editable_partner_fields()
        extra = [
            # common
            'department_id', 'partner_type',
            # student
            'enrollment_number', 'roll_number', 'program', 'batch',
            'admission_date', 'date_of_birth', 'guardian_name', 'guardian_phone',
            'semester', 'section', 'cgpa', 'student_status', 'emergency_contact',
            # staff
            'employee_id', 'designation', 'staff_type_id', 'hire_date',
            'job_grade', 'contract_type', 'work_email', 'work_phone',
            'office_room', 'specialization', 'qualification',
        ]
        # Keep only real fields to avoid issues
        model_fields = request.env['res.partner']._fields
        return list({*fields, *(f for f in extra if f in model_fields)})
