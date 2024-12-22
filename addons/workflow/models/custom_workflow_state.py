from odoo import models, fields, api

class WorkflowState(models.Model):
    _name = 'custom.workflow.state'
    _description = 'Workflow State'

    workflow_id = fields.Many2one('custom.workflow', string="Workflow", required=True, ondelete='cascade')
    priority = fields.Integer(string="Priority")
    name = fields.Many2one(string="State Name", required=True)
    approver_group_id = fields.Many2one('res.groups', string="Approver Group")
