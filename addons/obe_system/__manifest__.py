{
    'name': 'OBE Faiza',
    'version': '1.0',
    'summary': 'Manage PEOs for OBE System',
    'description': 'Allows creation of PEOs with publish & unpublish features',
    'category': 'Education',
    'author': 'XYZ',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/peo_views.xml',
          # keep fallback actions available
        'views/menu_views.xml',
    ],
    
    'installable': True,
    'application': True,
}
