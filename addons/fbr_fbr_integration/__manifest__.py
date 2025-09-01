# -*- coding: utf-8 -*-
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
        "base_setup",   # needed for inheriting General Settings form
        "product",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",

        # Settings UI (load before menus)
        "views/res_config_settings_view.xml",
        "views/menu_views.xml",

        # Product UIs
        "views/product_template_views.xml",              # your existing FBR page
        "views/product_template_views_extra_measures.xml",  # NEW inventory block

        # Accounting UI
        "views/account_move_views.xml",

        # Reports
        "views/report_invoice_fbr.xml",
    ],
    "external_dependencies": {
        "python": [
            "requests",
            "qrcode",
            "Pillow",
        ],
    },
    "post_init_hook": "post_init_set_fbr_uoms",   # seed FBR UoMs + codes
    "application": True,
    "installable": True,
}
