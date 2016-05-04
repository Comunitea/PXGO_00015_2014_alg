# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
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

from osv import fields, osv


class generate_requisitions_wizard(osv.osv_memory):
    _name = 'generate.requisitions.wizard'

    def generate(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        wiz = self.browse(cr, uid, ids, context)
        req_obj = self.pool.get('purchase.requisition')
        unsf_obj = self.pool.get('product.stock.unsafety')
        if wiz:
            for unsafety in wiz[0].unsafety_ids:
                qty = unsafety.min_fixed - (unsafety.real_stock
                                            + unsafety.incoming_qty)
                if qty > 0:
                    args_line = {'product_id': unsafety.product_id.id,
                                 'product_qty': qty,
                                 'product_uom_id':
                                 unsafety.product_id.uom_id.id,
                                 'requisition_id': None}
                    args_requisition = {'origin': unsafety.name,
                                        'date_start': unsafety.date,
                                        'purchase_ids': None,
                                        'line_ids': [(0, 0, args_line)],
                                        }
                    req_obj.create(cr, uid, args_requisition, context)
                    unsf_obj.write(cr, uid, unsafety.id,
                                   {'state': 'finalized'},
                                   context)
                else:
                    unsf_obj.write(cr, uid, unsafety.id,
                                   {'state': 'cancelled'},
                                   context)
        return

    def _get_unsafety(self, cr, uid, context=None):
        if not context or not context['active_ids']:
            return []
        return context['active_ids']

    _columns = {'unsafety_ids': fields.many2many(
                'product.stock.unsafety',
                'purchase_order_generate_requisitions_rel', 'unsafety_id',
                'wizard_id', 'unsafety')}

    _defaults = {
        'unsafety_ids': _get_unsafety,
    }
