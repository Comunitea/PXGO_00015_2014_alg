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

from openerp.osv import orm
from openerp import netsvc



# CREADO PARA  CORREGIR EL WORKFLOW DE LAS FACTURAS

class AccountInvoice(orm.Model):

    _inherit = "account.invoice"

    def fix_workflow(self, cr, uid, ids, ctx):
        print "FIXING WORKFLOW"
        wf_service = netsvc.LocalService("workflow")
        for inv in self.browse(cr, uid, ids, ctx):
            fixed = False
            inv_state = inv.state
            domain = [('res_type', '=', 'account.invoice'), ('res_id', '=', inv.id)]
            inst_id = self.pool.get('workflow.instance').search(cr, uid, domain, limit=1, context=ctx)
            if not inst_id:
                vals = {
                    'wkf_id': 1,
                    'uid': uid,
                    'res_id': inv.id,
                    'res_type': 'account.invoice',
                    'state': 'active'
                }
                inst_id = self.pool.get('workflow.instance').create(cr, uid, vals, ctx)
                print "CREADA INSTANCE"
                fixed = True

            domain = [('inst_id', '=', inst_id)]
            item_id = self.pool.get('workflow.workitem').search(cr, uid, domain, limit=1, context=ctx)
            if not item_id:
                vals = {
                    'inst_id': inst_id,
                    'act_id': 3,  # For validate
                    'state': 'complete'
                }
                item_id = self.pool.get('workflow.workitem').create(cr, uid, vals, ctx)
                print "CREADO ITEM"
                fixed = True

            if fixed:
                wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
                print "FACTURA CANCELADA"
                self.action_cancel_draft(cr, uid, [inv.id])
                print "FACTURA BORRADOR"
                if inv_state == 'open':
                    wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_open', cr)
                    print "FACTURA VALIDADA"
                print "DONE"
        return True