# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SeguimientoPractica(models.Model):
    _name = 'uprofe.seguimiento_practica'
    _description = 'Seguimiento de práctica'
    _order = 'dFecha_emision desc'

    name = fields.Char(string='Título del seguimiento', required=True)
    iNum_seguimiento_practica = fields.Integer(string='Nº de seguimiento', required=True, default=1)
    dFecha_emision = fields.Date(string='Fecha de emisión', required=True)
    sComentarios = fields.Text(string='Comentarios')
    fCalificacion_parcial = fields.Float(string='Calificación parcial', default=0.0)

    acuerdo_id = fields.Many2one('uprofe.acuerdo', string='Acuerdo', required=True)
    tutor_externo_id = fields.Many2one('uprofe.tutor_externo', string='Tutor externo', required=True)

    @api.constrains('name')
    def _check_titulo(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError('El título del seguimiento no puede estar vacío.')

    @api.constrains('iNum_seguimiento_practica', 'acuerdo_id')
    def _check_num_seguimiento(self):
        for record in self:
            if record.iNum_seguimiento_practica <= 0:
                raise ValidationError('El número de seguimiento debe ser mayor que cero.')

            if record.acuerdo_id:
                if self.search_count([
                    ('id', '!=', record.id),
                    ('acuerdo_id', '=', record.acuerdo_id.id),
                    ('iNum_seguimiento_practica', '=', record.iNum_seguimiento_practica)
                ]):
                    raise ValidationError('Este acuerdo ya tiene un seguimiento con ese número.')

    @api.constrains('fCalificacion_parcial')
    def _check_calificacion(self):
        for record in self:
            if record.fCalificacion_parcial < 0 or record.fCalificacion_parcial > 10:
                raise ValidationError('La calificación parcial debe estar entre 0 y 10.')

    @api.constrains('sComentarios')
    def _check_comentarios(self):
        for record in self:
            if record.sComentarios:
                if not record.sComentarios.strip():
                    raise ValidationError('Los comentarios no pueden contener solo espacios.')

    @api.onchange('iNum_seguimiento_practica')
    def _onchange_num_seguimiento(self):
        if self.iNum_seguimiento_practica <= 0:
            return {
                'value': {'iNum_seguimiento_practica': 1},
                'warning': {
                    'title': 'Número no válido',
                    'message': 'El número de seguimiento debe ser mayor que cero; se ha puesto 1.'
                }
            }

    @api.onchange('fCalificacion_parcial')
    def _onchange_calificacion(self):
        if self.fCalificacion_parcial < 0 or self.fCalificacion_parcial > 10:
            return {
                'value': {'fCalificacion_parcial': 0.0},
                'warning': {
                    'title': 'Calificación no válida',
                    'message': 'La calificación debe estar entre 0 y 10; se ha puesto 0.'
                }
            }