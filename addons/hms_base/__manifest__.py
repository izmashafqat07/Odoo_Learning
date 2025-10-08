{
    'name': 'HMS Base',
    'version': '1.0',
    'summary': 'Core module for Hospital Management System',
    'description': """
        Provides foundational models and data for HMS, including patient management and shared medical data.
    """,
    'author': 'Ammar',
    'category': 'Healthcare',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hms_base_patient_views.xml',
        'views/hms_base_doctor_views.xml',
        'views/hms_base_department_views.xml',
    ],
}
