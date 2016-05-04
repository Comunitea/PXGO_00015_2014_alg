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

from openerp.osv import orm, fields


class mrp_production(orm.Model):
    _inherit = 'mrp.production'

    _columns = {
        'work_line_ids': fields.one2many('hr.analytic.timesheet',
                                         'production_id', string="Timesheet",
                                         states={'done': [('readonly',
                                                           True)]}),
        'product_id': fields.many2one('product.product', 'Product',
                                      required=True, readonly=True,
                                      states={'draft': [('readonly', False)]},
                                      domain=[('analytic_acc_id', '!=',
                                               False)]),
    }

    def _check_product(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if not obj.product_id.analytic_acc_id:
            return False
        return True

    _constraints = [
        (_check_product, 'Cannot produce product without analytic account \
associated', ['product_id']),
    ]

    def _costs_generate(self, cr, uid, production):
        res = super(mrp_production, self)._costs_generate(cr, uid, production)
        if production.work_line_ids:
            lines = production.work_line_ids
            final_moves = [x for x in production.move_created_ids2
                           if x.state == 'done']
            total_hours = sum([x.unit_amount for x in lines])
            total_qty = sum([x.product_qty for x in final_moves])
            if total_hours:
                for line in lines:
                    line.write({'kg_moved': ((line.unit_amount * total_qty) /
                                             total_hours)})

        return res
