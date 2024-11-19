from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    related_sale_order_id = fields.Many2one('sale.order', string="Related Sale Order", readonly=True)

    @api.model
    def create(self, vals):
        purchase_order = super(PurchaseOrder, self).create(vals)
        company = self.env['res.company'].search([('partner_id', '=', purchase_order.partner_id.id)], limit=1)
        
        if self.env.context.get('from_intercompany_order') or not company:
            return purchase_order
        
        sale_order_vals = {
            'partner_id': purchase_order.company_id.partner_id.id, 
            'company_id': company.id, 
            'related_purchase_order_id': purchase_order.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_qty,
                'price_unit': line.price_unit,
            }) for line in purchase_order.order_line]
        }
        
        sale_order = self.env['sale.order'].with_context(from_intercompany_order=True).sudo().create(sale_order_vals)
        
        purchase_order.related_sale_order_id = sale_order.id

        return purchase_order
    
    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        
        for purchase_order in self.sudo():
            if purchase_order.related_sale_order_id:
                sale_order = purchase_order.sudo().related_sale_order_id
                sale_order.action_cancel()
        
        return res
