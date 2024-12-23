from odoo import models, fields


class CustomStateRecord(models.Model):
    _name = 'custom.state.record'
    _description = 'Custom State Record'
    
    workflow_id = fields.Many2one(
        'custom.workflow',
        string="Workflow", 
        ondelete='cascade')
    model_id = fields.Many2one(
        'ir.model', 
        string="Model", 
        ondelete='cascade')
    res_id = fields.Many2one(
        'ir.model.data', 
        string="Record",
        ondelete='cascade')
    current_state = fields.Char(string="Current State", required=True)
               