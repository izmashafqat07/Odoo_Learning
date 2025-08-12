from odoo import http
from odoo.http import request

class LibraryRequestController(http.Controller):

    @http.route('/library/request', type='http', auth='public', website=True)
    def library_request_form(self, **kw):
        return request.render('library_management.library_request_form')

    @http.route('/library/request/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def library_request_submit(self, **post):
        request.env['library.request'].sudo().create({
            'name': post.get('name') or 'Anonymous',
            'email': post.get('email'),
            'book_title': post.get('book_title'),
            'notes': post.get('notes'),
        })
        return request.render('library_management.library_request_thankyou')
