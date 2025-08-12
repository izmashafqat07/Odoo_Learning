# -*- coding: utf-8 -*-
{
    'name': 'Student Management Demo',
    'version': '1.0',
    'summary': 'Public registration form + backend management',
    'description': 'Public form and admin backend for simple student records',
    'author': 'You',
    'category': 'Education',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',   # load security first
        'data/seq_and_demo.xml',         # sequence before creation
        'views/student_views.xml',       # views (tree/form/search/action/menu)
        'views/templates.xml',           # website templates last
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

