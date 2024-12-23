from odoo import models, fields, api, _
from odoo.exceptions import UserError
from lxml import etree


class Workflow(models.Model):
    _name = 'custom.workflow'
    _description = 'Custom Workflow'

    name = fields.Char(string="Name")
    model_id = fields.Many2one('ir.model', string="Model", ondelete='cascade')
    from_date = fields.Date(string="Start Date")
    to_date = fields.Date(string="End Date")
    company_id = fields.Many2one(
        'res.company', 
        string="Company", 
        default=lambda self: self.env.company)
    state_ids = fields.One2many(
        'custom.workflow.state', 
        'workflow_id', 
        string="States")
    
    # for each record of the model
    # create a related record in custom.state.record
    @api.model
    def create(self, vals):
        res = super(Workflow, self).create(vals)
        
        res.action_check_add_header()
        
        records = self.env[res.model_id.model].search([])
        
        for record in records:
            self.env['custom.state.record'].create({
                'workflow_id': res.id,
                'model_id': res.model_id.id,  
                'res_id': record.id, 
                'current_state': 
                    res.state_ids.sorted(key=lambda s: s.priority)[0].name
            })
            
        return res
    
    # automatically delete form header when workflow is deleted
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
                    # Kiểm tra nếu thẻ là tự đóng (không có con)
                    if len(element) == 0:  
                        arch_tree.remove(element)
                
                new_arch = etree.tostring(
                    arch_tree, pretty_print=True, encoding='unicode')
                formview.write({'arch': new_arch})
                # Commit để lưu thay đổi
                self.env.cr.commit()  
            except Exception as e:
                raise UserError(_("Error while removing <header/>: %s") % str(e))
        
        res = super(Workflow, self).unlink()
        return res


    @api.model
    def action_approve(self, record_id, model_id):
        # Find the state record of the record
        state_record = self.env['custom.state.record'].search([
            ('model_id.model', '=', model_id), ('res_id', '=', record_id)
        ], limit=1)
        
        # Find the current state in state list
        current_state = self.env['custom.workflow.state'].search([
            ('workflow_id', '=', state_record.workflow_id.id),
            ('name', '=', state_record.current_state)
        ], limit=1)

        next_state = self.env['custom.workflow.state'].search([
            ('workflow_id', '=', state_record.workflow_id.id),
            ('priority', '>', current_state.priority)
        ], order='priority', limit=1)

        user = self.env.user
        # Check if the user has the rights to approve the state
        if current_state.approver_group_id and not user.has_group(
                current_state.approver_group_id.id):
            raise UserError(
                "You do not have the rights to approve this state")
        
        state_record.current_state = next_state.name

        return True
    
    # Add a header to the form view of the model
    @api.model
    def action_check_add_header(self):
        formview = self.env['ir.ui.view'].search([
            ('model', '=', self.model_id.model),
            ('type', '=', 'form')
        ], limit=1)
        
        if formview:
            arch = formview.arch
            arch_tree = etree.fromstring(arch)
            
            # If there is no header in the form view
            # add a header to the form view
            if not arch_tree.find('header'):
                header_element = etree.Element('header')
                arch_tree.insert(0, header_element)

                new_arch = etree.tostring(
                    arch_tree, pretty_print=True, encoding='unicode')
                formview.write({'arch': new_arch})
                self.env.cr.commit() 
        return {'type': 'ir.actions.client', 'tag': 'soft_reload'}
        