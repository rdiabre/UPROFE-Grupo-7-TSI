# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MetodoPago(models.Model):
    _name = 'uprofe.metodo_pago'
    _description = 'Método de pago'
    
    name = fields.Char(string='Método de pago', required=True)  # PK

    recibo_ids = fields.One2many('uprofe.recibo', 'metodo_pago_id', string='Recibos')

    @api.constrains('name')
    def _check_metodo(self):
        for record in self:
            metodo = (record.name or '').strip()
            if not metodo:
                raise ValidationError("El método de pago no puede estar vacío.")
            if self.search_count([('id', '!=', record.id), ('name', '=ilike', metodo)]):
                raise ValidationError("Ya existe ese método de pago.")