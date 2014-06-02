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


class res_users(orm.Model):
    _inherit = "res.users"
    _columns = {
        'code': fields.char('Code', size=8)
    }

    def name_search(self, cr, uid, name='', args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, uid, [('login', '=', name)] + args,
                              limit=limit, context=context)
            ids.extend(self.search(cr, uid, [('code', '=', name)] + args,
                                   limit=limit, context=context))
        if not ids:
            ids = self.search(cr, uid, [('name', operator, name)] + args,
                              limit=limit, context=context)
        else:
            ids = list(set(ids))
        return self.name_get(cr, uid, ids, context=context)
