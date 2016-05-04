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
    'name' : 'MRP timesheet',
    'version' : '1.1',
    'author' : 'Pexego',
    'category': 'MRP',
    'summary': "Employee's times input into production orders",
    'description': """Employee's times input into production orders""",
    'website': 'http://www.pexego.es',
    'depends' : ['analytic',
                 'mrp',
                 'hr',
                 'hr_timesheet',
                 'hr_activity_timesheet'],
    'data': ['mrp_production_view.xml',
             'hr_timesheet_report_view.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
