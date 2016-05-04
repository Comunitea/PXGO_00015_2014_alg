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
import time


class hr_task(orm.Model):
    _name = "hr.task"

    _columns = {
        'date': fields.date('Start date', required=True),
        'name': fields.char('Description', required=True),
        'note': fields.text('Notes'),
        'end_date': fields.date('End date', readonly=True),
        'state': fields.selection([('cancel', 'Cancelled'), ('draft', 'Draft'),
                                   ('open', 'Opened'), ('close', 'Closed')],
                                  'State', readonly=True, required=True),
        'product_id': fields.many2one('product.product', 'Work',
                                      required=True,
                                      domain=[('type', '=', 'service'),
                                              ('analytic_acc_id', '!=',
                                               False)]),
        'kg_moved': fields.float('KG moved', digits=(12, 4)),
        'work_line_ids': fields.one2many('hr.analytic.timesheet', 'hr_task_id',
                                         string="Timesheet")
    }

    _defaults = {
        'state': 'draft',
        'date': lambda *a: time.strftime("%Y-%m-%d")
    }

    def set_open(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'open',
                                  'date': time.strftime("%Y-%m-%d")},
                   context=context)

        return True

    def set_close(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'close',
                                  'end_date': time.strftime("%Y-%m-%d")},
                   context=context)
        for obj in self.browse(cr, uid, ids, context=context):
            total_hours = sum([x.unit_amount for x in obj.work_line_ids])
            if obj.kg_moved and total_hours:
                for line in obj.work_line_ids:
                    line.write({'kg_moved': ((line.unit_amount * obj.kg_moved)
                                             / total_hours)})

        return True

    def set_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

        return True

    def _check_product(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if not obj.product_id.analytic_acc_id:
            return False
        return True

    _constraints = [
        (_check_product, 'Cannot assign product without analytic account \
associated to activity', ['product_id']),
    ]
