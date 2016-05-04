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


class mrp_production(orm.Model):
    _inherit = "mrp.production"

    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse',
                                        readonly=True,
                                        states={'draft': [('readonly',
                                                           False)]}),
        'notes': fields.text('Notes')
    }

    _defaults = {
        'warehouse_id': lambda self, cr, uid, c:
        self.pool['stock.warehouse'].search(cr, uid, [], context=c) and
        self.pool['stock.warehouse'].search(cr, uid, [], context=c)[0] or
        False
    }

    def on_change_warehouse(self, cr, uid, ids, warehouse, context=None):
        res = {}
        if warehouse:
            warehouse = self.pool['stock.warehouse'].browse(cr, uid, warehouse,
                                                            context=context)
            res['value'] = {'location_src_id': warehouse.lot_stock_id.id,
                            'location_dest_id': warehouse.lot_stock_id.id}

        return res

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        if vals.get('warehouse_id') and not vals.get('location_src_id') and \
                not vals.get('location_dest_id'):
                warehouse = self.pool['stock.warehouse'].\
                    browse(cr, uid, vals['warehouse_id'], context=context)
                vals['location_src_id'] = warehouse.lot_stock_id.id
                vals['location_dest_id'] = warehouse.lot_stock_id.id

        return super(mrp_production, self).create(cr, uid, vals,
                                                  context=context)
