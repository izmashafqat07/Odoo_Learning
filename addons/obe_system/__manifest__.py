# -*- coding: utf-8 -*-
{
    'name': 'OBE Faiza',
    'version': '1.2.0',
    'summary': 'Manage PEOs with document-based publishing',
    'description': 'PEOs (obe.peo) must reference a Document (obe.document) to publish; create/delete disabled when all PEOs are published.',
    'category': 'Education',
    'author': 'XYZ',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/document_views.xml',
        'views/peo_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}
