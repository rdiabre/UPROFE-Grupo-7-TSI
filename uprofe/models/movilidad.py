# -*- coding: utf-8 -*-

import re
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class Movilidad(models.Model):
    """Movilidad de un estudiante a una plaza Erasmus.

    Validaciones (5+):
      1. La fecha de fin no es anterior a la de inicio
      2. La estancia dura al menos 60 días (mínimo Erasmus de 2 meses)
      3. La estancia no supera los 365 días
      4. El número sigue el formato MOV-AAAA-NNN (+ SQL único)
      5. La estancia no dura más que la plaza
      6. No se superan las vacantes de la plaza
    Reglas de negocio ORM (5+):
      1. Duración en días y meses (compute almacenado)
      2. Learning agreement vigente = el de versión más alta (compute con sorted)
      3. onchange: propone la fecha de fin según la duración de la plaza (relativedelta)
      4. create() numera la movilidad (MOV-AAAA-NNN) y le pone el estado inicial
      5. write() impide cambiar de estado una movilidad que ya está en un estado final
      6. unlink() impide borrar una movilidad con learning agreements
    """
    _name = 'uprofe.movilidad'
    _description = 'Movilidad'
    _rec_name = 'sNum_movilidad'
    _order = 'dFecha_inicio desc, sNum_movilidad'

    sNum_movilidad = fields.Char(string="Nº de movilidad", size=30, required=True, default='Nuevo', copy=False)
    dFecha_inicio = fields.Date(string="Fecha de inicio", required=True)
    dFecha_fin = fields.Date(string="Fecha de fin", required=True)
    sObservaciones = fields.Text(string="Observaciones")

    estado_id = fields.Many2one(
       'uprofe.estado_movilidad',
       string="Estado",
       required=True,
       ondelete='restrict',
       default=lambda self: self.env['uprofe.estado_movilidad']._estado_inicial(),
    )

    plaza_erasmus_id = fields.Many2one('uprofe.plaza_erasmus', string="Plaza Erasmus", ondelete='restrict')
    universidad_id = fields.Many2one(related='plaza_erasmus_id.universidad_id', string="Universidad", store=True)
    pais_id = fields.Many2one(related='plaza_erasmus_id.pais_id', string="País", store=True)

    # Descomentar cuando exista Solicitud (modelo de otro compañero).
    # El UNIQUE de abajo refleja el (0,1) de "origina": una solicitud origina como mucho una movilidad.
    # solicitud_id = fields.Many2one(
    #     'uprofe.solicitud',
    #     string="Solicitud de origen",
    #     required=True,
    #     ondelete='restrict',
    # )

    learning_agreement_ids = fields.One2many(
        'uprofe.learning_agreement', 'movilidad_id', string="Learning agreements")

    iDuracion_dias = fields.Integer(string="Duración (días)", compute='_compute_duracion', store=True)
    fDuracion_meses = fields.Float(string="Duración (meses)", compute='_compute_duracion', store=True, digits=(4, 1))
    la_vigente_id = fields.Many2one('uprofe.learning_agreement', string="Learning agreement vigente",
                                    compute='_compute_la_vigente')

    _sql_constraints = [
        ('num_movilidad_unico', 'UNIQUE("sNum_movilidad")',
         'Ya existe una movilidad con ese número.'),
        # ('solicitud_unica', 'UNIQUE(solicitud_id)',
        #  'Esa solicitud ya ha originado una movilidad.'),
    ]

    # ------------------------------------------------------------------ validaciones
    @api.constrains('dFecha_inicio', 'dFecha_fin')
    def _check_fechas(self):
        for record in self:
            if record.dFecha_inicio and record.dFecha_fin and record.dFecha_fin < record.dFecha_inicio:
                raise ValidationError("La fecha de fin no puede ser anterior a la de inicio.")

    @api.constrains('dFecha_inicio', 'dFecha_fin')
    def _check_duracion_minima(self):
        for record in self:
            if record.iDuracion_dias and record.iDuracion_dias < 60:
                raise ValidationError("Una movilidad Erasmus dura como mínimo 60 días (2 meses).")

    @api.constrains('dFecha_inicio', 'dFecha_fin')
    def _check_duracion_maxima(self):
        for record in self:
            if record.iDuracion_dias > 365:
                raise ValidationError("Una movilidad no puede durar más de un año (365 días).")

    @api.constrains('sNum_movilidad')
    def _check_numero(self):
        for record in self:
            if not re.match(r'^MOV-\d{4}-\d{3}$', record.sNum_movilidad or ''):
                raise ValidationError("El número de movilidad sigue el formato MOV-AAAA-NNN (por ejemplo MOV-2026-001).")

    @api.constrains('plaza_erasmus_id', 'dFecha_inicio', 'dFecha_fin')
    def _check_duracion_plaza(self):
        for record in self.filtered('plaza_erasmus_id'):
            limite = record.dFecha_inicio + relativedelta(months=record.plaza_erasmus_id.iDuracion_meses)
            if record.dFecha_fin > limite:
                raise ValidationError("La estancia dura más que la plaza %s (%d meses)."
                                      % (record.plaza_erasmus_id.cod_plaza, record.plaza_erasmus_id.iDuracion_meses))

    @api.constrains('plaza_erasmus_id', 'estado_id')
    def _check_vacantes(self):
        for record in self.filtered('plaza_erasmus_id'):
            if record.plaza_erasmus_id.iVacantes_libres < 0:
                raise ValidationError("La plaza %s no tiene vacantes libres (%d)."
                                      % (record.plaza_erasmus_id.cod_plaza, record.plaza_erasmus_id.iNum_vacantes))

    # ------------------------------------------------------------------ reglas de negocio
    @api.depends('dFecha_inicio', 'dFecha_fin')
    def _compute_duracion(self):
        for record in self:
            if record.dFecha_inicio and record.dFecha_fin:
                record.iDuracion_dias = (record.dFecha_fin - record.dFecha_inicio).days + 1
                record.fDuracion_meses = round(record.iDuracion_dias / 30.44, 1)
            else:
                record.iDuracion_dias = 0
                record.fDuracion_meses = 0.0

    @api.depends('learning_agreement_ids.iVersion')
    def _compute_la_vigente(self):
        for record in self:
            record.la_vigente_id = record.learning_agreement_ids.sorted('iVersion', reverse=True)[:1]

    @api.onchange('plaza_erasmus_id', 'dFecha_inicio')
    def _onchange_proponer_fin(self):
        if self.plaza_erasmus_id and self.dFecha_inicio:
            self.dFecha_fin = self.dFecha_inicio + relativedelta(
                months=self.plaza_erasmus_id.iDuracion_meses, days=-1)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sNum_movilidad') or vals['sNum_movilidad'] == 'Nuevo':
                anio = fields.Date.to_date(vals.get('dFecha_inicio') or fields.Date.context_today(self)).year
                prefijo = 'MOV-%d-' % anio
                numero = self.search_count([('sNum_movilidad', '=like', prefijo + '%')]) + 1
                vals['sNum_movilidad'] = '%s%03d' % (prefijo, numero)
            if not vals.get('estado_id'):
                vals['estado_id'] = self.env['uprofe.estado_movilidad']._estado_inicial().id
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('estado_id'):
            cerradas = self.filtered(lambda m: m.estado_id.bFinal and m.estado_id.id != vals['estado_id'])
            if cerradas:
                raise UserError("%s ya está en un estado final y no puede cambiar de estado."
                                % ', '.join(cerradas.mapped('sNum_movilidad')))
        return super().write(vals)

    def unlink(self):
        con_la = self.filtered('learning_agreement_ids')
        if con_la:
            raise UserError("No se puede borrar %s porque tiene learning agreements."
                            % ', '.join(con_la.mapped('sNum_movilidad')))
        return super().unlink()
