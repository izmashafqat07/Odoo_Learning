{
    'name': 'Library Management',
    'version': '1.0.0',
    'summary': 'Simple library request system',
    'description': 'Public book request form and backend management',
    'author': 'Generated for user',
    'depends': ['base', 'website'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/library_book_views.xml',
        'views/library_request_views.xml',
        'views/library_request_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}