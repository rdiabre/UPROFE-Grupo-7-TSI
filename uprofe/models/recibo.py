# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Recibo(models.Model):
    _name = 'uprofe.recibo'
    _description = 'Recibo de una tasa'
    _rec_name = 'snum_recibo'
    _order = 'dfecha desc'

    snum_recibo = fields.Char(string='Nº de recibo', required=True)  # PK
    fimporte = fields.Float(string='Importe (€)', required=True, default=0.0)
    dfecha = fields.Date(string='Fecha', required=True, default=fields.Date.context_today)
    dfecha_limite = fields.Date(string='Fecha límite')
    inumero_plazo = fields.Integer(string='Nº de plazo', required=True, default=1)

    
    tasa_id = fields.Many2one('uprofe.tasa', string='Tasa',
                              required=True, ondelete='restrict')
    
    metodo_pago_id = fields.Many2one('uprofe.metodo_pago', string='Método de pago',
                                     required=True, ondelete='restrict')

    # constrains
    @api.constrains('snum_recibo')
    def _check_num_recibo(self):
        for record in self:
            num = (record.snum_recibo or '').strip()
            if not num:
                raise ValidationError("El número de recibo no puede estar vacío.")
            if self.search_count([('id', '!=', record.id), ('snum_recibo', '=ilike', num)]):
                raise ValidationError("Ya existe un recibo con ese número.")

    @api.constrains('fimporte')
    def _check_importe(self):
        for record in self:
            if record.fimporte < 0:
                raise ValidationError("El importe no puede ser negativo.")

    @api.constrains('inumero_plazo', 'tasa_id')
    def _check_plazo(self):
        for record in self:
            if record.inumero_plazo < 1:
                raise ValidationError("El número de plazo debe ser al menos 1.")
            if record.inumero_plazo > record.tasa_id.icantidad_plazas:
                raise ValidationError("El plazo no puede superar el número de plazos de la tasa.")
            if self.search_count([('id', '!=', record.id),
                                  ('tasa_id', '=', record.tasa_id.id),
                                  ('inumero_plazo', '=', record.inumero_plazo)]):
                raise ValidationError("Esta tasa ya tiene un recibo para ese plazo.")

    # onchange
    @api.onchange('fimporte')
    def _onchange_importe(self):
        if self.fimporte < 0:
            return {
                'value': {'fimporte': 0.0},
                'warning': {'title': 'Importe no válido',
                            'message': 'El importe no puede ser negativo; se ha puesto 0.'}
            }

    @api.onchange('inumero_plazo', 'tasa_id')
    def _onchange_plazo(self):
        if self.inumero_plazo < 1 or \
                (self.tasa_id and self.inumero_plazo > self.tasa_id.icantidad_plazas):
            return {
                'value': {'inumero_plazo': 1},
                'warning': {'title': 'Plazo no válido',
                            'message': 'El plazo debe estar entre 1 y el número de plazos de la tasa; se ha puesto 1.'}
            }