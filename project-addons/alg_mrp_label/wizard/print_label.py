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
import openerp.addons.decimal_precision as dp


class print_label(osv.osv_memory):
    _name = "print.label"
    _columns = {
        'move_ids': fields.one2many('print.label.moves', 'wizard_id',
                                    string="Lines")
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        production_id = context.get('active_ids', [])
        production_obj = self.pool.get('mrp.production')

        production = production_obj.browse(cr, uid, production_id[0])
        if production.move_created_ids2:
            if 'move_ids' in fields:
                moves = []
                for move in production.move_created_ids2:
                    moves.append({'product_id': move.product_id.id,
                                  'qty': move.product_qty,
                                  'lot_id': move.prodlot_id.id,
                                  'language': move.prodlot_id.language and \
                                              move.prodlot_id.language.id or \
                                              False,
                                  'qty_box': 0})
                if moves:
                    res['move_ids'] = moves
        return res

    def print_label(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        datas = {
            'ids': context.get('active_ids', []),
            'model': 'mrp.production',
            'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'mrp.production.label',
            'datas': datas
            }


class print_label_moves(osv.osv_memory):
    _name = 'print.label.moves'
    _columns = {
        'wizard_id': fields.many2one('print.label', 'Wizard'),
        'product_id': fields.many2one('product.product', 'Product',
                                      required=True),
        'qty': fields.float("Quantity",
                            digits_compute=
                            dp.get_precision('Product Unit of Measure'),
                            required=True),
        'lot_id': fields.many2one('stock.production.lot', 'Lot',
                                  required=True),
        'language': fields.many2one('res.lang', string = 'Lang',
                                   readonly=True),
        'qty_box': fields.integer('Qty/Box', required=True)
    }

