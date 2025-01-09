from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError


class CustomWebsiteSale(WebsiteSale):
    
    # Override the pricelist method to allow check valid customer to use mkm code
    @route(['/shop/pricelist'], type='http', auth="public", website=True, sitemap=False)
    def pricelist(self, promo, **post):
        redirect = post.get('r', '/shop/cart')
        # empty promo code is used to reset/remove pricelist (see `sale_get_order()`)
        if promo:
            pricelist_sudo = request.env['product.pricelist'].sudo().search([('code', '=', promo)], limit=1)
            if not (pricelist_sudo and request.website.is_pricelist_available(pricelist_sudo.id)):
                return request.redirect("%s?code_not_available=1" % redirect)
            
            current_user = request.env.user.partner_id
            if pricelist_sudo.x_customer_id and pricelist_sudo.x_customer_id != current_user:
                raise ValidationError("You are not authorized to use this promo code.")

            request.session['website_sale_current_pl'] = pricelist_sudo.id
            order_sudo = request.website.sale_get_order()
            if order_sudo:
                order_sudo._cart_update_pricelist(pricelist_id=pricelist_sudo.id)
        else:
            # Reset the pricelist if empty promo code is given
            request.session.pop('website_sale_current_pl', None)
            order_sudo = request.website.sale_get_order()
            if order_sudo:
                pl_before = order_sudo.pricelist_id
                order_sudo._compute_pricelist_id()
                if order_sudo.pricelist_id != pl_before:
                    order_sudo._recompute_prices()
        return request.redirect(redirect)