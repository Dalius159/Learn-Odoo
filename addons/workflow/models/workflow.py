from odoo import models, fields, api, _
from odoo.exceptions import UserError
from lxml import etree

class Workflow(models.Model):
    _name = 'custom.workflow'
    _description = 'Custom Workflow'

    name = fields.Char(string="Name", required=True)
    model_id = fields.Many2one('ir.model', string="Model", required=True, ondelete='cascade')
    from_date = fields.Date(string="Start Date")
    to_date = fields.Date(string="End Date")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    state_ids = fields.One2many('custom.workflow.state', 'workflow_id', string="States", required=True)
    
    @api.model
    def create(self, vals):
        res = super(Workflow, self).create(vals)
        
        res.check_and_add_header()
        
        records = self.env[res.model_id.model].search([])
        
        for record in records:
            self.env['custom.state.record'].create({
                'workflow_id': res.id,
                'model_id': res.model_id.id,  
                'res_id': record.id, 
                'current_state': res.state_ids.sorted(key=lambda s: s.priority)[0].name
            })
            
        return res
    
    def unlink(self):
        formview = self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('type', '=', 'form')
        ], limit=1)
        
        if formview: 
            try:
                arch = formview.arch
                arch_tree = etree.fromstring(arch)
                
                for element in arch_tree.xpath('header'):
                    if len(element) == 0:  # Kiểm tra nếu thẻ là tự đóng (không có con)
                        arch_tree.remove(element)
                
                new_arch = etree.tostring(arch_tree, pretty_print=True, encoding='unicode')
                formview.write({'arch': new_arch})
                self.env.cr.commit()  # Commit để lưu thay đổi
            except Exception as e:
                raise UserError(_("Error while removing <header/>: %s") % str(e))
        
        res = super(Workflow, self).unlink()
        return res

    @api.model
    def action_approve(self, record_id, model_id):
        state_record = self.env['custom.state.record'].search([
            ('model_id.model', '=', model_id), ('res_id', '=', record_id)
        ], limit=1)
       
        current_state = self.env['custom.workflow.state'].search([
            ('workflow_id', '=', state_record.workflow_id.id),
            ('name', '=', state_record.current_state)
        ], limit=1)

        if not current_state:
            raise UserError("Current state not found.")

        next_state = self.env['custom.workflow.state'].search([
            ('workflow_id', '=', state_record.workflow_id.id),
            ('priority', '>', current_state.priority)
        ], order='priority', limit=1)

        if not next_state:
            raise UserError("No higher priority state found.")

        user = self.env.user
        if current_state.approver_group_id and not user.has_group(current_state.approver_group_id.id):
            raise UserError("You do not have the rights to approve this state")
        
        state_record.current_state = next_state.name

        return True
    
    @api.model
    def check_and_add_header(self):
        formview = self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('type', '=', 'form')
        ], limit=1)
        
        if formview:
            arch = formview.arch
            arch_tree = etree.fromstring(arch)

            if not arch_tree.find('header'):
                header_element = etree.Element('header')
                arch_tree.insert(0, header_element)

                new_arch = etree.tostring(arch_tree, pretty_print=True, encoding='unicode')
                formview.write({'arch': new_arch})
                self.env.cr.commit() 
        return {'type': 'ir.actions.client', 'tag': 'soft_reload'}
        