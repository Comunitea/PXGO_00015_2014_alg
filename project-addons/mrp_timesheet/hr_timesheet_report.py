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

from openerp import tools
from openerp.osv import fields,osv

class hr_timesheet_report_custom(osv.osv):

    _inherit = "hr.timesheet.report.custom"

    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production',
                                         readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'hr_timesheet_report_custom')
        cr.execute("""
            create or replace view hr_timesheet_report_custom as (
                select
                    min(t.id) as id,
                    l.date as date,
                    to_char(l.date, 'YYYY-MM-DD') as day,
                    to_char(l.date,'YYYY') as year,
                    to_char(l.date,'MM') as month,
                    sum(l.amount) as cost,
                    sum(l.unit_amount) as quantity,
                    l.account_id as account_id,
                    l.journal_id as journal_id,
                    l.product_id as product_id,
                    l.general_account_id as general_account_id,
                    l.user_id as user_id,
                    l.company_id as company_id,
                    l.currency_id as currency_id,
                    t.kg_moved as kg_moved,
                    t.hr_task_id as hr_task_id,
                    t.production_id as production_id
                from
                    hr_analytic_timesheet as t
                    left join account_analytic_line as l ON (t.line_id=l.id)
                group by
                    l.date,
                    l.account_id,
                    l.product_id,
                    l.general_account_id,
                    l.journal_id,
                    l.user_id,
                    l.company_id,
                    l.currency_id,
                    t.kg_moved,
                    t.hr_task_id,
                    t.production_id
            )
        """)

hr_timesheet_report_custom()
