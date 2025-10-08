# __manifest__.py
{
    'name': 'OBE University Management System',
    'version': '1.1.0',
    'category': 'Education',
    'author': 'Izma Shafqat',
    'depends': ['base', 'web', 'mail'],  # <-- add mail
    'data': [
        'security/ir.model.access.csv',
        'views/peo_view.xml',
        'views/plo_view.xml',
        'views/clo_view.xml',
        'views/course_view.xml',
        'views/peo_view.xml',           # dual views + dual act ions
    
        # NEW:
        'views/document_views.xml',
        
    
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
            'obesystem/static/src/scss/custom_theme.scss',
        ],
    },
    'installable': True,
    'application': True,
}
