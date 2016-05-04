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
    'name' : 'Mrp customization',
    'version' : '1.1',
    'author' : 'Pexego',
    'category': 'Custom',
    'summary': 'Several changes in mrp orders',
    'description': """
Allow split mrp moves from web interface (mrp_webpanel_app)""",
    'website': 'http://www.pexego.es',
    'depends' : ['mrp',
                 'stock',
                 'product_expiry',
                 'mrp_automatic_lot',
                 'stock_picking_valued'],
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
