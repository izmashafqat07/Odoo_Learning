{
    'name': 'HMS Pharmacy',
    'version': '1.0.0',
    'summary': 'Pharmacy and basic inventory for HMS',
    'description': 'Medicine product extensions + prescription model integrated with HMS Base',
    'author': 'Ammar',
    'category': 'Healthcare',
    'depends': ['hms_base', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/hms_pharmacy_medicine_views.xml',
        'views/hms_pharmacy_prescription_views.xml',
        'views/hms_pharmacy_menu.xml',
    ],
    'installable': True,
    'application': False,
}
