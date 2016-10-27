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
import openerp.addons.decimal_precision as dp


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
                        # import ipdb; ipdb.set_trace()
                        if production.product_id.transfer_lot:
                            for to_produce in production.move_created_ids:
                                new_lot_id = False
                                lot_obj = self.pool.get('stock.production.lot')
                                domain = [
                                    ('product_id', '=', to_produce.product_id.id),
                                    ('name', '=', lot.name),
                                    ('language', '=', lot.language.id),
                                ]
                                exist_lot_ids = lot_obj.search(cr, uid, domain)
                                if exist_lot_ids:
                                    new_lot_id = exist_lot_ids[0]
                                else:
                                    new_lot_id = lot_obj.copy(cr, uid, lot.id,
                                                               {'product_id': to_produce.product_id.id,
                                                                'name': lot.name,
                                                                'language': lot.language.id})
                                to_produce.write({'prodlot_id': new_lot_id})

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

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Propagar el lote, ya que en las producciones cuando ya tienes un poco
        de un movimiento consumido, digamos 30 unidades de 100, si recalculamos
        desde la aplicación de django la cantidad, el movimiento que quedaba que
        era de 70, pàsa a ser de 130 por ejemplo, quedan 70 por productir, 140-70
        es distinto de cero por lo que nos hará un copy el action_consume del módulo
        stock, no cogiendo el lote, lo cual es un error.
        """
        if not default:
            default = {}
        move = self.browse(cr, uid, id, context=context)
        if not default.get('prodlot_id', False) and move.prodlot_id:
            default.update({
                'prodlot_id': move.prodlot_id.id
            })
        return super(stock_move, self).copy(cr, uid, id, default, context)


class StockProductionLot(orm.Model):

    _inherit = "stock.production.lot"

    def _get_locations_fom_warehouse(self, cr, uid, warehouse_id, 
                                     context=None):
        res = []
        stock_locs = set()
        wh_obj = self.pool.get('stock.warehouse').browse(cr, uid,
                                                         warehouse_id,
                                                         context=context)
        if wh_obj.lot_input_id:
            stock_locs.add(wh_obj.lot_input_id.id)
        if wh_obj.lot_stock_id:
            stock_locs.add(wh_obj.lot_stock_id.id)
        if wh_obj.lot_output_id:
            stock_locs.add(wh_obj.lot_output_id.id)

        stock_locs = list(stock_locs)
        domain = [('id', 'child_of', stock_locs), ('usage', '=', 'internal')]
        res = self.pool.get('stock.location').search(cr, uid, domain,
                                                     context=context)
        return res

    def _get_stock(self, cr, uid, ids, field_name, arg, context=None):
        """ Gets stock of products for locations
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        if 'location_id' not in context:
            locations = self.pool.get('stock.location').search(cr, uid, [('usage', '=', 'internal')], context=context)
        else:
            locations = context['location_id'] and [context['location_id']] or []

        if context.get('warehouse_id', False):
            wh_id = context['warehouse_id']
            locations = self._get_locations_fom_warehouse(cr, uid, wh_id,
                                                          context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]

        res = {}.fromkeys(ids, 0.0)
        if locations:
            cr.execute('''select
                    prodlot_id,
                    sum(qty)
                from
                    stock_report_prodlots
                where
                    location_id IN %s and prodlot_id IN %s group by prodlot_id''',(tuple(locations),tuple(ids),))
            res.update(dict(cr.fetchall()))

        return res

    def _stock_search(self, cr, uid, obj, name, args, context=None):
        """ Searches Ids of products
        @return: Ids of locations
        """
        locations = self.pool.get('stock.location').search(cr, uid, [('usage', '=', 'internal')])

        if context.get('warehouse_id', False):
            wh_id = context['warehouse_id']
            locations = self._get_locations_fom_warehouse(cr, uid, wh_id,
                                                          context=context)
        cr.execute('''select
                prodlot_id,
                sum(qty)
            from
                stock_report_prodlots
            where
                location_id IN %s group by prodlot_id
            having  sum(qty) '''+ str(args[0][1]) + str(args[0][2]),(tuple(locations),))
        res = cr.fetchall()
        ids = [('id', 'in', map(lambda x: x[0], res))]
        return ids

    _columns = {
        'warehouse_id': fields.dummy(string='Warehouse',
                                     relation='stock.warehouse',
                                     type='many2one'),
        'stock_available': fields.function(_get_stock, fnct_search=_stock_search, type="float", string="Available", select=True,
            help="Current quantity of products with this Serial Number available in company warehouses",
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'active': fields.boolean('Active')

    }

    _defaults = {
        'active': True
    }
