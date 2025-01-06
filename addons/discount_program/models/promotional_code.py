from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PromotionalCode(models.Model):
    _name = 'promotional.code'
    _description = 'Promotional Code'

    mkm_code = fields.Char('Code', compute='_compute_code', store=True)
    discount_percentage = fields.Integer('Discount Percentage')
    valid_from = fields.Date('Valid From')
    valid_to = fields.Date('Valid To')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    active = fields.Boolean('Active', default=True)

    @api.depends('discount_percentage')
    def _compute_code(self):
        for record in self:
            if record.discount_percentage:
                record.mkm_code = f"VIP_{record.discount_percentage}"
                
    @api.constrains('discount_percentage')
    def _check_discount_percentage(self):
        for record in self:
            if record.discount_percentage < 1 or record.discount_percentage > 100:
                raise ValidationError("The discount percentage must be between 1 and 100.")