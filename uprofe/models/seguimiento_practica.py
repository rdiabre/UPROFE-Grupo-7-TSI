# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SeguimientoPractica(models.Model):
    _name = 'uprofe.seguimiento_practica'
    _description = 'Seguimiento de práctica'
    _order = 'dfecha_emision desc'

    inum_seguimiento_practica = fields.Integer(string='Nº de seguimiento', required=True, default=1)
    dfecha_emision = fields.Date(string='Fecha de emisión', required=True,
                                 default=fields.Date.context_today)
    scomentarios = fields.Text(string='Comentarios')
    fcalificacion_parcial = fields.Float(string='Calificación parcial', default=0.0)

    acuerdo_id = fields.Many2one('uprofe.acuerdo', string='Acuerdo',
                                 required=True, ondelete='restrict')

    tutor_externo_id = fields.Many2one('uprofe.tutor_externo', string='Tutor externo',
                                        ondelete='restrict')

    @api.depends('inum_seguimiento_practica')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"Seguimiento {record.inum_seguimiento_practica}"

    # constrains
    @api.constrains('inum_seguimiento_practica', 'acuerdo_id')
    def _check_num_seguimiento(self):
        if self.inum_seguimiento_practica <= 0:
            raise ValidationError("El número de seguimiento debe ser mayor que cero.")
        if self.search_count([('id', '!=', self.id),
                              ('acuerdo_id', '=', self.acuerdo_id.id),
                              ('inum_seguimiento_practica', '=', self.inum_seguimiento_practica)]):
            raise ValidationError("Este acuerdo ya tiene un seguimiento con ese número.")

    @api.constrains('fcalificacion_parcial')
    def _check_calificacion(self):
        if self.fcalificacion_parcial < 0 or self.fcalificacion_parcial > 10:
            raise ValidationError("La calificación parcial debe estar entre 0 y 10.")

    # onchange 
    @api.onchange('fcalificacion_parcial')
    def _onchange_calificacion(self):
        if self.fcalificacion_parcial < 0 or self.fcalificacion_parcial > 10:
            return {
                'value': {'fcalificacion_parcial': 0.0},
                'warning': {'title': 'Calificación no válida',
                            'message': 'La calificación debe estar entre 0 y 10; se ha puesto 0.'}
            }