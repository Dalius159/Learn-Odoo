from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    x_customer_id = fields.Many2one('res.partner', string='Customer')
    
    