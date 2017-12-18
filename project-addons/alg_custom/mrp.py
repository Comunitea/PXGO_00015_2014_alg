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

    def _get_subflow_id(self, cr, uid, ids, mo, context=None):
        res = False
        if mo.picking_id:
            self.pool.get('stock.picking').fix_workflow(cr, uid, [mo.picking_id.id], context=context)
            domain = [('res_type', '=', 'stock.picking'),
                      ('res_id', '=', mo.picking_id.id)]
            inst_id = self.pool.get('workflow.instance').search(cr, uid, domain, limit=1, context=context)
            res = inst_id[0]
        return res

    # CREADO PARA  CORREGIR EL WORKFLOW DE LAS FACTURA
    def fix_workflow(self, cr, uid, ids, ctx):
        print "FIXING WORKFLOW"
        for mo in self.browse(cr, uid, ids, ctx):
            fixed = False
            mo_state = mo.state
            domain = [('res_type', '=', 'mrp.production'), ('res_id', '=', mo.id)]
            inst_id = self.pool.get('workflow.instance').search(cr, uid, domain, limit=1, context=ctx)
            if inst_id:
                inst_id = inst_id[0]

            if not inst_id:
                vals = {
                    'wkf_id': 5,
                    'uid': uid,
                    'res_id': mo.id,
                    'res_type': 'mrp.production',
                    'state': 'active'
                }
                inst_id = self.pool.get('workflow.instance').create(cr, uid, vals, ctx)
                print "CREADA INSTANCE"

            domain = [('inst_id', '=', inst_id)]
            item_id = self.pool.get('workflow.workitem').search(cr, uid, domain, limit=1, context=ctx)
            if not item_id:
                act_id = 39
                subflow_id = False
                state = 'complete'
                if mo_state == 'draft':
                    act_id = 37
                elif mo_state == 'confirmed':
                    act_id = 38
                    state = 'runing'
                    subflow_id = self._get_subflow_id(cr, uid, ids, mo, ctx)
                elif mo.state == 'ready':
                    act_id = 39
                vals = {
                    'inst_id': inst_id,
                    'act_id': act_id,  # For validate
                    'subflow_id': subflow_id,
                    'state': state
                }
                item_id = self.pool.get('workflow.workitem').create(cr, uid, vals, ctx)
                print "CREADO ITEM"
        return True
