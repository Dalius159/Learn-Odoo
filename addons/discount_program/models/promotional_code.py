from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PromotionalCode(models.Model):
    _name = 'promotional.code'
    _description = 'Promotional Code'
    
    name = fields.Char('Name')
    mkm_code = fields.Char('Code', compute='_compute_code', store=True)
    discount_percentage = fields.Float('Discount Percentage (%)')
    valid_from = fields.Date('Valid From')
    valid_to = fields.Date('Valid To')
    customer_id = fields.Many2one('res.partner', string='Customer')
    active = fields.Boolean('Active', default=True)
    
    _sql_constraints = [
        ('check_discount_percentage', 
         'CHECK(discount_percentage BETWEEN 1 AND 100)', 
         'The discount percentage must be between 1 and 100.'),
        ('check_valid_dates',
         'CHECK(valid_from <= valid_to)', 
         'The "Valid From" date must be earlier than or equal to the "Valid To" date.')
    ]
    
    @api.model
    def create(self, vals):
        res = super(PromotionalCode, self).create(vals)
        if not self.env.user.has_group(
                'discount_program.group_mkm_field_access'):
            raise ValidationError(
                'You do not have the necessary permissions to create a promotional code.')
            
        pricelist_vals = {
            'name': res.name,
            'code': res.mkm_code,
            'x_customer_id': res.customer_id.id,
            'item_ids':[
            (0, 0, {
                'display_applied_on': '1_product',
                'compute_price': 'percentage',
                'percent_price': res.discount_percentage,
                'date_start': res.valid_from,  
                'date_end': res.valid_to,  
            })]
        }
        self.env['product.pricelist'].sudo().create(pricelist_vals)

        return res
    
    @api.depends('discount_percentage')
    def _compute_code(self):
        for record in self:
            if record.discount_percentage:
                record.mkm_code = f"VIP_{int(record.discount_percentage)}"
                
   