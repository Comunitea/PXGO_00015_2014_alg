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


class MrpProduction(orm.Model):

    _inherit = "mrp.production"

    _columns = {
        'issue_ids': fields.one2many('alg.issue', 'production_id', 'Issues'),
        'part_ids': fields.one2many('hr.task', 'production_id', 'Clean Parts'),
        'final_lot_id': fields.related('move_created_ids2', 'prodlot_id',
                                       type='many2one',
                                       relation="stock.production.lot",
                                       string="Final lot"),
        'consume_date': fields.related('final_lot_id', 'use_date',
                                       type='date', string='Consume date')
    }
