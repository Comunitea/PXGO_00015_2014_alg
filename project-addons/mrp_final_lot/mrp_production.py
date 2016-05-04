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

    def _get_lot(self, cursor, user, ids, name, args, context=None):
        res = {}

        for production in self.browse(cursor, user, ids, context=context):
            res[production.id] = False
            for move in production.move_created_ids:
                if move.product_id.id == production.product_id.id:
                    res[production.id] = move.prodlot_id.id
                    break
            if not res[production.id]:
                for move in production.move_created_ids2:
                    if move.product_id.id == production.product_id.id:
                        res[production.id] = move.prodlot_id.id
        return res

    _columns = {
        'lot_id': fields.function(_get_lot, string='Lot', type='many2one',
                                  relation='stock.production.lot'),
    }

