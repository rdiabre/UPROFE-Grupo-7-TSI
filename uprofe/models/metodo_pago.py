# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MetodoPago(models.Model):
    _name = 'uprofe.metodo_pago'
    _description = 'Método de pago'

    name = fields.Char(string='Método de pago', required=True)

    recibo_ids = fields.One2many('uprofe.recibo', 'metodo_pago_id', string='Recibos')

    @api.constrains('name')
    def _check_metodo(self):
        for record in self:
            metodo = (record.name or '').strip()

            if not metodo:
                raise ValidationError( "El método de pago no puede estar vacío.")

            if record.name != metodo:
                raise ValidationError("El método de pago no puede tener espacios al principio o al final.")

            if len(metodo) > 50:
                raise ValidationError("El método de pago no puede superar los 50 caracteres.")

            if self.search_count([
                ('id', '!=', record.id),
                ('name', '=ilike', metodo)
            ]):
                raise ValidationError( "Ya existe ese método de pago.")

    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            self.name = ' '.join(self.name.split())
