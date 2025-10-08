{
    'name': 'UMS System',
    'version': '1.0',
    'summary': 'University Management System (Departments, Students, Faculty, Access Control)',
    'category': 'Education',
    'author': 'University',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail','portal','website'],
    'data': [
        # 🔹 Security
        'security/obe_security.xml', 
         
        'security/record_rules.xml',     # Record Rules for Faculty & Students
        'security/ir.model.access.csv',                # Access rights for Department & custom models
        'security/university_user_template.xml',       # Optional user templates (if you made)

        # 🔹 Views
        'views/university_department_views.xml',       # Department model views
        'views/university_user_type_views.xml',        # Staff types
        'views/university_partner_views.xml',  
        'views/university_users_views.xml',
        'views/university_student_views.xml',
        'views/university_staff_views.xml',
        # Partner form (students & staff with department)
        'views/university_views.xml',                  # Any other models
        'views/user_profile_views.xml',                # User profile customization
        'views/obe_menu.xml',
        'views/portal_templates.xml',
        
                              # Menu structure
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
