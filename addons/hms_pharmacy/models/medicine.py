from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_medicine = fields.Boolean(string='Is Medicine', default=False)
    dosage = fields.Char(string='Dosage')
    stock_quantity = fields.Float(
        string='Stock Quantity',
        compute='_compute_stock_quantity',
        digits='Product Unit of Measure'
    )

    @api.depends()   # No direct depends on stock.quant (cannot reference across models), computed at read-time
    def _compute_stock_quantity(self):
        StockQuant = self.env['stock.quant']
        for product in self:
            quants = StockQuant.sudo().search([
                ('product_id', '=', product.id),
                ('location_id.usage', '=', 'internal')
            ])
            product.stock_quantity = sum(quants.mapped('quantity'))
