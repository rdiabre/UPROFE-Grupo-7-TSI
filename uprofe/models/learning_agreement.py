# -*- coding: utf-8 -*-
# Autor: Isabel Cherino

import re
from odoo import models, fields, api, Command
from odoo.exceptions import ValidationError

ESTADOS_FIRMADOS = ('firmado_estudiante', 'firmado_origen', 'firmado_destino', 'aprobado')
MAX_CREDITOS = 60


class LearningAgreement(models.Model):
    """Learning agreement (acuerdo de estudios) de una movilidad.

    Validaciones (5+):
      1. La versión es 1 o superior (+ SQL: versión única por movilidad)
      2. La fecha de firma no puede ser futura
      3. No se puede firmar después de que termine la movilidad
      4. El número sigue el formato LA-AAAA-NNN (+ SQL único)
      5. Los estados firmados o aprobado exigen fecha de firma
      6. El acuerdo no supera 60 créditos ECTS
    Reglas de negocio ORM (5+):
      1. Créditos totales y reconocidos de sus líneas (compute con mapped)
      2. Nota media de las líneas con nota (compute con filtered + mapped)
      3. Nº de líneas y si está firmado (compute)
      4. create() numera el acuerdo, calcula la versión siguiente y pone el estado inicial
      5. write() pone la fecha de firma de hoy al aprobarlo si no la tiene
      6. onchange de la movilidad: propone la versión siguiente
      7. Botón «Nueva versión»: copia el acuerdo y sus líneas con la versión siguiente
    """
    _name = 'uprofe.learning_agreement'
    _description = 'Learning agreement'
    _rec_name = 'sNum_la'
    _order = 'sNum_la desc'

    sNum_la = fields.Char(string="Nº de learning agreement", size=30, required=True, default='Nuevo', copy=False)
    iVersion = fields.Integer(string="Versión", required=True, default=0,
                              help="Se calcula sola al guardar si se deja en 0.")
    dFecha_firma = fields.Date(string="Fecha de firma")
    sObservaciones = fields.Text(string="Observaciones")

    movilidad_id = fields.Many2one(
       'uprofe.movilidad',
       string="Movilidad",
       required=True,
       ondelete='restrict',
    )
    universidad_id = fields.Many2one(related='movilidad_id.universidad_id', string="Universidad", store=True)

    estado_id = fields.Many2one(
       'uprofe.estado_learning_agreement',
       string="Estado",
       required=True,
       ondelete='restrict',
       default=lambda self: self.env['uprofe.estado_learning_agreement']._estado_inicial(),
    )

    linea_ids = fields.One2many('uprofe.la_linea', 'learning_agreement_id', string="Líneas")

    fCreditos_totales = fields.Float(string="Créditos ECTS", compute='_compute_creditos', store=True)
    fCreditos_reconocidos = fields.Float(string="Créditos reconocidos", compute='_compute_creditos', store=True)
    fNota_media = fields.Float(string="Nota media", compute='_compute_nota_media', store=True, digits=(4, 2))
    iNum_lineas = fields.Integer(string="Nº de líneas", compute='_compute_resumen', store=True)
    bFirmado = fields.Boolean(string="Firmado", compute='_compute_resumen', store=True)

    _sql_constraints = [
        ('num_la_unico', 'UNIQUE("sNum_la")',
         'Ya existe un learning agreement con ese número.'),
        ('version_unica_por_movilidad', 'UNIQUE(movilidad_id, "iVersion")',
         'Esa movilidad ya tiene un learning agreement con esa versión.'),
    ]

    # ------------------------------------------------------------------ validaciones
    @api.constrains('iVersion')
    def _check_version(self):
        for record in self:
            if record.iVersion < 1:
                raise ValidationError("La versión debe ser 1 o superior.")

    @api.constrains('dFecha_firma')
    def _check_firma_no_futura(self):
        hoy = fields.Date.context_today(self)
        for record in self:
            if record.dFecha_firma and record.dFecha_firma > hoy:
                raise ValidationError("La fecha de firma no puede ser posterior a hoy.")

    @api.constrains('dFecha_firma', 'movilidad_id')
    def _check_firma_antes_fin(self):
        for record in self:
            if record.dFecha_firma and record.dFecha_firma > record.movilidad_id.dFecha_fin:
                raise ValidationError("No se puede firmar el acuerdo después de que termine la movilidad.")

    @api.constrains('sNum_la')
    def _check_numero(self):
        for record in self:
            if not re.match(r'^LA-\d{4}-\d{3}$', record.sNum_la or ''):
                raise ValidationError("El número sigue el formato LA-AAAA-NNN (por ejemplo LA-2026-001).")

    @api.constrains('estado_id', 'dFecha_firma')
    def _check_firma_si_firmado(self):
        for record in self:
            if record.estado_id.sName in ESTADOS_FIRMADOS and not record.dFecha_firma:
                raise ValidationError("Un acuerdo en estado «%s» necesita fecha de firma." % record.estado_id.sName)

    @api.constrains('linea_ids')
    def _check_creditos_maximos(self):
        for record in self:
            # mapped sobre el campo de la línea (no sobre la asignatura) para no perder
            # créditos si dos líneas usan la misma asignatura
            total = sum(record.linea_ids.mapped('fCreditos_ects'))
            if total > MAX_CREDITOS:
                raise ValidationError("El acuerdo %s suma %.1f créditos y el máximo es %d."
                                      % (record.sNum_la, total, MAX_CREDITOS))

    # ------------------------------------------------------------------ reglas de negocio
    @api.depends('linea_ids.asignatura_destino_id.fCreditos_ects', 'linea_ids.fCreditos_reconocidos')
    def _compute_creditos(self):
        for record in self:
            record.fCreditos_totales = sum(record.linea_ids.mapped('fCreditos_ects'))
            record.fCreditos_reconocidos = sum(record.linea_ids.mapped('fCreditos_reconocidos'))

    @api.depends('linea_ids.fNota')
    def _compute_nota_media(self):
        for record in self:
            notas = record.linea_ids.filtered('fNota').mapped('fNota')
            record.fNota_media = sum(notas) / len(notas) if notas else 0.0

    @api.depends('linea_ids', 'dFecha_firma')
    def _compute_resumen(self):
        for record in self:
            record.iNum_lineas = len(record.linea_ids)
            record.bFirmado = bool(record.dFecha_firma)

    @api.model
    def _siguiente_version(self, movilidad_id):
        versiones = self.search([('movilidad_id', '=', movilidad_id)]).mapped('iVersion')
        return max(versiones or [0]) + 1

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('iVersion') and vals.get('movilidad_id'):
                vals['iVersion'] = self._siguiente_version(vals['movilidad_id'])
            if not vals.get('sNum_la') or vals['sNum_la'] == 'Nuevo':
                anio = fields.Date.context_today(self).year
                prefijo = 'LA-%d-' % anio
                numero = self.search_count([('sNum_la', '=like', prefijo + '%')]) + 1
                vals['sNum_la'] = '%s%03d' % (prefijo, numero)
            if not vals.get('estado_id'):
                vals['estado_id'] = self.env['uprofe.estado_learning_agreement']._estado_inicial().id
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('estado_id') and not vals.get('dFecha_firma'):
            estado = self.env['uprofe.estado_learning_agreement'].browse(vals['estado_id'])
            if estado.sName == 'aprobado':
                sin_firma = self.filtered(lambda la: not la.dFecha_firma)
                if sin_firma:
                    sin_firma.write({'dFecha_firma': fields.Date.context_today(self)})
        return super().write(vals)

    @api.onchange('movilidad_id')
    def _onchange_movilidad(self):
        if self.movilidad_id and not self._origin.id:
            self.iVersion = self._siguiente_version(self.movilidad_id.id)

    def action_nueva_version(self):
        """Crea una versión nueva del acuerdo con las mismas líneas, en estado inicial."""
        self.ensure_one()
        lineas = []
        for vals in self.linea_ids.copy_data():
            vals.pop('learning_agreement_id', None)
            lineas.append(Command.create(vals))
        nueva = self.copy({
            'iVersion': self._siguiente_version(self.movilidad_id.id),
            'dFecha_firma': False,
            'estado_id': self.env['uprofe.estado_learning_agreement']._estado_inicial().id,
            'linea_ids': lineas,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': nueva.id,
            'view_mode': 'form',
        }
