{
    'name': 'HMS OPD/IPD Management',
    'version': '2.1',
    'summary': 'Complete OPD and IPD Management System',
    'description': """
        Real-world OPD/IPD workflow implementation with:
        - Separate OPD (outpatient) and IPD (inpatient) processes
        - Bed management for IPD admissions
        - Proper status tracking
        - Integrated with HMS Base
    """,
    'author': 'Your Name',
    'category': 'Healthcare',
    'depends': ['hms_base', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'views/admission_views.xml',
        'views/patient_views.xml',
        
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}