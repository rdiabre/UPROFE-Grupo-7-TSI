# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Tasa(models.Model):
    _name = 'uprofe.tasa'
    _description = 'Tasa universitaria'
    _rec_name = 'snum_liquidacion'
    _order = 'id desc'

    snum_liquidacion = fields.Char(string='Nº de liquidación', required=True)
    fimporte = fields.Float(string='Importe (€)', required=True, default=0.0)
    sestado = fields.Selection([('pendiente', 'Pendiente'),
                                ('pagada', 'Pagada')],
                               string='Estado', required=True, default='pendiente')
    stipo_tasa = fields.Selection([('matricula', 'Matrícula'),
                                   ('secretaria', 'Secretaría'),
                                   ('titulo', 'Título'),
                                   ('otras', 'Otras')],
                                  string='Tipo de tasa', required=True, default='matricula')
    icantidad_plazas = fields.Integer(string='Nº de plazos', required=True, default=1)

    alumno_id = fields.Many2one('uprofe.persona', string='Alumno',
                                required=True, ondelete='restrict')
    recibo_ids = fields.One2many('uprofe.recibo', 'tasa_id', string='Recibos')

    # constrains
    @api.constrains('snum_liquidacion')
    def _check_num_liquidacion(self):
        num = (self.snum_liquidacion or '').strip()
        if not num:
            raise ValidationError("El número de liquidación no puede estar vacío.")
        if self.search_count([('id', '!=', self.id),
                              ('snum_liquidacion', '=ilike', num)]):
            raise ValidationError("Ya existe una tasa con este número de liquidación.")

    @api.constrains('fimporte')
    def _check_importe(self):
        if self.fimporte < 0:
            raise ValidationError("El importe no puede ser negativo.")

    @api.constrains('icantidad_plazas')
    def _check_plazas(self):
        if self.icantidad_plazas < 1:
            raise ValidationError("La tasa debe tener al menos un plazo.")

    # onchange 
    @api.onchange('fimporte')
    def _onchange_importe(self):
        if self.fimporte < 0:
            return {
                'value': {'fimporte': 0.0},
                'warning': {'title': 'Importe no válido',
                            'message': 'El importe no puede ser negativo; se ha puesto 0.'}
            }

    @api.onchange('icantidad_plazas')
    def _onchange_plazas(self):
        if self.icantidad_plazas < 1:
            return {
                'value': {'icantidad_plazas': 1},
                'warning': {'title': 'Plazos no válidos',
                            'message': 'Debe haber al menos un plazo; se ha puesto 1.'}
            }