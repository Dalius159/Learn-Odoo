from odoo import models, fields

class MKMMassCreationWizard(models.TransientModel):
    _name = 'mkm.mass.creation.wizard'
    _description = 'Mkm Mass Creation Wizard'
    

    target_type = fields.Selection([
        ('selected_customers', 'Selected Customers'),
        ('all_users', 'All Users'),
        ('all_companies', 'All Companies')],
        string='Target Type',
        required=True,
        default='selected_customers'
    )
    name = fields.Char('Name')
    customer_ids = fields.Many2many('res.partner', string='Customers')
    discount_percentage = fields.Float('Discount Percentage (%)')
    valid_from = fields.Date('Valid From')
    valid_to = fields.Date('Valid To')

    def create_mass_mkm(self):
        promotional_code_obj = self.env['promotional.code']

        if self.target_type == 'selected_customers':
            for customer in self.customer_ids:
                promotional_code_obj.create({
                    'name': self.name,
                    'customer_id': customer.id,
                    'discount_percentage': self.discount_percentage,
                    'valid_from': self.valid_from,
                    'valid_to': self.valid_to,
                })
        elif self.target_type == 'all_users':
            all_users = self.env['res.partner'].search([('user_ids', '!=', False)])
            for user in all_users:
                promotional_code_obj.create({
                    'name': self.name,
                    'customer_id': user.id,
                    'discount_percentage': self.discount_percentage,
                    'valid_from': self.valid_from,
                    'valid_to': self.valid_to,
                })
        elif self.target_type == 'all_companies':
            all_companies = self.env['res.company'].search([])
            for company in all_companies:
                partner = company.partner_id
                promotional_code_obj.create({
                    'name': self.name,
                    'customer_id': partner.id,
                    'discount_percentage': self.discount_percentage,
                    'valid_from': self.valid_from,
                    'valid_to': self.valid_to,
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
