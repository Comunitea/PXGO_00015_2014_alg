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
import time


class AlgIssue(orm.Model):

    _name = "alg.issue"

    _columns = {
        'name': fields.char('Description', size=256),
        'date': fields.date('Date', readonly=True),
        'type': fields.selection([('production', 'In Production'),
                                  ('machine', 'In Machine')],
                                 string="Issue type"),
        'notes': fields.text('Notes'),
        'production_id': fields.many2one('mrp.production', 'Production')
    }

    _defaults = {
        'date': lambda *a: time.strftime("%Y-%m-%d"),
        'type': 'production'
    }
