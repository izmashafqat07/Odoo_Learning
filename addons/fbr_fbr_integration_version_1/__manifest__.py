# fbr_fbr_integration/__manifest__.py
# -*- coding: utf-8 -*-
{
    "name": "FBR Digital Invoicing (PRAL) – Odoo 18 - version 1",
    "summary": (
        "Post customer invoices to FBR Digital Invoicing (PRAL): "
        "postinvoicedata with GST details, QR, and manual tax override."
    ),
    "version": "1.0.0",
    "category": "Accounting",
    "author": "Faiza",
    "license": "OPL-1",
    "depends": ["base", "base_setup", "product", "account", "uom"],
    "data": [
        "security/ir.model.access.csv",

        # Settings UI
        "views/res_config_settings_view.xml",
        "views/menu_views.xml",

        # Product UIs
        "views/product_template_views.xml",
        "views/product_template_views_extra_measures.xml",  # ✅ correct filename

        # UoM form: show FBR code on UoM
        "views/uom_views.xml",  # ✅ must be included

        # Accounting UI
        "views/account_move_views.xml",

        # Reports
        "views/report_invoice_fbr.xml",

        # Seed / updates for UoMs
        "data/uom_data.xml",
    ],
    "external_dependencies": {"python": ["requests", "qrcode", "Pillow"]},
    "application": True,
    "installable": True,
}
