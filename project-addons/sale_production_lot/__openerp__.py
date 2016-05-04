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
    'name' : 'Production lot on sale',
    'version' : '1.1',
    'author' : 'Pexego',
    'category': 'Sales Management',
    'summary': 'Production lot on sales orders',
    'description': """
Creates two fields on sale order lines, one for barcode entering
like ean13##lot ex. 8437002393038##LOT2750
and the other for production lot selection.""",
    'website': 'http://www.pexego.es',
    'depends' : ['base',
                 'sale',
                 'sale_stock',
                 'stock'],
    'data': ['sale_view.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
