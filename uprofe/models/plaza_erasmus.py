# -*- coding: utf-8 -*-

import re
import unicodedata
from odoo import models, fields, api
from odoo.exceptions import ValidationError

NIVELES_IDIOMA = [('a1', 'A1'), ('a2', 'A2'), ('b1', 'B1'), ('b2', 'B2'), ('c1', 'C1'), ('c2', 'C2')]


class PlazaErasmus(models.Model):
    """Plaza Erasmus ofertada en una universidad de destino.

    Validaciones (5+):
      1. La duración es de al menos 1 mes
      2. La duración no supera los 12 meses de una movilidad Erasmus
      3. Hay al menos una vacante
      4. La ayuda mensual no puede ser negativa
      5. El idioma requerido lo imparte la universidad (Many2many idioma_ids)
      6. El código solo admite mayúsculas, números y guiones (+ SQL único)
    Reglas de negocio ORM (5+):
      1. Ayuda total = meses x ayuda mensual (compute)
      2. Vacantes libres = vacantes - movilidades que la ocupan (compute con filtered)
      3. create() genera el código automáticamente (PLZ-CIUDAD-NN) con search_count
      4. write() pasa el código a mayúsculas
      5. onchange de la universidad: propone un idioma que esa universidad imparte
      6. onchange de la duración: avisa si supera 12 meses
      7. Nombre a mostrar «código · universidad» (_compute_display_name)
    """
    _name = 'uprofe.plaza_erasmus'
    _description = 'Plaza Erasmus'
    _rec_name = 'cod_plaza'
    _order = 'cod_plaza'

    cod_plaza = fields.Char(string="Código de la plaza", size=30, required=True, default='Nuevo', copy=False)
    iDuracion_meses = fields.Integer(string="Duración (meses)", required=True, default=5)
    iNum_vacantes = fields.Integer(string="Nº de vacantes", default=1)
    sNivel_idioma = fields.Selection(NIVELES_IDIOMA, string="Nivel de idioma exigido", default='b1')
    fAyuda_mensual = fields.Float(string="Ayuda mensual (€)", digits=(8, 2))

    universidad_id = fields.Many2one(
       'uprofe.universidad_destino',
       string="Universidad de destino",
       required=True,
       ondelete='restrict',
    )
    pais_id = fields.Many2one(related='universidad_id.pais_id', string="País", store=True)

    nivel_estudios_id = fields.Many2one(
       'uprofe.nivel_estudios',
       string="Nivel de estudios",
       required=True,
       ondelete='restrict',
    )

    idioma_id = fields.Many2one(
       'uprofe.idioma',
       string="Idioma requerido",
       required=True,
       ondelete='restrict',
    )

    movilidad_ids = fields.One2many('uprofe.movilidad', 'plaza_erasmus_id', string="Movilidades")

    fAyuda_total = fields.Float(string="Ayuda total (€)", compute='_compute_ayuda_total', store=True, digits=(8, 2))
    iVacantes_libres = fields.Integer(string="Vacantes libres", compute='_compute_vacantes_libres')

    convocatoria_id = fields.Many2one(
        'uprofe.convocatoria',
        string="Convocatoria",
        required=True,
        ondelete='restrict',
    )

    _sql_constraints = [
        ('cod_plaza_unico', 'UNIQUE(cod_plaza)',
         'Ya existe una plaza con ese código.'),
    ]

    # ------------------------------------------------------------------ validaciones
    @api.constrains('iDuracion_meses')
    def _check_duracion_meses(self):
        for record in self:
            if record.iDuracion_meses <= 0:
                raise ValidationError("La duración debe ser de al menos 1 mes.")

    @api.constrains('iDuracion_meses')
    def _check_duracion_maxima(self):
        for record in self:
            if record.iDuracion_meses > 12:
                raise ValidationError("Una plaza Erasmus no puede durar más de 12 meses.")

    @api.constrains('iNum_vacantes')
    def _check_vacantes(self):
        for record in self:
            if record.iNum_vacantes < 1:
                raise ValidationError("La plaza debe tener al menos una vacante.")

    @api.constrains('fAyuda_mensual')
    def _check_ayuda(self):
        for record in self:
            if record.fAyuda_mensual < 0:
                raise ValidationError("La ayuda mensual no puede ser negativa.")

    @api.constrains('idioma_id', 'universidad_id')
    def _check_idioma_universidad(self):
        for record in self:
            if record.idioma_id not in record.universidad_id.idioma_ids:
                raise ValidationError("%s no imparte docencia en %s."
                                      % (record.universidad_id.sName, record.idioma_id.sName))

    @api.constrains('cod_plaza')
    def _check_codigo(self):
        for record in self:
            if not re.match(r'^[A-Z0-9]+(-[A-Z0-9]+)*$', record.cod_plaza or ''):
                raise ValidationError("El código de la plaza solo admite mayúsculas, números y guiones "
                                      "(por ejemplo PLZ-ROMA-01).")

    # ------------------------------------------------------------------ reglas de negocio
    @api.depends('iDuracion_meses', 'fAyuda_mensual')
    def _compute_ayuda_total(self):
        for record in self:
            record.fAyuda_total = record.iDuracion_meses * record.fAyuda_mensual

    @api.depends('iNum_vacantes', 'movilidad_ids.estado_id')
    def _compute_vacantes_libres(self):
        for record in self:
            ocupadas = record.movilidad_ids.filtered(lambda m: m.estado_id.sName not in ('cancelada', 'rechazada'))
            record.iVacantes_libres = record.iNum_vacantes - len(ocupadas)

    @api.model
    def _generar_codigo(self, universidad_id):
        ciudad = self.env['uprofe.universidad_destino'].browse(universidad_id).ciudad_id.sName or 'PLAZA'
        ciudad = unicodedata.normalize('NFKD', ciudad)
        ciudad = re.sub(r'[^A-Z0-9]', '', ''.join(c for c in ciudad if not unicodedata.combining(c)).upper())
        prefijo = 'PLZ-%s-' % ciudad
        numero = self.search_count([('cod_plaza', '=like', prefijo + '%')]) + 1
        while self.search_count([('cod_plaza', '=', '%s%02d' % (prefijo, numero))]):
            numero += 1
        return '%s%02d' % (prefijo, numero)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('cod_plaza') or vals['cod_plaza'] == 'Nuevo':
                vals['cod_plaza'] = self._generar_codigo(vals.get('universidad_id'))
            else:
                vals['cod_plaza'] = vals['cod_plaza'].strip().upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('cod_plaza'):
            vals['cod_plaza'] = vals['cod_plaza'].strip().upper()
        return super().write(vals)

    @api.onchange('universidad_id')
    def _onchange_universidad(self):
        idiomas = self.universidad_id.idioma_ids
        if idiomas and self.idioma_id not in idiomas:
            self.idioma_id = idiomas[:1]

    @api.onchange('iDuracion_meses')
    def _onchange_duracion(self):
        if self.iDuracion_meses > 12:
            return {'warning': {'title': "Duración excesiva",
                                'message': "Una movilidad Erasmus dura como máximo 12 meses."}}

    @api.depends('cod_plaza', 'universidad_id.sName')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s · %s" % (record.cod_plaza or '', record.universidad_id.sName or '') \
                if record.universidad_id else (record.cod_plaza or '')
