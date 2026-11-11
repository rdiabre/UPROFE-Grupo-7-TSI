# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Direccion(models.Model):
    _name = 'uprofe.direccion'
    _description = 'Dirección postal'
    _order = 'sCiudad asc, sCalle asc'

    name = fields.Char(string='Código de dirección', required=True)
    sCalle = fields.Char(string='Calle', required=True)
    sNumero = fields.Char(string='Número', required=True)
    sCiudad = fields.Char(string='Ciudad', required=True)
    sCod_postal = fields.Char(string='Código postal', required=True)

    empresa_ids = fields.One2many('uprofe.empresa', 'direccion_id', string='Empresas')
    # persona_ids = fields.One2many('uprofe.persona', 'direccion_id', string='Personas')

    @api.constrains('name')
    def _check_codigo(self):
        for record in self:
            codigo = (record.name or '').strip()
            if not codigo:
                raise ValidationError('El código de dirección no puede estar vacío.')
            if record.name != codigo:
                raise ValidationError('El código de dirección no puede tener espacios al principio o al final.')
            if self.search_count([
                ('id', '!=', record.id),
                ('name', '=ilike', codigo)
            ]):
                raise ValidationError('Ya existe una dirección con ese código.')

    @api.constrains('sCalle', 'sNumero', 'sCiudad')
    def _check_datos_direccion(self):
        for record in self:
            if not record.sCalle or not record.sCalle.strip():
                raise ValidationError('La calle no puede estar vacía.')
            if not record.sNumero or not record.sNumero.strip():
                raise ValidationError('El número no puede estar vacío; puedes indicar S/N si no tiene.')
            if not record.sCiudad or not record.sCiudad.strip():
                raise ValidationError('La ciudad no puede estar vacía.')

    @api.constrains('sCod_postal')
    def _check_codigo_postal(self):
        for record in self:
            codigo = record.sCod_postal or ''

            if len(codigo) != 5:
                raise ValidationError('El código postal debe tener 5 caracteres.')

            for caracter in codigo:
                if caracter not in '0123456789':
                    raise ValidationError('El código postal solo puede contener dígitos del 0 al 9.')

    @api.onchange('name')
    def _onchange_codigo(self):
        if self.name:
            return {
                'value': {
                    'name': self.name.strip().upper()
                }
            }