# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api

def post_init_set_fbr_uoms(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    Uom = env['uom.uom']
    Cat = env['uom.category']

    def ensure_category(name, ref_uom_name):
        cat = Cat.search([('name', '=', name)], limit=1)
        if not cat:
            cat = Cat.create({'name': name})
        ref = Uom.search([('name', '=ilike', ref_uom_name), ('category_id', '=', cat.id)], limit=1)
        if not ref:
            ref = Uom.create({
                'name': ref_uom_name, 'category_id': cat.id,
                'uom_type': 'reference', 'factor': 1.0, 'rounding': 0.000001
            })
        return cat, ref

    # Reference categories/uoms
    weight_cat, kg  = ensure_category('Weight', 'Kilogram')
    volume_cat, m3  = ensure_category('Volume', 'Cubic Meter')
    length_cat, m   = ensure_category('Length', 'Meter')
    area_cat,   sqm = ensure_category('Area', 'Square Meter')
    unit_cat,   unit= ensure_category('Unit', 'Unit(s)')
    energy_cat, kwh = ensure_category('Energy', 'Kilowatt-hour')
    power_cat,  w   = ensure_category('Power', 'Watt')

    # label -> (name, cat_id, factor)
    F = {
        # Weight
        'MT':        ('Metric Ton',       weight_cat.id, 1000.0),
        '40KG':      ('40 Kilogram',      weight_cat.id, 40.0),
        'KG':        ('Kilogram',         weight_cat.id, 1.0),
        'Gram':      ('Gram',             weight_cat.id, 0.001),
        'Carat':     ('Carat',            weight_cat.id, 0.0002),
        'Pound':     ('Pound',            weight_cat.id, 0.45359237),

        # Volume
        'Liter':         ('Liter',           volume_cat.id, 0.001),
        'Gallon':        ('Gallon (US)',     volume_cat.id, 0.00378541178),
        'Cubic Metre':   ('Cubic Meter',     volume_cat.id, 1.0),
        'Barrels':       ('Barrel (Oil)',    volume_cat.id, 0.1589872949),

        # Length
        'Meter':     ('Meter',           length_cat.id, 1.0),
        'Foot':      ('Foot',            length_cat.id, 0.3048),

        # Area
        'Square Yard':  ('Square Yard',  area_cat.id, 0.83612736),
        'Square Metre': ('Square Meter', area_cat.id, 1.0),
        'Square Foot':  ('Square Foot',  area_cat.id, 0.09290304),

        # Energy (ref = kWh)
        'KWH':      ('Kilowatt-hour',    energy_cat.id, 1.0),
        'MMBTU':    ('MMBTU',            energy_cat.id, 293.07107),

        # Power (ref = Watt)
        'Mega Watt':('Megawatt',         power_cat.id, 1_000_000.0),

        # Unit/Counts
        'SET':           ('Set',             unit_cat.id, 1.0),
        'Dozen':         ('Dozen',           unit_cat.id, 12.0),
        'Pieces':        ('Pieces',          unit_cat.id, 1.0),
        'Number':        ('Number',          unit_cat.id, 1.0),
        'Packs':         ('Pack',            unit_cat.id, 1.0),
        'Pair':          ('Pair',            unit_cat.id, 2.0),
        'Thousand Unit': ('Thousand Unit',   unit_cat.id, 1000.0),
        'Bag':           ('Bag',             unit_cat.id, 1.0),
        'Timber Logs':   ('Timber Logs',     unit_cat.id, 1.0),

        # Optional catch-all
        'Others':        ('Others',          unit_cat.id, 1.0),
    }

    CODE = {
        'U1000003': 'MT',
        'U1000005': 'SET',
        'U1000006': 'KWH',
        'U1000008': '40KG',
        'U1000009': 'Liter',
        'U1000011': 'Square Yard',
        'U1000012': 'Bag',
        'U1000013': 'KG',
        'U1000046': 'MMBTU',
        'U1000048': 'Meter',
        'U1000053': 'Carat',
        'U1000055': 'Cubic Metre',
        'U1000057': 'Dozen',
        'U1000059': 'Gram',
        'U1000061': 'Gallon',
        'U1000063': 'Kilogram',
        'U1000065': 'Pound',
        'U1000067': 'Timber Logs',
        'U1000069': 'Pieces',
        'U1000071': 'Packs',
        'U1000073': 'Pair',
        'U1000075': 'Square Foot',
        'U1000077': 'Square Metre',
        'U1000079': 'Thousand Unit',
        'U1000081': 'Mega Watt',
        'U1000083': 'Foot',
        'U1000085': 'Barrels',
        'U1000087': 'Number',
        'U1000004': None,   # Bill of lading (skip)
        'U1000088': 'Others',
    }

    for fbr_code, label in CODE.items():
        if not label:
            continue
        name, cat_id, factor = F[label]
        uom = Uom.search([('name', '=ilike', name), ('category_id', '=', cat_id)], limit=1)
        if not uom:
            uom = Uom.create({
                'name': name,
                'category_id': cat_id,
                'uom_type': 'bigger' if factor > 1.0 else ('smaller' if factor < 1.0 else 'reference'),
                'factor': factor,
                'rounding': 0.000001,
            })
        uom.fbr_code = fbr_code
