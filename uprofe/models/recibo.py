# -*- coding: utf-8 -*-
# Autora: Sandra Megolla Fernández
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Recibo(models.Model):
    _name = 'uprofe.recibo'
    _description = 'Recibo de una tasa'
    _order = 'dFecha desc'

    name = fields.Char(string='Nº de recibo', required=True)
    fImporte = fields.Float(string='Importe (€)', required=True, default=0.0)
    dFecha = fields.Date(string='Fecha de pago', required=True)
    dFecha_limite = fields.Date(string='Fecha límite')
    iNumero_plazo = fields.Integer(string='Nº de plazo', required=True, default=1)


    tasa_id = fields.Many2one('uprofe.tasa', string='Tasa', required=True)

    metodo_pago_id = fields.Many2one('uprofe.metodo_pago', string='Método de pago', required=True)

    @api.constrains('name')
    def _check_num_recibo(self):
        for record in self:
            num = (record.name or '').strip()

            if not num:
                raise ValidationError( "El número de recibo no puede estar vacío." )

            if record.name != num:
                raise ValidationError("El número de recibo no puede tener espacios al principio o al final." )

            if self.search_count([
                ('id', '!=', record.id),
                ('name', '=ilike', num)
            ]):
                raise ValidationError( "Ya existe un recibo con ese número." )

    @api.constrains('fImporte')
    def _check_importe(self):
        for record in self:
            if record.fImporte < 0:
                raise ValidationError("El importe no puede ser negativo.")

    @api.constrains('iNumero_plazo', 'tasa_id')
    def _check_plazo(self):
        for record in self:
            if record.iNumero_plazo < 1:
                raise ValidationError("El número de plazo debe ser al menos 1.")
            if record.iNumero_plazo > record.tasa_id.iCantidad_plazos:
                raise ValidationError("El plazo no puede superar el número de plazos de la tasa.")
            if self.search_count([('id', '!=', record.id),
                                  ('tasa_id', '=', record.tasa_id.id),
                                  ('iNumero_plazo', '=', record.iNumero_plazo)]):
                raise ValidationError("Esta tasa ya tiene un recibo para ese plazo.")

    @api.onchange('fImporte')
    def _onchange_importe(self):
        if self.fImporte < 0:
            return {
                'value': {'fImporte': 0.0},
                'warning': {'title': 'Importe no válido',
                            'message': 'El importe no puede ser negativo; se ha puesto 0.'}
            }

    @api.onchange('iNumero_plazo', 'tasa_id')
    def _onchange_plazo(self):
        if self.iNumero_plazo < 1 or \
                (self.tasa_id and self.iNumero_plazo > self.tasa_id.iCantidad_plazos):
            return {
                'value': {'iNumero_plazo': 1},
                'warning': {'title': 'Plazo no válido',
                            'message': 'El plazo debe estar entre 1 y el número de plazos de la tasa; se ha puesto 1.'}
            }
