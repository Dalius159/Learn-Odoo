from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add a field to store the related purchase order
    x_related_purchase_order_id = fields.Many2one(
        'purchase.order', 
        string="Related Purchase Order", 
        readonly=True)

    # Automatically create a related purchase order when a sale order is created
    @api.model
    def create(self, vals):
        sale_order = super(SaleOrder, self).create(vals)
        company = self.env['res.company'].search(
            [('partner_id', '=', sale_order.partner_id.id)], limit=1)
        
        # If the sale order is created from an intercompany purchase order,
        if self.env.context.get('from_intercompany_order') or not company:
            return sale_order

        purchase_order_vals = {
            'partner_id': sale_order.company_id.partner_id.id,
            'company_id': company.id,
            'x_related_sale_order_id': sale_order.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
            }) for line in sale_order.order_line]
        }
        
        # Create a purchase order with the same products and quantities as the sale order
        # add context to prevent infinite loop
        purchase_order = self.env['purchase.order'].with_context(
            from_intercompany_order=True).sudo().create(purchase_order_vals)
        
        sale_order.x_related_purchase_order_id = purchase_order.id

        return sale_order

