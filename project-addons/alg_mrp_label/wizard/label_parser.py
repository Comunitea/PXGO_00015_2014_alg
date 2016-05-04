# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import pooler
import jasper_reports
from datetime import datetime
from tools.translate import _
import math


def parser( cr, uid, ids, data, context ):
    pool = pooler.get_pool(cr.dbname)
    ids = []
    name = 'report.mrp.production.label'
    model = 'mrp.production'
    records = []
    data_source = 'records'
    parameters = {}
    line_obj = pool.get('print.label.moves')
    user = pool.get('res.users').browse(cr, uid, uid)
    company_name = user.company_id.name

    if data['form'].get('move_ids', []):
        for move in line_obj.browse(cr, uid, data['form']['move_ids'], context):
            label_qty = int(math.ceil(move.qty / (move.qty_box or 1.0)))
            ctx = context.copy()
            ctx['lang'] = move.language.code
            move = line_obj.browse(cr, uid, move.id, ctx)
            for rec in range(0, label_qty):
                records.append({
                    'product': move.product_id.name,
                    'lang': move.language.code,
                    'lot': move.lot_id.name,
                    'use_date': move.lot_id.use_date,
                    'ean13': move.product_id.ean13,
                    'qty': move.qty_box,
                    'company': company_name})
    return {
        'ids': ids,
        'name': name,
        'model': model,
        'records': records,
        'data_source': data_source,
        'parameters': parameters,
    }
jasper_reports.report_jasper( 'report.mrp.production.label', 'mrp.production', parser )
