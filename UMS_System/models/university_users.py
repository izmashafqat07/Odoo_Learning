# models/university_student.py 
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    # user_ids = fields.One2many('res.users', 'partner_id', string="Related Users")

    # @api.model
    # def action_create_user(self):
    #     self.ensure_one()
    #     if not self.user_ids:
    #         user_vals = {
    #             'name': self.name,
    #             'login': self.email or f"{self.employee_id}@university.local",
    #             'partner_id': self.id,
    #             'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
    #         }
    #         self.env['res.users'].create(user_vals)
    #     return True

    partner_type = fields.Selection([
        ('student', 'Student'),
        ('staff', 'Staff')
    ], string="Partner Type", default='student')
    
    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        # Clear student-related fields if not a student
        if self.partner_type != 'student':
            self.enrollment_number = False
            self.roll_number = False
            self.program = False
            self.batch = False
        
        # Clear staff-related fields if not a staff
        if self.partner_type != 'staff':
            self.employee_id = False
            self.department_id = False
            self.designation = False
            self.staff_type_id = False

    def action_open_user_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create User'),
            'res_model': 'res.users',
            'view_mode': 'form',
            'view_id': self.env.ref('base.view_users_form').id,
            'target': 'current',
            'context': {
            # prefill & lock to this partner
                'default_partner_id': self.id,
                'search_default_partner_id': self.id,   # search panel me partner filter lag jaye
                'force_partner_id': self.id,            # custom key; neeche XML me use hoga
                'default_login': self.email or '',
        },
    }


# =========================== STUDENT FIELDS (own model) ===========================
class UniversityStudent(models.Model):
    _inherit = "res.partner"   # extend partner for student fields

    # Core
    enrollment_number = fields.Char(string="Enrollment Number", tracking=True)
    roll_number = fields.Char(string="Roll Number")
    program = fields.Char(string="Program")
    batch = fields.Char(string="Batch/Year")

    # Common (partner-level) — define once here, usable everywhere
    department_id = fields.Many2one('university.department', string="Department")

    # Additional Student Details (useful in a UMS)
    admission_date = fields.Date(string="Admission Date")
    date_of_birth = fields.Date(string="Date of Birth")
    guardian_name = fields.Char(string="Guardian Name")
    guardian_phone = fields.Char(string="Guardian Phone")

    semester = fields.Integer(string="Current Semester")
    section = fields.Char(string="Section")

    cgpa = fields.Float(string="CGPA", digits=(3, 2))
    

   
    student_status = fields.Selection([
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('graduated', 'Graduated'),
        ('dropped', 'Dropped')
    ], string="Student Status", default='active')

    # advisor_id = fields.Many2one(
    #     'res.partner', string="Faculty Advisor",
    #     domain="[('partner_type','=','staff')]"
    # )
    emergency_contact = fields.Char(string="Emergency Contact")

    # Constraints
    @api.constrains('enrollment_number')
    def _check_unique_enrollment(self):
        for rec in self.filtered(lambda r: r.enrollment_number):
            dup = self.search([
                ('id', '!=', rec.id),
                ('partner_type', '=', 'student'),
                ('enrollment_number', '=', rec.enrollment_number)
            ], limit=1)
            if dup:
                raise ValidationError(_("Enrollment Number must be unique among students."))


# ============================ STAFF FIELDS (own model) ============================
class UniversityStaff(models.Model):
    _inherit = "res.partner"   # extend partner for staff fields

    # Core
    employee_id = fields.Char(string="Employee ID", tracking=True)
    department_id = fields.Many2one('university.department', string="Department")
    designation = fields.Char(string="Designation")
    staff_type_id = fields.Many2one('university.staff.type', string="Staff Type",
                                    help="Staff's role in the university.")

    # Additional Staff Details
    hire_date = fields.Date(string="Hire Date")
    job_grade = fields.Char(string="Job Grade")
    contract_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('visiting', 'Visiting')
    ], string="Contract Type", default='permanent')

    work_email = fields.Char(string="Work Email")
    work_phone = fields.Char(string="Work Phone")
    office_room = fields.Char(string="Office/Room")

    specialization = fields.Char(string="Specialization")
    qualification = fields.Char(string="Highest Qualification")

   
   

    # Safe default for staff type
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'staff_type_id' in fields_list and not res.get('staff_type_id'):
            try:
                st = self.env['university.staff.type'].search([], limit=1)
                res['staff_type_id'] = st.id or False
            except Exception:
                pass
        return res

    # Constraints
    @api.constrains('employee_id')
    def _check_unique_employee(self):
        for rec in self.filtered(lambda r: r.employee_id):
            dup = self.search([
                ('id', '!=', rec.id),
                ('partner_type', '=', 'staff'),
                ('employee_id', '=', rec.employee_id)
            ], limit=1)
            if dup:
                raise ValidationError(_("Employee ID must be unique among staff."))
