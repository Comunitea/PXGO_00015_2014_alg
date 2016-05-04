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

{
    'name' : 'Employee\'s activity timesheet',
    'version' : '1.1',
    'author' : 'Pexego',
    'category': 'HR',
    'summary': "Simple management of employee's tasks",
    'description': """Activities associated to services and analytic accounts
where employee's input their time. Similar to projects but simplified""",
    'website': 'http://www.pexego.es',
    'depends' : ['analytic',
                 'product',
                 'hr',
                 'hr_attendance',
                 'hr_timesheet'],
    'data': ['hr_task_view.xml',
             'product_view.xml',
             'hr_timesheet_report_view.xml',
             'hr_analytic_timesheet.xml',
             'security/ir.model.access.csv'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
