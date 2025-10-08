{
    'name': 'Activity Logger',
    'summary': 'User session, HTTP request, and ORM data change auditing',
    'version': '1.0.0',
    'category': 'Tools',
    'author': 'University',
    'website': 'https://example.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'data/sequence.xml',
        'data/ir_actions_server_data.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/activity_views.xml',
    ],
    'installable': True,
    'application': True,
}


