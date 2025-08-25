{
    "name": "FBR Mock Integration",
    "summary": "Send posted customer invoices to a mock FBR server (local testing)",
    "version": "1.0.0",
    "category": "Accounting",
    "author": "Faiza",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu_views.xml",
        "views/res_config_settings_view.xml",
        "views/account_move_view.xml",
        "views/report_invoice_fbr.xml", 
    ],
    "external_dependencies": {"python": ["requests"]},
    "application": True,  # This is the key setting!
    "installable": True,
    "auto_install": False,
}

