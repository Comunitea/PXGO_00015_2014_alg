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
from osv import osv, fields
import decimal_precision as dp
import time
import netsvc
from tools.translate import _

class valid_stock_moves(osv.osv):
    """View that filter stock_moves by not state = 'cancel' Use this view to show traceability tree"""
    _inherit = "valid.stock.moves"
    _columns ={
    'split_id': fields.many2one('split.lot', 'Split', readonly=True,
                         select=True)
    }

    def init(self, cr):
        ##Sobreeescrito desde full_stock_traceability
        """creates view when install"""
        cr.execute("""
            create or replace view valid_stock_moves as (
                select stock_move.id as id,stock_move.name as name,stock_move.product_id as product_id,product_qty,product_uom,prodlot_id,stock_production_lot.life_date as expiry_date,
                    supplier,tracking_id,product_packaging,picking_id,location_id,location_dest_id,stock_move.date as date,
                    date_expected,state,production_id,split_id
                from stock_move left join stock_production_lot on stock_move.prodlot_id = stock_production_lot.id
                where state not in ('cancel')
            )""")