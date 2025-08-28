{
    "name": "FBR Digital Invoicing (PRAL) – Odoo 18",
    "summary": (
        "Post customer invoices to FBR Digital Invoicing (PRAL): "
        "postinvoicedata with GST details, QR, and manual tax override."
    ),
    "version": "1.0.0",
    "category": "Accounting",
    "author": "Faiza",
    "license": "OPL-1",
    "depends": [
        "base",
        "account",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu_views.xml",
        "views/res_config_settings_view.xml",
      
       
        "views/product_template_views.xml",
        "views/account_move_views.xml",
        "views/report_invoice_fbr.xml",
    ],
    "external_dependencies": {
        "python": [
            "requests",
            "qrcode",
            "Pillow",
        ],
    },
    "application": True,
    "installable": True,
}
