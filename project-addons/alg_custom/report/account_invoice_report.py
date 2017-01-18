# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv


class account_invoice_report(osv.osv):

    _inherit = "account.invoice.report"

    _columns = {
        'country_id': fields.many2one('res.country', 'Country'),
        'ref': fields.char('Customer reference'),
    }

    def _select(self):
      return  super(account_invoice_report, self)._select() + ", sub.ref, sub.country_id"

    def _sub_select(self):
        return  super(account_invoice_report, self)._sub_select() + ", rp.ref AS ref, rp.country_id AS country_id"

    def _group_by(self):
        return super(account_invoice_report, self)._group_by() + ", rp.ref, rp.country_id"

    def _from(self):
        return super(account_invoice_report, self)._from() + " INNER JOIN res_partner rp ON rp.id = ai.partner_id"
