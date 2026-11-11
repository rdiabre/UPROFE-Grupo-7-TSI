# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SeguimientoAluInt(models.Model):
    _name = 'uprofe.seguimiento_alu_int'
    _description = 'Seguimiento del alumno interno'
    _order = 'dFecha desc'

    name = fields.Char(string='Seguimiento', compute='_compute_name', store=True)
    iNum_seguimiento_alu = fields.Integer(string='Nº de seguimiento', required=True, default=1)
    dFecha = fields.Date(string='Fecha', required=True)
    sObservaciones = fields.Text(string='Observaciones')
    fCalificacion = fields.Float(string='Calificación', default=0.0)

    acuerdo_id = fields.Many2one('uprofe.acuerdo', string='Acuerdo', required=True)

    _sql_constraints = [
        ('seguimiento_acuerdo_uniq', 'unique(acuerdo_id, "iNum_seguimiento_alu")', 'Ya existe un seguimiento con ese número en este acuerdo.'),
    ]

    @api.depends('iNum_seguimiento_alu')
    def _compute_name(self):
        for record in self:
            record.name = "Seguimiento %s" % record.iNum_seguimiento_alu

    @api.constrains('iNum_seguimiento_alu')
    def _check_numero(self):
        for record in self:
            if record.iNum_seguimiento_alu < 1:
                raise ValidationError('El número de seguimiento debe ser mayor que 0.')

    @api.constrains('fCalificacion')
    def _check_calificacion(self):
        for record in self:
            if record.fCalificacion < 0 or record.fCalificacion > 10:
                raise ValidationError('La calificación debe estar entre 0 y 10.')

    @api.constrains('sObservaciones')
    def _check_observaciones(self):
        for record in self:
            if record.sObservaciones:
                if not record.sObservaciones.strip():
                    raise ValidationError('Las observaciones no pueden contener solo espacios.')

    @api.onchange('iNum_seguimiento_alu')
    def _onchange_numero(self):
        if self.iNum_seguimiento_alu < 1:
            return {
                'value': {'iNum_seguimiento_alu': 1},
                'warning': {
                    'title': 'Valor incorrecto',
                    'message': 'El número de seguimiento debe ser mayor que 0; se ha puesto 1.'
                }
            }

    @api.onchange('fCalificacion')
    def _onchange_calificacion(self):
        if self.fCalificacion < 0:
            return {
                'value': {'fCalificacion': 0.0},
                'warning': {
                    'title': 'Calificación no válida',
                    'message': 'La calificación no puede ser negativa; se ha puesto 0.'
                }
            }

        if self.fCalificacion > 10:
            return {
                'value': {'fCalificacion': 10.0},
                'warning': {
                    'title': 'Calificación no válida',
                    'message': 'La calificación no puede superar 10; se ha puesto 10.'
                }
            }

    @api.onchange('sObservaciones')
    def _onchange_observaciones(self):
        if self.sObservaciones:
            self.sObservaciones = self.sObservaciones.strip()
