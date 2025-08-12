from odoo import http
from odoo.http import request

class StudentWebsite(http.Controller):

    @http.route(['/student/submit'], type='http', auth='public', website=True, methods=['GET', 'POST'])
    def student_submit(self, **post):
        if request.httprequest.method == 'GET':
            return request.render('student_mgmt_demo.student_form')
        vals = {
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'dob': post.get('dob'),
            'notes': post.get('notes'),
        }
        rec = request.env['student.mgmt'].sudo().create(vals)
        return request.render('student_mgmt_demo.thanks', {'rec': rec})

    @http.route(['/student/list'], type='http', auth='public', website=True)
    def student_list(self, **kw):
        students = request.env['student.mgmt'].sudo().search([])
        return request.render('student_mgmt_demo.student_list', {'students': students})
