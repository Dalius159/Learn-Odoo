from odoo import models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()

        for move in self:
            # if move.move_type == 'in_invoice':
            #     move = self.env['account.move'].browse(87)
            #     _logger.info("Aloha: Purchase ID is %s", move.purchase_id.id)
            #     purchase_order = move.purchase_id
            #     if purchase_order:
            #         sale_order = purchase_order.related_sale_order_id
                    
            #         if sale_order:
            #             invoice = self.env['account.move'].sudo().search([
            #                 ('invoice_origin', '=', sale_order.name),
            #                 ('move_type', '=', 'out_invoice'),
            #             ], limit=1)
                        
            #             if invoice and invoice.state == 'posted':
            #                 invoice.sudo().write({'state': 'draft'})
            #                 # new_invoice = self.env['account.move'].sudo().create({
            #                 #     'company_id': sale_order.company_id.id,
            #                 #     'partner_id': sale_order.partner_id.id,
            #                 #     'move_type': 'out_invoice',
            #                 #     'invoice_origin': sale_order.name,
            #                 # })
                            
            #                 # for bill_line in move.invoice_line_ids:
            #                 #     self.env['account.move.line'].sudo().create({
            #                 #         'move_id': new_invoice.id,
            #                 #         'product_id': bill_line.product_id.id,
            #                 #         'quantity': bill_line.quantity,  # Số lượng đã xác nhận
            #                 #         'price_unit': bill_line.price_unit,
            #                 #     })

            #                 # # Đóng hóa đơn cũ
            #                 # invoice.sudo().button_cancel()
            #             else :
            #                 raise ValidationError("No invoice.")
            #         else:
            #             raise ValidationError("No sale order.")
            #     else:
            #         raise ValidationError("No related purchase order.")
                                                                
            if move.move_type == 'out_invoice':
                sale_order = move.invoice_origin and self.env['sale.order'].sudo().search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order and sale_order.related_purchase_order_id:
                    purchase_order = sale_order.related_purchase_order_id

                    if purchase_order.picking_ids.state != 'done':
                        raise ValidationError("The related purchase order must have a done picking before creating the vendor bill.")

                    bill = self.env['account.move'].sudo().create({
                        'company_id': purchase_order.company_id.id,
                        'partner_id': purchase_order.partner_id.id,
                        'move_type': 'in_invoice', 
                        'purchase_id': purchase_order.id,
                    })

                    for so_line, po_line in zip(self.invoice_line_ids, purchase_order.order_line):
                        self.env['account.move.line'].sudo().create({
                            'move_id': bill.id,
                            'product_id': po_line.product_id.id,
                            'quantity': so_line.quantity, 
                            'price_unit': po_line.price_unit,
                            'purchase_line_id': po_line.id,
                        })

        return res
