# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
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
from osv import osv, fields
import decimal_precision as dp
import time
import netsvc
from tools.translate import _


class split_lot_line(osv.osv):
    _name= 'split.lot.line'
    _columns = {
        'qty': fields.float('Cantidad', required=True),
        'new_lot_id': fields.many2one('stock.production.lot', 'Nuevo lote', required=True),
        'split_id': fields.many2one('split.lot'),
    }
split_lot_line()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'split_id': fields.many2one('split.lot', 'División de lote')
    }
stock_move()

class split_lot(osv.osv):

    _name= 'split.lot'

    _columns = {
        'lot_id': fields.many2one('stock.production.lot', 'Lote original',
                                  required=True),

        'product_id': fields.many2one('product.product','Producto',
                                      required=True),
        'location_id' : fields.many2one('stock.location' ,'Ubicación de '
                                                          'origen',  required=True),
        'location_dest_id' : fields.many2one('stock.location' ,'Ubicación de '
                                                          'destino',
                                             help='Ubicación de estino del '
                                                  'lote original ('
                                                  'normalmente producción)',
                                             required=True),
        'new_lot_lines': fields.one2many('split.lot.line', 'split_id',
                                         'Nuevos lotes'),
        'move_ids': fields.one2many('stock.move', 'split_id', 'Movimientos '
                                                              'generados'),
        'state': fields.selection([('draft','Borrador'),('done',
                                                   'Done')], 'Estate ',
                                  required=True,)

    }
    _defaults = {
        'state': 'draft',
    }

    def onchange_lot_id (self, cr, uid,ids, lot_id, context=None):
        lot_obj = self.pool.get('stock.production.lot')
        lot = lot_obj.browse(cr,uid, lot_id, context)
        return {'value' : {'product_id': lot.product_id and
                                          lot.product_id.id}}


    def action_split_lots(self, cr, uid, ids, context):
        lot_obj = self.pool.get('stock.production.lot')
        move_obj = self.pool.get('stock.move')
        for split in self.browse(cr, uid, ids):
            lot = split.lot_id

            qty_tot = 0
            split_move_ids = []

            for line in split.new_lot_lines:
                qty_tot += line.qty

            assert qty_tot <=  lot.stock_available, 'No se puede ' \
                                'realizar la división. La cantidad a ' \
                                                     'generar es mayor ' \
                                                     'que la disponible'
            #Crea movimiento del lote consumido
            orig_line_vals = {
                'product_id': lot.product_id.id,
                'product_qty': qty_tot,
                'product_uom': lot.product_id.uom_id.id,
                'location_dest_id': split.location_dest_id.id,
                'location_id': split.location_id.id,
                'prodlot_id': split.lot_id.id,
                'name': 'Consume lot for split' + lot.name,
                'split_id':split.id
            }
            new_move_id= move_obj.create(cr, uid,orig_line_vals)
            move_obj.action_confirm(cr, uid, [new_move_id])

            # Crea los movimientos de creacion de los nuevos lotes
            for line in split.new_lot_lines:
                qty_tot += line.qty
                dest_line_vals = {
                    'product_id': lot.product_id.id,
                    'product_qty': line.qty,
                    'product_uom': lot.product_id.uom_id.id,
                    'location_dest_id': split.location_id.id,
                    'location_id': split.location_dest_id.id,
                    'prodlot_id': line.new_lot_id.id,
                    'name': 'Split lot ' + lot.name,
                    'split_id':split.id
                }
                dest_move_id = move_obj.create(cr, uid, dest_line_vals)
                move_obj.action_confirm(cr, uid, [dest_move_id])
                split_move_ids.append(dest_move_id)

            move_obj.action_done(cr, uid, [new_move_id])
            move_obj.action_done(cr, uid, split_move_ids)
            for move_id in split_move_ids:
                move_obj.write (cr, uid,new_move_id ,
                             {'move_history_ids': [(4, move_id )]})
            #move_obj.write (cr, uid, split_move_ids,
            #                 {'move_history_ids2': [(6, 0, [new_move_id])]})



            self.write(cr, uid, ids, {'state':'done'})

split_lot()

