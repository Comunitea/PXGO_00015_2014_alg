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

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import datetime,time
from django.utils import timezone
from datetime import datetime

from erp import POOL, DB, USER

class Usuario(models.Model):
    code = models.CharField(_(u'Codigo'), max_length = 200)
    name = models.CharField(_(u'Usuario'), max_length = 200)
    project = models.CharField(_(u"Proyecto"), max_length = 200, blank=True, null=True)
    pr_name = models.CharField(_(u"Pr Nombre"), max_length = 200, blank=True,
                         null=True)
    task = models.CharField(_(u"Tarea"), max_length = 200, blank=True, null=True)
    start = models.DateTimeField(auto_now_add=True, editable=False)
    end = models.DateTimeField(_(u"Fin"), blank=True, null=True)
    
    def __unicode__(self):
        return self.code

    def timestamp(self, fecha):
        return time.mktime(fecha.timetuple())/3600

    def control_time (self, project=None, task=None):

        cursor = DB.cursor()
        production_obj = POOL.get('mrp.production')
        tarea_obj = POOL.get('hr.task')
        oerp_ctx = {'lang': 'es_ES'}

        if not task and not project:
            self.register_time()
            self.project = None
            self.task = None
            self.pr_name = None
            self.save()
            self.delete()


        if task: #REGISTRO EN TAREA
            if self.project or self.task:   # EL USUARIO YA ESTÁ REGISTRANDO
                if self.project or (int(self.task) != int(task)):  #SI ES UNA
                # TAREA DISTINTA A EN LO QUE ESTÁ
                    self.register_time()   #Registra el tiempo en la que estaba
                    self.init_time()        #REinicia contador
                    self.task = task          #Asigna nueva tarea
                    tarea = tarea_obj.browse(cursor, USER,
                                         [int(task)],
                                         context=oerp_ctx)
                    self.pr_name = "[T]" + tarea[0].name
                    self.save()
            else: # El usuario no estaba registrando
                self.init_time()        #REinicia contador
                self.task = task          #Asigna nueva tarea
                tarea = tarea_obj.browse(cursor, USER,
                                         [int(task)],
                                         context=oerp_ctx)
                self.pr_name = "[T]- REG --"
                self.save()
        if project:
            if self.project or self.task:   # EL USUARIO YA ESTÁ REGISTRANDO
                if self.task or (int(self.project) != int(project)):  #SI ES
                #  UNA
                # PRODUCCIÓN DISTINTA A EN LO QUE ESTÁ
                    self.register_time()   #Registra el tiempo en la que estaba
                    self.init_time()        #REinicia contador
                    self.project = project          #Asigna nueva produccion
                    production = production_obj.browse(cursor, USER,
                                                       [int(project)],
                                                       context=oerp_ctx)
                    self.pr_name = "[P]" + production[0].name
                    self.save()
            else: # El usuario no estaba registrando
                self.init_time()        #REinicia contador
                self.project = project          #Asigna nueva tarea
                production = production_obj.browse(cursor, USER,
                                                       [int(project)],
                                                       context=oerp_ctx)
                self.pr_name = "[P]" + production[0].name
                self.save()

    def init_time(self):
        self.start = timezone.now()
        self.save()

    def register_time(self):
        context={}
        oerp_ctx = {'lang': 'es_ES'}
        from erp import POOL, DB, USER
        user_obj = POOL.get('res.users')
        mrp_obj = POOL.get('mrp.production')
        time_obj = POOL.get('hr.analytic.timesheet')
        hr_obj = POOL.get('hr.employee')
        cursor = DB.cursor()

        user_ids = user_obj.search(cursor, USER, [('code', '=', self.code
                                                     )], order="login ASC")
        usere = user_obj.browse(cursor, USER, user_ids)

        hr_ids = hr_obj.search(cursor, USER, [('user_id', '=', usere[0].id )], order="login ASC")
        hr_usere = hr_obj.browse(cursor, USER, hr_ids, context=oerp_ctx)

        if self.project:
            vals = {}
            mrp = mrp_obj.browse(cursor, USER, int(self.project))
            vals['production_id'] = mrp.id
            vals['journal_id'] = hr_usere[0].journal_id.id
            vals['product_uom_id'] = mrp.product_id.uom_id.id
            vals['product_id'] = mrp.product_id.id
            vals['general_account_id'] = False
            vals['account_id'] = mrp.product_id.analytic_acc_id.id
            vals['init_date'] = self.start
            vals['date'] = timezone.now()
            v_tiempo = self.timestamp(vals['date']) - self.timestamp(self.start)
            vals['unit_amount'] = v_tiempo
            vals['name'] = mrp.name
            vals['user_id'] = usere[0].id
            vals['amount'] = hr_usere[0].product_id.standard_price * vals['unit_amount']

            time_obj.create(cursor, USER, vals, context=oerp_ctx)
            cursor.commit()
        if self.task:
            tarea_obj = POOL.get('hr.task')
            tareas_ids = tarea_obj.browse(cursor, USER, int(self.task), context=oerp_ctx)
            vals = {}
            vals['hr_task_id'] = tareas_ids.id
            vals['journal_id'] =  hr_usere[0].journal_id.id
            vals['product_uom_id'] = tareas_ids.product_id.uom_id.id
            vals['product_id'] = tareas_ids.product_id.id
            vals['general_account_id'] = False
            vals['account_id'] = tareas_ids.product_id.analytic_acc_id.id
            vals['init_date'] = self.start
            vals['date'] = timezone.now()
            v_tiempo = self.timestamp(vals['date']) - self.timestamp(self.start)
            vals['unit_amount'] = v_tiempo
            vals['name'] = tareas_ids.name
            vals['user_id'] = usere[0].id
            vals['amount'] = hr_usere[0].product_id.standard_price * vals['unit_amount']
            time_obj.create(cursor, USER, vals, context=oerp_ctx)
            cursor.commit()

        cursor.close()
        self.project = None
        self.task = None
        self.pr_name= None
        self.save()

    class Meta():
        verbose_name= "usuario"
        verbose_name_plural = "usuarios"
