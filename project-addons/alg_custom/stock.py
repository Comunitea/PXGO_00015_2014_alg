# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Pexego (<http://www.pexego.es>).
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import fields, orm


class stock_move(orm.Model):

    _inherit = "stock.move"

    _columns = {
        'production_ids': fields.many2many('mrp.production',
                                           'mrp_production_move_ids',
                                           'move_id', 'production_id',
                                           'Consumed Products'),
        'scrapped': fields.boolean('Scrapped', readonly=True),
    }

    def apply_lots_in_production(self, cr, uid, ids, selected_lots):
        # REVIEW: qty available in lots must be in prod warehouse
        if selected_lots:
            lot_obj = self.pool.get('stock.production.lot')
            move_obj = self.pool.get('stock.move')
            move = move_obj.browse(cr, uid, ids[0])
            production = move.production_ids[0]
            qty = move.product_qty
            new_moves = []
            if 0 in selected_lots:
                selected_lots.remove(0)
            if selected_lots:
                selected_lots = lot_obj.browse(cr, uid, selected_lots)
                # order by expiry_date and qty
                selected_lots = sorted(selected_lots,
                                       key=lambda x: (x.life_date,
                                                      x.stock_available))
                for lot in selected_lots:
                    if lot.stock_available >= qty:
                        move.write({'product_qty': qty,
                                    'prodlot_id': lot.id})
                        qty = 0.0

                        ## ADDED FOR mrp_automatic_lot and tranfer the lot to the products to produce for transfering
                        #  the name to the produced lot
                        if production.product_id.transfer_lot:
                            for to_produce in production.move_created_ids:
                                if to_produce.prodlot_id:
                                    lot_obj.write(cr, uid, to_produce.prodlot_id.id, {'name': lot.name})
                        if production.product_id.transfer_lot_date:
                            for to_produce in production.move_created_ids:
                                if to_produce.prodlot_id:
                                    lot_obj.write(cr, uid,
                                                  to_produce.prodlot_id.id,
                                                  {'use_date': lot.use_date,
                                                   'life_date': lot.life_date
                                                   })
                        break
                    else:
                        qty -= lot.stock_available
                        nm = move_obj.copy(cr, uid, move.id,
                                           {'product_qty': lot.stock_available,
                                            'prodlot_id': lot.id,
                                            'state': move.state})
                        new_moves.append(nm)

            if qty:
                move.write({'product_qty': qty,
                            'prodlot_id': False})

            if new_moves:
                production.write({'move_lines': [4, new_moves]})

            return True
