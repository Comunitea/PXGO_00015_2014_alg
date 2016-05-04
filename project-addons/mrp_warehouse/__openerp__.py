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
    'name' : 'MRP warehouse',
    'version' : '1.1',
    'author' : 'Pexego',
    'category': 'MRP',
    'summary': "Warehouse field in production orders",
    'description': "Add warehouse field to production order to autocomplete stock \
locations",
    'website': 'http://www.pexego.es',
    'depends' : ['stock',
                 'mrp'],
    'data': ['mrp_production_view.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
