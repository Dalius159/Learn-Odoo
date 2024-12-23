from odoo import models, fields, api


class StockQuantPeriod(models.Model):
    _name = 'stock.quant.period'
    _description = 'Stock Quant Period'
    _order = 'period_date desc'

    period_date = fields.Datetime(string="Period Date")
    location_id = fields.Many2one('stock.location', string="Location")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float(string="Remain Quantity")
    
    
class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    x_quant_period_ids = fields.One2many(
        'stock.quant.period', 
        'product_id', 
        string='Stock Quant Periods')


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'


    @api.model
    def create(self, vals):
        record = super(StockQuantInherit, self).create(vals)
        record.action_create_stock_quant_period()
        return record


    def write(self, vals):
        res = super(StockQuantInherit, self).write(vals)
        if 'quantity' in vals:
            for record in self:
                record.action_create_stock_quant_period()
        return res


    def action_create_stock_quant_period(self):
        stock_quant_period_env = self.env['stock.quant.period']
        for record in self:
            stock_quant_period_env.sudo().create({
                'period_date': fields.Datetime.now(),
                'location_id': record.location_id.id,
                'product_id': record.product_id.id,
                'quantity': record.quantity
            })
