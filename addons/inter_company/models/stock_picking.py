from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        
        for picking in self:
            if picking.picking_type_id.code == 'incoming':
                for line in picking.move_ids_without_package:
                    quant = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id', '=', 6)
                    ], limit=1)
                    
                    if quant:
                        quant.quantity -= line.quantity
                    else:
                        self.env['stock.quant'].sudo().create({
                            'product_id': line.product_id.id,
                            'location_id': 6,
                            'quantity': -line.quantity,
                        })            
            elif picking.picking_type_id.code == 'outgoing':
                for line in picking.move_ids_without_package:
                    quant = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id', '=', 6)
                    ], limit=1)
                    
                    if quant:
                        quant.quantity += line.quantity
                    else:
                        self.env['stock.quant'].sudo().create({
                            'product_id': line.product_id.id,
                            'location_id': 6,
                            'quantity': line.quantity,
                        })
      
        return res
