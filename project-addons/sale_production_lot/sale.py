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
import netsvc


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    _columns = {
        'barcode_enter': fields.char('Code', size=64),
        'prodlot_id': fields.many2one('stock.production.lot', 'Lot')
    }

    def onchange_barcode_enter(self, cr, uid, ids, barcode):
        res = {}
        if barcode:
            barcode_data = barcode.split("##")
            product_obj = self.pool['product.product']
            product_ids = product_obj.search(cr, uid, [('ean13', '=',
                                                        barcode_data[0])])
            if product_ids:
                res['value'] = {'product_id': product_ids[0]}
                if len(barcode_data) == 2:
                    plot_obj = self.pool['stock.production.lot']
                    lot_ids = plot_obj.search(cr, uid, [('product_id', '=',
                                                         product_ids[0]),
                                                        ('name', '=',
                                                         barcode_data[1])])
                    if lot_ids:
                        res['value']['prodlot_id'] = lot_ids[0]
                    else:
                        res['value']['prodlot_id'] = False

        return res


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id,
                                 date_planned, context=None):
        if context is None:
            context = {}
        res = super(sale_order, self)._prepare_order_line_move(cr, uid, order,
                                                               line,
                                                               picking_id,
                                                               date_planned,
                                                               context=context)
        if line.prodlot_id:
            res['prodlot_id'] = line.prodlot_id.id

        return res

    def action_ship_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(sale_order, self).action_ship_create(cr, uid, ids,
                                                         context=context)
        wf_service = netsvc.LocalService("workflow")

        for order in self.browse(cr, uid, ids, context=context):
            for picking in order.picking_ids:
                if picking.state == 'confirmed':
                    picking.force_assign()
                    wf_service.trg_validate(uid, 'stock.picking', picking.id,
                                            'button_done', cr)

        return res
