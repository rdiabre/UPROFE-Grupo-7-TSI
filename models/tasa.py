# -*- coding: utf-8 -*-
# Autora: Sandra Megolla Fernández
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Tasa(models.Model):
    _name = 'uprofe.tasa'
    _description = 'Tasa universitaria'
    _order = 'id desc'

    name = fields.Char(string='Nº de liquidación', required=True)
    fImporte = fields.Float(string='Importe (€)', required=True, default=0.0)
    sEstado = fields.Selection([('pendiente', 'Pendiente'), ('pagada', 'Pagada')],
                               string='Estado', required=True, default='pendiente')
    iCantidad_plazos = fields.Integer(string='Nº de plazos', required=True, default=1)

    tipo_tasa_id = fields.Many2one('uprofe.tipo_tasa', string='Tipo de tasa', required=True)

    alumno_id = fields.Many2one('uprofe.alumno', string='Alumno', required=True)

    recibo_ids = fields.One2many('uprofe.recibo', 'tasa_id', string='Recibos')

    @api.constrains('name')
    def _check_num_liquidacion(self):
        for record in self:
            num = (record.name or '').strip()

            if not num:
                raise ValidationError( "El número de liquidación no puede estar vacío." )

            if record.name != num:
                raise ValidationError( "El número de liquidación no puede tener espacios al principio o al final.")

            if self.search_count([
                ('id', '!=', record.id),
                ('name', '=ilike', num)
            ]):
                raise ValidationError( "Ya existe una tasa con ese número de liquidación." )

    @api.constrains('fImporte')
    def _check_importe(self):
        for record in self:
            if record.fImporte < 0:
                raise ValidationError("El importe no puede ser negativo.")

    @api.constrains('iCantidad_plazos')
    def _check_plazos(self):
        for record in self:
            if record.iCantidad_plazos < 1:
                raise ValidationError("La tasa debe tener al menos un plazo.")
            for recibo in record.recibo_ids:
                if recibo.iNumero_plazo > record.iCantidad_plazos:
                    raise ValidationError( "No puedes reducir los plazos porque existe un recibo con un número de plazo superior." )

    @api.onchange('fImporte')
    def _onchange_importe(self):
        if self.fImporte < 0:
            return {
                'value': {'fImporte': 0.0},
                'warning': {'title': 'Importe no válido',
                            'message': 'El importe no puede ser negativo; se ha puesto 0.'}
            }

    @api.onchange('iCantidad_plazos')
    def _onchange_plazos(self):
        if self.iCantidad_plazos < 1:
            return {
                'value': {'iCantidad_plazos': 1},
                'warning': {'title': 'Plazos no válidos',
                            'message': 'Debe haber al menos un plazo; se ha puesto 1.'}
            }
