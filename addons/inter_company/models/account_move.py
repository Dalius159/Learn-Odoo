from odoo import models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Automatically create a vendor bill when a customer invoice is created
    def action_post(self):
        res = super(AccountMove, self).action_post()

        for move in self:
            # If the invoice is created from a sale order,
            if move.move_type == 'out_invoice':
                sale_order = move.invoice_origin and self.env['sale.order'].sudo().search(
                    [('name', '=', move.invoice_origin)], limit=1)
                
                # If the sale order has a related purchase order,
                if sale_order and sale_order.x_related_purchase_order_id:
                    purchase_order = sale_order.sudo().x_related_purchase_order_id

                    if purchase_order.picking_ids.state != 'done':
                        raise ValidationError(
                            "The related purchase order must have a done picking before creating the vendor bill.")
                        
                    
                    bill = self.env['account.move'].sudo().create({
                        'company_id': purchase_order.company_id.id,
                        'partner_id': purchase_order.partner_id.id,
                        'move_type': 'in_invoice', 
                        'purchase_id': purchase_order.id,
                    })
                    
                    # Create a vendor bill with the same products and quantities as the customer invoice
                    for so_line, po_line in zip(self.invoice_line_ids, purchase_order.order_line):
                        self.env['account.move.line'].sudo().create({
                            'move_id': bill.id,
                            'product_id': po_line.product_id.id,
                            'quantity': so_line.quantity, 
                            'price_unit': po_line.price_unit,
                            'purchase_line_id': po_line.id,
                        })

        return res
