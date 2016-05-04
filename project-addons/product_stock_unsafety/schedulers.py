# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv
from openerp import pooler
from datetime import date


class procurement_order(osv.Model):
    _inherit = 'procurement.order'

    def _procure_orderpoint_confirm(self, cr, uid, automatic=False,
                                    use_new_cursor=False, context=None,
                                    user_id=False):
        if context is None:
            context = {}
        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        stock_unsafety = self.pool.get('product.stock.unsafety')
        product = self.pool.get('product.product')
        offset = 0
        ids = [1]
        seller = False
        if automatic:
            self.create_automatic_op(cr, uid, context=context)
        while ids:
            ids = product.search(cr, uid, [], offset=offset, limit=100)
            for prod in product.browse(cr, uid, ids, context=context):
                orderpoint_ids = orderpoint_obj.search(cr, uid,
                                                       [('product_id', '=',
                                                         prod.id),
                                                        ('from_date', '<=',
                                                         date.today()),
                                                        ('to_date', '>=',
                                                         date.today()), ])
                if not orderpoint_ids:
                    orderpoint_ids = orderpoint_obj.search(cr, uid,
                                                           [('product_id', '=',
                                                             prod.id),
                                                            ('from_date', '=',
                                                             False),
                                                            ('to_date', '=',
                                                             False)])
                if not orderpoint_ids:
                    orderpoint_ids = []
                for orderpoint in orderpoint_obj.browse(cr, uid,
                                                        orderpoint_ids,
                                                        context=context):
                    virtual_stock = prod.virtual_stock_conservative
                    days_sale = prod.remaining_days_sale
                    if (orderpoint.min_days_id
                        and days_sale < orderpoint.min_days_id.days_sale or
                        virtual_stock < orderpoint.product_min_qty) \
                            and prod.active:

                        if prod.seller_ids:
                            seller = prod.seller_ids[0].name.id
                            state = 'in_progress'
                        else:
                            state = 'exception'
                        vals = {'product_id': prod.id,
                                'supplier_id': seller,
                                'min_fixed': orderpoint.product_min_qty,
                                'real_stock': prod.qty_available,
                                'virtual_stock': virtual_stock,
                                'responsible': uid,
                                'state': state}
                        daylysales = product.calc_remaining_days(cr, uid,
                                                                 [prod.id],
                                                                 context)
                        if daylysales and orderpoint.min_days_id.days_sale:
                            vals['minimum_proposal'] = daylysales * \
                                orderpoint.min_days_id.days_sale
                        if daylysales \
                           and days_sale < orderpoint.min_days_id.days_sale:
                                vals['name'] = 'Dias de venta'
                        if virtual_stock < orderpoint.product_min_qty:
                            vals['name'] = 'stock minimo'
                        stock_unsafety.create_or_write(cr, uid, vals,
                                                       context=context)
                offset += len(ids)
                if use_new_cursor:
                    cr.commit()
        if use_new_cursor:
            cr.commit()
            cr.close()
        return {}
