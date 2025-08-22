{
    "name": "FBR Digital Invoicing (PK)",
    "summary": "Integrate Pakistan FBR e-Invoicing / POS with Odoo Invoicing (Odoo 17/18)",
    "version": "18.0.1.0.0",
    "author": "You",
    "license": "OPL-1",
    "depends": ["account", "base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
        "views/account_move_views.xml",
        "report/report_templates.xml"
    ],
    "assets": {},
    "application": False,
    "installable": True
}