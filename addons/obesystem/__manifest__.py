{
    'name': 'OBE University Management System',
    'version': '1.0',
    'category': 'Education',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/peo_view.xml',
        'views/plo_view.xml',
        'views/clo_view.xml',
        'views/course_view.xml',
    ],
    'installable': True,
    'application': True,
}
