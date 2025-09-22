{
    'name': 'OBE University Management System',
    'version': '1.0',
    'category': 'Education',
    'author': 'Izma Shafqat',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/peo_view.xml',
        'views/plo_view.xml',
        'views/clo_view.xml',
        'views/course_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'obesystem/static/src/scss/custom_theme.scss',
            'obesystem/static/src/js/custom_buttons.js',
        ],
    },
    'installable': True,
    'application': True,
}
