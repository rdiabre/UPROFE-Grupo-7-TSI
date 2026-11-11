# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Acuerdo(models.Model):
    _name = 'uprofe.acuerdo'
    _description = 'Acuerdo de prácticas'
    _order = 'dFecha_inicio desc'

    name = fields.Char(string='Nº de acuerdo', required=True)
    dFecha_firma = fields.Date(string='Fecha de firma', required=True)
    dFecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    dFecha_fin = fields.Date(string='Fecha de fin', required=True)

    # alumno_id = fields.Many2one('uprofe.alumno', string='Alumno', required=True)
    tutor_interno_id = fields.Many2one('uprofe.profesor', string='Tutor interno', required=True)
    solicitud_id = fields.Many2one('uprofe.solicitud', string='Solicitud')
    estado_acuerdo_id = fields.Many2one('uprofe.estado_acuerdo', string='Estado', required=True)
    seguimiento_ids = fields.One2many('uprofe.seguimiento_practica', 'acuerdo_id', string='Seguimientos')

    @api.constrains('name')
    def _check_num_acuerdo(self):
        for record in self:
            numero = (record.name or '').strip()
            if not numero:
                raise ValidationError('El número de acuerdo no puede estar vacío.')
            if record.name != numero:
                raise ValidationError('El número de acuerdo no puede tener espacios al principio o al final.')
            if len(numero) > 50:
                raise ValidationError('El número de acuerdo no puede superar los 50 caracteres.')

    @api.constrains('name')
    def _check_num_acuerdo_unique(self):
        for record in self:
            if record.name:
                if self.search_count([
                    ('id', '!=', record.id),
                    ('name', '=ilike', record.name)
                ]):
                    raise ValidationError('Ya existe un acuerdo con este número.')

    @api.constrains('dFecha_inicio', 'dFecha_fin')
    def _check_fechas(self):
        for record in self:
            if record.dFecha_inicio and record.dFecha_fin:
                if record.dFecha_fin <= record.dFecha_inicio:
                    raise ValidationError('La fecha de fin debe ser posterior a la de inicio.')

    @api.onchange('dFecha_inicio', 'dFecha_fin')
    def _onchange_fechas(self):
        if self.dFecha_inicio and self.dFecha_fin:
            if self.dFecha_fin <= self.dFecha_inicio:
                return {
                    'value': {'dFecha_fin': False},
                    'warning': {
                        'title': 'Fechas incorrectas',
                        'message': 'La fecha de fin debe ser posterior a la de inicio.'
                    }
                }
