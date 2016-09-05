# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Pexego (<http://www.pexego.es>).
#    $Omar Castiñeira Saavedra$
#    $Alejandro Núñez Liz$
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

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import redirect
from models import Usuario
import datetime,time
from django.utils import timezone
from datetime import datetime


def timestamp(date):
    return time.mktime(date.timetuple())/3600

def home(request):
    # Busco usuario,si exite,para el tiempo y crea nuevo tiempo de trabajo
    # Si no exite,creo una nuevo tiempo de trabajo
    # guardo en una session, el id del usuario para futuras busquedas

    template = loader.get_template('conector/index.html')
    context={}

    if request.method == 'POST':
        from erp import POOL, DB, USER
        user_obj = POOL.get('res.users')
        cursor = DB.cursor()
        try:
            codigo = int(request.POST.get("code",False))


            user_ids = user_obj.search(cursor, USER, [('code', '=', codigo)], order="login ASC")
            users = user_obj.browse(cursor, USER, user_ids)
            if users:
                try:

                    user_access = Usuario.objects.get(code=str(codigo))
                    #user_access.end = timezone.now()

                    user_access.save()
                    #user_access = Usuario(code=codigo, name = users[0].name )
                    #user_access.save()

                except:
                    user_access = Usuario(code=str(codigo), name=users[0].name)
                    user_access.save()
                hr_obj = POOL.get('hr.employee')
                hr_ids = hr_obj.search(cursor, USER, [('user_id', '=',
                                                        users[0].id )],
                                       order="login ASC")
                if not hr_ids:
                     return HttpResponse('<script '
                                         'type="text/javascript">window.alert("ESTE USUARIO NO TIENE EMPLEADO CONFIGURADO EN EL ERP!!!");window.location.replace("/");</script>')

                request.session['codigo'] = user_access.code
                return selector(request)
            else:
                context = RequestContext(request, {
                    'nouser': False,
                    'inicio': True,
                })
                return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/");</script>')
            pass
        finally:

            cursor.commit()
            cursor.close()
    else:
        users_list = Usuario.objects.filter()
        context = RequestContext(request, {
                'users_list': users_list,
                'inicio': True,
            })
        return HttpResponse(template.render(context))

def selector(request):
    template = loader.get_template('conector/selector.html')

    users_list = Usuario.objects.filter()

    context = RequestContext(request, {
            'users_list': users_list,
            'codigo': request.session['codigo'],
    })
    return HttpResponse(template.render(context))


def productos(request):
    template = loader.get_template('conector/productos.html')
    context={}
    oerp_ctx = {'lang': 'es_ES'}
    from erp import POOL, DB, USER
    cursor = DB.cursor()
    product_obj = POOL.get('mrp.production')


    try:
        product_ids = product_obj.search(cursor, USER, [('state', 'not in', ['done','cancel'])], order="name ASC")
        products = product_obj.browse(cursor, USER, product_ids, context=oerp_ctx)

        users_list = Usuario.objects.filter()





        context = RequestContext(request, {

            'users_list': users_list,
            'products_list': products,
            'codigo': request.session['codigo'],

        })
    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/productos/");</script>')
        pass
    finally:
        return HttpResponse(template.render(context))
        cursor.commit()
        cursor.close()


def nota(request, id):
    if request.method == 'POST':
        from erp import POOL, DB, USER
        cursor = DB.cursor()
        move_obj = POOL.get('stock.move')
        lot_obj = POOL.get('stock.production.lot')
        production_obj = POOL.get('mrp.production')
        try:
            production_obj.write(cursor, USER, [int(id)], {'notes':
                                                              request.POST.get("notes")})
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()
            return HttpResponse('<script type="text/javascript">opener.location.reload();window.close()</script>')
    else:
        template = loader.get_template('conector/nota.html')
        context={}
        oerp_ctx = {'lang': 'es_ES'}
        from erp import POOL, DB, USER
        cursor = DB.cursor()

        production_obj = POOL.get('mrp.production')
        try:
            production = production_obj.browse(cursor, USER, [int(id)], context=oerp_ctx)
            print production[0].notes
            if production[0].notes:
                notes = production[0].notes
            else:
                notes = ""
            context = RequestContext(request, {
                'product': production[0],
                'notes': notes,
            })

        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            return HttpResponse(template.render(context))
            cursor.commit()
            cursor.close()


def producto(request,id):
    template = loader.get_template('conector/producto.html')
    context={}
    oerp_ctx = {'lang': 'es_ES'}
    from erp import POOL, DB, USER
    cursor = DB.cursor()

    production_obj = POOL.get('mrp.production')
    try:
        production = production_obj.browse(cursor, USER, [int(id)], context=oerp_ctx)
        users_list = Usuario.objects.filter()
        user_access = Usuario.objects.get(code = str(request.session[
            'codigo']))
        user_access.control_time(project=id)
        context = RequestContext(request, {
            'users_list': users_list,
            'product': production[0],
            'codigo': request.session['codigo'],

        })
    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");</script>')
        pass
    finally:
        return HttpResponse(template.render(context))
        cursor.commit()
        cursor.close()


def crear_producto(request):
    oerp_ctx = {'lang': 'es_ES'}
    if request.method == 'POST':
        pr_id = int(request.POST.get("pr"))
        w_id = int(request.POST.get("wr"))
        vals = {}
        from erp import POOL, DB, USER
        from openerp import netsvc
        wf_service = netsvc.LocalService("workflow")
        cursor = DB.cursor()
        qty = int(request.POST.get("qty"))

        codigo = int(request.session.get('codigo', False))
        mrp_obj = POOL.get('mrp.production')
        prod_obj = POOL.get('product.product')
        user_obj = POOL.get('res.users')
        mrp = 0
        try:
            user_ids = user_obj.search(cursor, USER, [('code', '=', codigo )], order="login ASC")
            users = user_obj.browse(cursor, USER, user_ids, context=oerp_ctx)
            product = prod_obj.browse(cursor, USER, pr_id)
            vals['date_planned'] = timezone.now()
            vals['product_id'] = pr_id
            vals['product_qty'] = qty
            vals['warehouse_id'] = w_id
            vals['product_uom'] = product.uom_id.id
            vals['user_id'] = users[0].id

            mrp = mrp_obj.create(cursor, USER, vals)
            production = mrp_obj.browse(cursor, USER, mrp)
            wf_service.trg_validate(USER, 'mrp.production', mrp, 'button_confirm', cursor)
            #user_access = Usuario.objects.get(code = codigo)
            #user_access.control_time(project=mrp)
        except Exception as e:
            cursor.rollback()
            cursor.close()
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/crear_productos/");</script>')
            return redirect('/producto/' + str(mrp))

        cursor.commit()
        cursor.close()

        return redirect('/producto/' + str(mrp))

    else:
        template = loader.get_template('conector/crear_producto.html')
        context={}
        from erp import POOL, DB, USER
        cursor = DB.cursor()
        product_obj = POOL.get('product.product')
        warehouse_obj = POOL.get('stock.warehouse')
        try:
            products_ids = product_obj.search(cursor, USER, [('analytic_acc_id', '!=', False),('bom_ids', '!=', False), ('bom_ids.bom_id','=',False)], order="name ASC")
            products = product_obj.browse(cursor, USER, products_ids, context=oerp_ctx)
            warehouse_ids = warehouse_obj.search(cursor, USER, [], order="name ASC")
            warehouses = warehouse_obj.browse(cursor, USER, warehouse_ids, context=oerp_ctx)
            users_list = Usuario.objects.filter()

            context = RequestContext(request, {
                'users_list': users_list,
                'products': products,
                'warehouses':warehouses,
                'codigo': request.session['codigo'],
            })
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/crear_productos/");</script>')
            pass
        finally:
            return HttpResponse(template.render(context))
            cursor.commit()
            cursor.close()


def procesar(request, id):
    context={}
    from erp import POOL, DB, USER
    mrp_obj = POOL.get('mrp.production')
    cursor = DB.cursor()
    oerp_ctx = {'lang': 'es_ES'}

    try:
        pr_id = int(id)
        #product = mrp_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
        mrp = mrp_obj.check_availability(cursor, USER, [pr_id], context=oerp_ctx)
        #mrp = mrp_obj.force_production(cursor, USER, [product[0].id])
        #mrp_obj.action_produce(cursor, USER, product[0].id, product[0].product_qty, "consume_produce")
    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");</script>')
        pass
    finally:
        cursor.commit()
        cursor.close()
        return HttpResponse('<script type="text/javascript">window.location.replace("/producto/'+id+'/");</script>')


def recalcular(request, id):

    context={}
    from erp import POOL, DB, USER
    context={}
    oerp_ctx = {'lang': 'es_ES'}
    mrp_obj = POOL.get('mrp.production')
    cursor = DB.cursor()
    change_obj = POOL.get('change.production.qty')
    bom_obj = POOL.get('mrp.bom')
    move_obj = POOL.get('stock.move')
    line_planned_obj = POOL.get('mrp.production.product.line')
    try:
        pr_id = int(id)
        mrp = mrp_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)[0]
        total = 0
        for final in mrp.move_created_ids:
            total = total + final.product_qty

        #Actualizacion de cantidades y recálculo de bom

        mrp_obj.write(cursor, USER, [mrp.id], {'product_qty': total})

        for move in mrp.move_lines:

            bom_point = mrp.bom_id
            bom_id = mrp.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cursor, USER, mrp.product_id.id, mrp.product_uom.id)

                if not bom_id:
                    raise osv.except_osv(_('Error!'), _("Cannot find bill of material for this product."))
                mrp_obj.write(cursor, USER, [mrp.id], {'bom_id': bom_id})
                bom_point = bom_obj.browse(cursor, USER, [bom_id])[0]

            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find bill of material for this product."))

            factor = mrp.product_qty * mrp.product_uom.factor / bom_point.product_uom.factor
            product_details, workcenter_details = \
                bom_obj._bom_explode(cursor, USER, bom_point, factor / bom_point.product_qty, [])
            product_move = dict((mv.product_id.id, mv.id) for mv in mrp.picking_id.move_lines)
            product_planned = dict((line_planned.product_id.id, line_planned.id) for line_planned in mrp.product_lines)
            for r in product_details:
                if r['product_id'] == move.product_id.id:
                    move_obj.write(cursor, USER, [move.id], {'product_qty': r['product_qty']})
                if r['product_id'] in product_move:
                    move_obj.write(cursor, USER, [product_move[r['product_id']]], {'product_qty': r['product_qty']})
                if r['product_id'] in product_planned:
                    line_planned_obj.write(cursor, USER, [product_planned[r['product_id']]], {'product_qty': r['product_qty']})
        # if mrp[0].move_prod_id:
        #     move_obj.write(cursor, USER, [mrp[0].move_prod_id.id], {'product_qty' : cantidad})
        # change_obj._update_product_to_produce(cursor, USER, mrp[0], cantidad, context=context)

    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");</script>')
        pass
    finally:
        cursor.commit()
        cursor.close()
        return HttpResponse('<script type="text/javascript">window.location.replace("/producto/'+id+'/");</script>')


def abrir(request, id):

    context={}
    from erp import POOL, DB, USER

    mrp_obj = POOL.get('mrp.production')
    cursor = DB.cursor()

    try:
        pr_id = int(id)
        mrp_obj.action_ready(cursor, USER, [pr_id], *args)
    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");</script>')
        pass
    finally:
        cursor.commit()
        cursor.close()
        return HttpResponse('<script type="text/javascript">window.location.replace("/producto/'+id+'/");</script>')

def finalizar(request, id):

    context={}
    oerp_ctx = {'lang': 'es_ES'}
    from erp import POOL, DB, USER
    user_obj = POOL.get('res.users')
    mrp_obj = POOL.get('mrp.production')
    time_obj = POOL.get('hr.analytic.timesheet')
    hr_obj = POOL.get('hr.employee')
    cursor = DB.cursor()

    try:
        pr_id = int(id)
        codigo = int(request.session.get('codigo', False))
        mrp = mrp_obj.browse(cursor, USER, pr_id)
        mrp_obj.action_produce(cursor, USER, mrp.id, mrp.product_qty, "consume_produce")
        mrp_obj.action_production_end(cursor, USER, [mrp.id,])
        user_access = Usuario.objects.filter(project = mrp.id, end__isnull = True)


        users_time = Usuario.objects.filter(project = mrp.id )

        for t in users_time:
            t.control_time()
            # user_ids = user_obj.search(cursor, USER, [('code', '=', t.code )], order="login ASC")
            # usere = user_obj.browse(cursor, USER, user_ids)
            #
            # hr_ids = hr_obj.search(cursor, USER, [('user_id', '=', usere[0].id )], order="login ASC")
            # hr_usere = hr_obj.browse(cursor, USER, hr_ids, context=oerp_ctx)
            #
            # vals = {}
            #
            # vals['production_id'] =  mrp.id
            # vals['journal_id'] =  hr_usere[0].journal_id.id
            # vals['product_uom_id'] = mrp.product_id.uom_id.id
            # vals['product_id'] = mrp.product_id.id
            # vals['general_account_id'] = False
            # vals['account_id'] = mrp.product_id.analytic_acc_id.id
            # vals['date'] = t.end
            # vals['unit_amount'] = timestamp(t.end) - timestamp(t.start)
            # vals['name'] = mrp.name
            # vals['user_id'] = usere[0].id
            # vals['amount'] = hr_usere[0].product_id.standard_price * vals['unit_amount']
            #
            # time_obj.create(cursor, USER, vals, context=oerp_ctx)

    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");</script>')
        pass
    finally:
        cursor.commit()
        cursor.close()
        return HttpResponse('<script type="text/javascript">window.location.replace("/");</script>')


def verstock(request, id):
    # Busco usuario,si exite,para el tiempo y crea nuevo tiempo de trabajo
    # Si no exite,creo una nuevo tiempo de trabajo
    # guardo en una session, el id del usuario para futuras busquedas

    template = loader.get_template('conector/verstock.html')
    context={}
    move_id = int(id)
    from erp import POOL, DB, USER
    lot_obj = POOL.get('stock.production.lot')
    prod_obj = POOL.get('product.product')
    move_obj = POOL.get('stock.move')
    cursor = DB.cursor()
    oerp_ctx = {'lang': 'es_ES'}
    move = move_obj.browse(cursor, USER, move_id, context=oerp_ctx)
    lot_ids = lot_obj.search(cursor, USER, [('product_id', '=', move.product_id.id),('stock_available', '>', 0.0)], order='use_date ASC')
    try:
        if request.method == 'POST':
            selected_lots = []
            for field in  request.POST:
                if 'foo' in field:
                    selected_lots.append(int(request.POST[field]))

            if selected_lots:
                move_obj.apply_lots_in_production(cursor, USER, [move.id], selected_lots)
            return HttpResponse('<script type="text/javascript">opener.location.reload();window.close()</script>')

        else:
            lots = lot_obj.browse(cursor, USER, lot_ids)
            lots_qty = sum([x.stock_available for x in lots])
            product = move.product_id
            qty_without_lot = product.qty_available - lots_qty
            if qty_without_lot > 0:
                lots.append({'name': 'Sin lote',
                             'product_id': product,
                             'stock_available': qty_without_lot,
                             'expiry_date': '',
                             'use_date': '',
                             'id': 0})

            context = RequestContext(request, {
                'lots': lots,

            })
            return HttpResponse(template.render(context))
    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
        pass
    finally:
        cursor.commit()
        cursor.close()


def eliminar(request, id):
    pr_id = int(id)
    oerp_ctx = {'lang': 'es_ES', 'call_unlink': True}
    if request.method == 'POST':

        from erp import POOL, DB, USER
        cursor = DB.cursor()
        prod_obj = POOL.get('stock.move')
        try:
            prod_obj.unlink(cursor, USER, [pr_id], context=oerp_ctx)
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()

            return HttpResponse('<script type="text/javascript">opener.location.reload();window.close();</script>')
    else:

        template = loader.get_template('conector/eliminar.html')
        context={}

        from erp import POOL, DB, USER
        product_obj = POOL.get('stock.move')
        cursor = DB.cursor()
        try:
            product = product_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            context = RequestContext(request, {
                'product': product[0],
            })
            return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')

            pass
        finally:
            cursor.commit()
            cursor.close()


def cambiar_cantidad(request, id):
    pr_id = int(id)
    oerp_ctx = {'lang': 'es_ES', 'call_unlink': True}
    if request.method == 'POST':

        from erp import POOL, DB, USER
        cursor = DB.cursor()
        prod_obj = POOL.get('stock.move')
        lot_obj = POOL.get('stock.production.lot')
        try:
            cantidad = float(request.POST.get("product_qty"))
            prod_obj.write(cursor, USER, [pr_id], {'product_qty':
                                                    cantidad}, oerp_ctx)
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()

            return HttpResponse('<script type="text/javascript">opener.location.reload();window.close();</script>')
    else:

        template = loader.get_template('conector/cambiar_cantidad.html')
        context={}

        from erp import POOL, DB, USER
        move_obj = POOL.get('stock.move')
        cursor = DB.cursor()
        try:
            move = move_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            context = RequestContext(request, {
                'move': move[0],
            })
            return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')

            pass
        finally:
            cursor.commit()
            cursor.close()

def validateDateEs(date):
    """
    Funcion para validar una fecha en formato:
        dd/mm/yyyy, dd/mm/yy, d/m/yy
    """
    for format in ['%d/%m/%Y', '%d/%m/%y']:
        try:
            result = time.strptime(date, format)
            return True
        except:
            pass
    return False

def cambiar_fecha(request, id):
    pr_id = int(id)
    oerp_ctx = {'lang': 'es_ES', 'call_unlink': True}
    if request.method == 'POST':

        from erp import POOL, DB, USER
        cursor = DB.cursor()
        prod_obj = POOL.get('stock.move')
        lot_obj = POOL.get('stock.production.lot')
        print_format_error = False
        try:
            date_str = request.POST.get("use_date")
            if not validateDateEs(date_str):
                print_format_error = True
            else:
                lot_obj.write(cursor, USER, [pr_id], {'use_date': date_str}, oerp_ctx)
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()
            if print_format_error:
                return HttpResponse('<script type="text/javascript">window.alert("ERROR: El formato de la fecha debe ser dd/mm/aaaa");opener.location.reload();window.close();</script>')
            return HttpResponse('<script type="text/javascript">opener.location.reload();window.close();</script>')
    else:

        template = loader.get_template('conector/cambiar_fecha.html')
        context={}

        from erp import POOL, DB, USER
        lot_obj = POOL.get('stock.production.lot')
        cursor = DB.cursor()
        try:
            prodlot = lot_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            context = RequestContext(request, {
                'prodlot': prodlot[0],
            })
            return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')

            pass
        finally:
            cursor.commit()
            cursor.close()



def reciclar(request, id):
    pr_id = int(id)
    oerp_ctx = {'lang': 'es_ES'}
    if request.method == 'POST':
        cantidad = float(request.POST.get("unidades"))
        from erp import POOL, DB, USER
        cursor = DB.cursor()
        prod_obj = POOL.get('stock.move')

        try:

            product = prod_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            prod_obj = prod_obj.action_scrap(cursor, USER, [product[0].id], cantidad, product[0].location_id.id, context=oerp_ctx)
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()

            return HttpResponse('<script type="text/javascript">opener.location.reload();window.close();</script>')
    else:

        template = loader.get_template('conector/reciclar.html')
        context={}

        from erp import POOL, DB, USER
        product_obj = POOL.get('stock.move')
        cursor = DB.cursor()
        try:
            product = product_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            context = RequestContext(request, {
                'product': product[0],
            })
            return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')

            pass
        finally:
            cursor.commit()
            cursor.close()

def etiquetas (request, id):
    template = loader.get_template('conector/etiquetas.html')
    context={}
    oerp_ctx = {'lang': 'es_ES'}
    pr_id = int(id)
    response = HttpResponse('<script type="text/javascript">window.close()</script>')
    if request.method == 'POST':
        from erp import POOL, DB, USER
        cursor = DB.cursor()
        move_obj = POOL.get('stock.move')
        lot_obj = POOL.get('stock.production.lot')
        try:

            updated=False
            new_lots = {}
            first_lang = True
            label_moves_obj = POOL.get('print.label.moves')
            data={'move_ids': []}
            for move_id, unidades in zip(request.POST.getlist("move_id"), request.POST.getlist("unidades_caja")):
                unidades = float(unidades)
                move_id = int(move_id)
                move = move_obj.browse(cursor, USER, move_id, oerp_ctx)
                vals = {
                    'product_id': move.product_id.id,
                    'qty': move.product_qty,
                    'lot_id': move.prodlot_id.id,
                    'language': move.prodlot_id.language.id,
                    'qty_box': unidades
                }
                label_id = label_moves_obj.create(cursor, USER, vals)
                data['move_ids'].append(label_id)
            import netsvc

            datas = {
                'ids': [pr_id,],
                'model': 'mrp.production',
                'form': data
            }
            service = netsvc.LocalService("report.mrp.production.label");
            (result, format) = service.create(cursor, USER, [pr_id], datas, {})

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="etiquetas.pdf"'
            response.write(result)

        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");</script>')
            response = HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()
            return response
            # return HttpResponse('<script type="text/javascript">window.close()</script>')
    else:

        template = loader.get_template('conector/etiquetas.html')
        context={}

        from erp import POOL, DB, USER
        product_obj = POOL.get('mrp.production')
        cursor = DB.cursor()
        try:
            product = product_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            context = RequestContext(request, {
                'product': product[0],
            })
            return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')

            pass
        finally:
            cursor.commit()
            cursor.close()



def dividir(request, id):
    # Una vez recibido el post, tengo que llamar a alguna funcion que me pase omar.

    template = loader.get_template('conector/dividir.html')
    context={}
    oerp_ctx = {'lang': 'es_ES'}
    pr_id = int(id)
    if request.method == 'POST':
        from erp import POOL, DB, USER
        cursor = DB.cursor()
        move_obj = POOL.get('stock.move')
        lot_obj = POOL.get('stock.production.lot')

        try:

            updated=False
            move = move_obj.browse(cursor, USER, pr_id)
            new_lots = {}
            first_lang = True
            for language, qty in zip(request.POST.getlist("language"), request.POST.getlist("unidades")):
                qty = float(qty)
                language = int(language)

                #copy_vals = {'language': language, 'product_qty': qty}

                if move.prodlot_id:
                    if first_lang:
                        lot_obj.write(cursor, USER, move.prodlot_id.id, {'language': language})
                        move_obj.write(cursor, USER, move.id, {'product_qty': qty})

                    else:
                        new_lot = lot_obj.copy(cursor, USER, move.prodlot_id.id, {'language': language})
                        new_move = move_obj.copy(cursor, USER, move.id, {'product_qty': qty, 'prodlot_id': new_lot})
                    first_lang = False


            #if not updated and request.POST.get("product", False):
            #move_obj.unlink(cursor, USER, [move.id])

        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()

            return HttpResponse('<script type="text/javascript">opener.location.reload();window.close()</script>')
    else:

        from erp import POOL, DB, USER
        product_obj = POOL.get('product.product')
        lang_obj = POOL.get('res.lang')
        move_obj = POOL.get('stock.move')
        cursor = DB.cursor()
        try:
            move = move_obj.browse(cursor, USER, [pr_id])
            products_ids = product_obj.search(cursor, USER, [('analytic_acc_id', '!=', False),('bom_ids', '!=', False), ('bom_ids.bom_id','=',False),('type', '=', 'product')], order="name ASC", context=oerp_ctx)
            products = product_obj.browse(cursor, USER, products_ids, context=oerp_ctx)
            lang_ids = lang_obj.search(cursor, USER, [], context=oerp_ctx)
            langs = lang_obj.browse(cursor, USER, lang_ids, context=oerp_ctx)
            context = RequestContext(request, {
                'move': move[0],
                'products': products,
                'langs': langs,
            })
            return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()

def tareas(request):
    template = loader.get_template('conector/tareas.html')
    context={}
    oerp_ctx = {'lang': 'es_ES'}
    from erp import POOL, DB, USER
    cursor = DB.cursor()
    tarea_obj = POOL.get('hr.task')
    time_obj = POOL.get('hr.analytic.timesheet')

    try:
        tarea_ids = tarea_obj.search(cursor, USER, [('state', 'not in', ['close','cancel'])], order="name ASC")

        tareas = tarea_obj.browse(cursor, USER, tarea_ids, context=oerp_ctx)

        users_list = Usuario.objects.filter()
        context = RequestContext(request, {
            'users_list': users_list,
            'tareas_list': tareas,
            'codigo': request.session['codigo'],
        })
    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/tareas/");</script>')
        pass
    finally:
        return HttpResponse(template.render(context))
        cursor.commit()
        cursor.close()

def tarea(request,id=None):
    template = loader.get_template('conector/tarea.html')
    context={}
    oerp_ctx = {'lang': 'es_ES'}
    from erp import POOL, DB, USER
    cursor = DB.cursor()
    tar = False
    if request.method == 'POST':

        pr_id = int(request.POST.get("pr"))
        description = request.POST.get("description")
        note = request.POST.get("note")
        estado = request.POST.get("state", False)
        task_id = request.POST.get("taskid", False)
        kg_mov = request.POST.get("kg_mov", False)
        vals = {}

        codigo = int(request.session.get('codigo', False))
        tarea_obj = POOL.get('hr.task')
        user_obj = POOL.get('res.users')
        time_obj = POOL.get('hr.analytic.timesheet')
        hr_obj = POOL.get('hr.employee')

        try:
            if request.POST.get('accion') == "Guardar":
                tarea_id = tarea_obj.browse(cursor, USER, int(task_id), context=oerp_ctx)
                vals['name'] = description
                vals['product_id'] = pr_id
                vals['note'] = note
                tarea_obj.write(cursor, USER, [tarea_id.id], vals, context=oerp_ctx)
            else:

                #Si no existe la tarea, se crea.
                if not estado:
                    vals['name'] = description
                    vals['product_id'] = pr_id
                    vals['note'] = note
                    tareas=tarea_obj.create(cursor, USER, vals)
                    task_id = int(tareas)
                    user_access = Usuario.objects.get(code = codigo)
                    user_access.control_time(task=task_id)
                    #
                    # user_access.task = tareas
                    # user_access.save()


                else:
                #Si existe, se finaliza o se abre, dependiendo del estado.
                    tareas_ids = tarea_obj.browse(cursor, USER, int(task_id), context=oerp_ctx)

                    user_access = Usuario.objects.get(code=codigo)
                    if tareas_ids.state == "draft":
                        tarea_obj.set_open(cursor, USER, [tareas_ids.id])
                        #user_access.task = task_id
                        user_access.control_time(task=task_id)

                    else:
                        tar = True
                        #
                        # user_access.task = task_id
                        # user_access.end = timezone.now()
                        # user_access.save()

                        # user_access = Usuario.objects.filter(task = id)
                        # for u in user_access:
                        #     u.register_time()
                        #     u.save()

                        # FINALIZA Y REGISTRA TODOS LOS USUARIOS DE LA TAREA
                        users_time = Usuario.objects.filter(task = id )

                        for t in users_time:
                            t.control_time()
                            # user_ids = user_obj.search(cursor, USER, [('code', '=', t.code )], order="login ASC")
                            # usere = user_obj.browse(cursor, USER, user_ids)
                            #
                            # hr_ids = hr_obj.search(cursor, USER, [('user_id', '=', usere[0].id )], order="login ASC")
                            # hr_usere = hr_obj.browse(cursor, USER, hr_ids, context=oerp_ctx)
                            #
                            # vals = {}
                            # vals['hr_task_id'] = tareas_ids.id
                            # vals['journal_id'] =  hr_usere[0].journal_id.id
                            # vals['product_uom_id'] = tareas_ids.product_id.uom_id.id
                            # vals['product_id'] = tareas_ids.product_id.id
                            # vals['general_account_id'] = False
                            # vals['account_id'] = tareas_ids.product_id.analytic_acc_id.id
                            # vals['date'] = t.end
                            # vals['unit_amount'] = timestamp(t.end) - timestamp(t.start)
                            # vals['name'] = tareas_ids.name
                            # vals['user_id'] = usere[0].id
                            # vals['amount'] = hr_usere[0].product_id.standard_price * vals['unit_amount']
                            # time_obj.create(cursor, USER, vals, context=oerp_ctx)

                        vals['name'] = description
                        vals['product_id'] = pr_id
                        vals['note'] = note
                        vals['kg_moved'] = kg_mov
                        tarea_obj.write(cursor, USER, [tareas_ids.id], vals, context=oerp_ctx)
                        tarea_obj.set_close(cursor, USER, [tareas_ids.id])


        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/tarea/'+id+'/");</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()

            #return home(request)
        if tar == False:
            return HttpResponse('<script type="text/javascript">window.location.replace("/tarea/'+str(task_id)+'/");</script>')
        else:
            return HttpResponse('<script type="text/javascript">window.location.replace("/");</script>')
    else:


        tarea_obj = POOL.get('hr.task')
        trabajo_obj = POOL.get('product.product')
        try:
            if id != None:
                tarea = tarea_obj.browse(cursor, USER, [int(id)])
            trabajos_ids = trabajo_obj.search(cursor, USER, [('type', '=', 'service'),('analytic_acc_id', '!=', False)], order="name ASC")
            trabajos = trabajo_obj.browse(cursor, USER, trabajos_ids, context=oerp_ctx)
            users_list = Usuario.objects.filter()
            user_access = Usuario.objects.get(code = request.session['codigo'])
            # if (user_access.project or user_access.task):
            #     if user_access.project or (int(user_access.task) != int(id)):
            #         user_access.register_time()
            #         user_access.init_time()
            # else:
            #     user_access.task = id
            #     user_access.save()
            #     user_access.init_time
            if id != None:
                if tarea[0].state != 'close':
                    user_access.control_time(task=id)
            if id != None:
                context = RequestContext(request, {
                    'users_list': users_list,
                    'tarea': tarea[0],
                    'trabajos':trabajos,
                    'codigo': request.session['codigo'],
                })
            else:
                context = RequestContext(request, {
                    'users_list': users_list,
                    'tarea': False,
                    'trabajos':trabajos,
                    'codigo': request.session['codigo'],
                })
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/tarea/'+id+'/");</script>')
            pass
        finally:
            return HttpResponse(template.render(context))
            cursor.commit()
            cursor.close()


def salir(request):
    # Busco usuario,si exite,para el tiempo y borro sesion

    template = loader.get_template('conector/index.html')
    context={}
    codigo = int(request.session.get('codigo', False))
    from erp import POOL, DB, USER
    user_obj = POOL.get('res.users')
    cursor = DB.cursor()
    try:
        user_ids = user_obj.search(cursor, USER, [('code', '=', codigo )], order="login ASC")
        users = user_obj.browse(cursor, USER, user_ids)
        if users:
            user_access= Usuario.objects.get(code = codigo)
            #user_access.end = timezone.now()

            user_access.register_time()
            user_access.project = None
            user_access.task = None
            user_access.pr_name = None
            user_access.save()
            user_access.delete()

            del request.session['codigo']
        else:
            context = RequestContext(request, {
                'nouser': False,
            })
            return HttpResponse(template.render(context))
    except Exception as e:
        return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/");</script>')
        pass
    finally:
        cursor.commit()
        cursor.close()
    return HttpResponse('<script type="text/javascript">window.location.replace("/");</script>')

def actualizar_cantidad(request, id):

    template = loader.get_template('conector/actualizar_cantidad.html')
    context={}
    oerp_ctx = {'lang': 'es_ES'}
    pr_id = int(id)
    if request.method == 'POST':
        from erp import POOL, DB, USER
        cantidad = float(request.POST.get("unidades"))
        cursor = DB.cursor()
        mrp_obj = POOL.get('mrp.production')
        change_obj = POOL.get('change.production.qty')
        bom_obj = POOL.get('mrp.bom')
        move_obj = POOL.get('stock.move')

        try:
            mrp = mrp_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            mrp_obj.write(cursor, USER, [mrp[0].id], {'product_qty': cantidad})
            mrp_obj.action_compute(cursor, USER, [mrp[0].id])
            for move in mrp[0].move_lines:

                bom_point = mrp[0].bom_id
                bom_id = mrp[0].bom_id.id
                if not bom_point:
                    bom_id = bom_obj._bom_find(cursor, USER, mrp[0].product_id.id, mrp[0].product_uom.id)

                    if not bom_id:
                        raise osv.except_osv(_('Error!'), _("Cannot find bill of material for this product."))
                    mrp_obj.write(cursor, USER, [mrp[0].id], {'bom_id': bom_id})
                    bom_point = bom_obj.browse(cursor, USER, [bom_id])[0]

                if not bom_id:
                    raise osv.except_osv(_('Error!'), _("Cannot find bill of material for this product."))

                factor = mrp[0].product_qty * mrp[0].product_uom.factor / bom_point.product_uom.factor
                product_details, workcenter_details = \
                    bom_obj._bom_explode(cursor, USER, bom_point, factor / bom_point.product_qty, [])
                product_move = dict((mv.product_id.id, mv.id) for mv in mrp[0].picking_id.move_lines)
                for r in product_details:
                    if r['product_id'] == move.product_id.id:
                        move_obj.write(cursor, USER, [move.id], {'product_qty': r['product_qty']})
                    if r['product_id'] in product_move:
                        move_obj.write(cursor, USER, [product_move[r['product_id']]], {'product_qty': r['product_qty']})
            if mrp[0].move_prod_id:
                move_obj.write(cursor, USER, [mrp[0].move_prod_id.id], {'product_qty' : cantidad})
            change_obj._update_product_to_produce(cursor, USER, mrp[0], cantidad, context=context)

        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()

        return HttpResponse('<script type="text/javascript">opener.location.reload();window.close()</script>')
    else:

        from erp import POOL, DB, USER
        product_obj = POOL.get('mrp.production')
        cursor = DB.cursor()
        try:
            product = product_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            context = RequestContext(request, {
                'product': product[0],
            })
            return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')

            pass
        finally:
            cursor.commit()
            cursor.close()

def desechar(request, id):
    pr_id = int(id)
    oerp_ctx = {'lang': 'es_ES'}
    if request.method == 'POST':
        cantidad = float(request.POST.get("unidades"))
        from erp import POOL, DB, USER
        cursor = DB.cursor()
        prod_obj = POOL.get('stock.move')
        location_obj = POOL.get('stock.location')
        try:

            product = prod_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            scraped_location = location_obj.search(cursor, USER, [('scrap_location','=',True)])
            prod_obj = prod_obj.action_scrap(cursor, USER, [product[0].id], cantidad, scraped_location[0], context=oerp_ctx)
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')
            pass
        finally:
            cursor.commit()
            cursor.close()

            return HttpResponse('<script type="text/javascript">opener.location.reload();window.close();</script>')
    else:

        template = loader.get_template('conector/desechar.html')
        context={}

        from erp import POOL, DB, USER
        product_obj = POOL.get('stock.move')
        cursor = DB.cursor()
        try:
            product = product_obj.browse(cursor, USER, [pr_id], context=oerp_ctx)
            context = RequestContext(request, {
                'product': product[0],
            })
            return HttpResponse(template.render(context))
        except Exception as e:
            return HttpResponse('<script type="text/javascript">window.alert("ERROR: '+unicode(e)+'");window.location.replace("/producto/'+id+'/");window.close();</script>')

            pass
        finally:
            cursor.commit()
            cursor.close()
