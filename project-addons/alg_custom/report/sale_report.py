# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import tools
from openerp.osv import fields, osv


class sale_report(osv.osv):

    _inherit = 'sale.report'

    _columns = {
        'lot_id': fields.many2one('stock.production.lot', 'Lot'),
        'country_id': fields.many2one('res.country', 'Country'),
        'lang_id': fields.many2one('res.lang', 'Language', select=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sale_report')
        cr.execute("""
            create or replace view sale_report as (
                select
                    min(l.id) as id,
                    l.product_id as product_id,
                    l.prodlot_id as lot_id,
                    rp.country_id as country_id,
                    spl.language as lang_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.product_uom_qty * l.price_unit * (100.0-l.discount) / 100.0) as price_total,
                    count(*) as nbr,
                    s.date_order as date,
                    s.date_confirm as date_confirm,
                    to_char(s.date_order, 'YYYY') as year,
                    to_char(s.date_order, 'MM') as month,
                    to_char(s.date_order, 'YYYY-MM-DD') as day,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.shop_id as shop_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    s.state,
                    t.categ_id as categ_id,
                    s.shipped,
                    s.shipped::integer as shipped_qty_1,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id
                from
                    sale_order_line l
                        join sale_order s on (l.order_id=s.id)
                        left join product_product p on (l.product_id=p.id)
                        left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=l.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id)
                        left join res_partner rp on (rp.id =s.partner_id)
                        left join stock_production_lot spl on (spl.id = l.prodlot_id)
                        left join res_lang rl on (rl.id = spl.language)
                group by
                    l.product_id,
                    l.prodlot_id,
                    rp.country_id,
                    spl.language,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.shop_id,
                    s.company_id,
                    s.state,
                    s.shipped,
                    s.pricelist_id,
                    s.project_id
            )
        """)
sale_report()
