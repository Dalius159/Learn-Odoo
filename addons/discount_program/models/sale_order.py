from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    x_promotional_code_id = fields.Many2one(
        'promotional.code',
        string='Promotional Code')
    x_mkm_code = fields.Char('Discount Code') 
    x_discount_name = fields.Char('Coupon',
        related='x_promotional_code_id.name')
    
    def action_apply_promo(self):
        if self.order_line:
            if self.x_mkm_code:
                res = self.env['promotional.code'].search([
                    ('customer_id', '=', self.partner_id.id), 
                    ('mkm_code', '=', self.x_mkm_code), 
                    ('active', '=', True)], limit=1)

                if res:
                    self.write({'x_promotional_code_id': res.id,})
                    self.order_line.write({
                        'discount': 
                            self.x_promotional_code_id.discount_percentage})
                    self.x_promotional_code_id.sudo().write({
                        'active': 
                            False})
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
                        
            return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('INVALID CODE'),
                        'type': 'danger',
                    }
                }
        raise ValidationError(_('No order lines to apply the discount.'))
        
    
    def action_remove_promo(self):
        self.x_promotional_code_id.sudo().write({'active': True})
        self.write({'x_promotional_code_id': False,
                    'x_mkm_code': False})
        self.order_line.write({'discount': 0})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
   