# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SeguimientoAluInt(models.Model):
    _name = 'uprofe.seguimiento_alu_int'
    _description = 'Seguimiento del alumno'
    _order = 'dfecha desc'

    name = fields.Char(string='Seguimiento', compute='_compute_name', store=True)
    inum_seguimiento_alu = fields.Integer(string='Nº de seguimiento', required=True, default=1)  # PK
    dfecha = fields.Date(string='Fecha', required=True, default=fields.Date.context_today)
    sobservaciones = fields.Text(string='Observaciones')
    fcalificacion = fields.Float(string='Calificación', default=0.0, aggregator='avg')

  

    acuerdo_id = fields.Many2one('uprofe.acuerdo', string='Acuerdo',
                                 required=True, ondelete='cascade')
    _sql_constraints = [
        ('seguimiento_acuerdo_uniq', 'unique(acuerdo_id, inum_seguimiento_alu)',
         'Ya existe un seguimiento con ese número en este acuerdo.'),
    ]

    @api.depends('inum_seguimiento_alu')
    def _compute_name(self):
        for record in self:
            record.name = "Seguimiento %s" % record.inum_seguimiento_alu

    # constrains
    @api.constrains('inum_seguimiento_alu')
    def _check_numero(self):
        for record in self:
            if record.inum_seguimiento_alu < 1:
                raise ValidationError("El número de seguimiento debe ser mayor que 0.")

    @api.constrains('fcalificacion')
    def _check_calificacion(self):
        for record in self:
            if record.fcalificacion < 0 or record.fcalificacion > 10:
                raise ValidationError("La calificación debe estar entre 0 y 10.")

    # onchange
    @api.onchange('inum_seguimiento_alu')
    def _onchange_numero(self):
        if self.inum_seguimiento_alu < 1:
            return {
                'value': {'inum_seguimiento_alu': 1},
                'warning': {'title': 'Valor incorrecto',
                            'message': 'El número de seguimiento debe ser mayor que 0.'}
            }

    @api.onchange('fcalificacion')
    def _onchange_calificacion(self):
        if self.fcalificacion < 0:
            return {
                'value': {'fcalificacion': 0.0},
                'warning': {'title': 'Calificación no válida',
                            'message': 'La calificación no puede ser negativa; se ha puesto 0.'}
            }
        if self.fcalificacion > 10:
            return {
                'value': {'fcalificacion': 10.0},
                'warning': {'title': 'Calificación no válida',
                            'message': 'La calificación no puede superar 10; se ha puesto 10.'}
            }