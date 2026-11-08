# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Tasa(models.Model):
    _name = 'uprofe.tasa'
    _description = 'Tasa universitaria'
    _rec_name = 'snum_liquidacion'
    _order = 'id desc'

    snum_liquidacion = fields.Char(string='Nº de liquidación', required=True)  # PK
    fimporte = fields.Float(string='Importe (€)', required=True, default=0.0)
    sestado = fields.Selection([('pendiente', 'Pendiente'), ('pagada', 'Pagada')],
                               string='Estado', required=True, default='pendiente')
    icantidad_plazas = fields.Integer(string='Nº de plazos', required=True, default=1)

    # TASA tiene TIPO_TASA (cada tasa tiene un tipo)
    tipo_tasa_id = fields.Many2one('uprofe.tipo_tasa', string='Tipo de tasa',
                                   required=True, ondelete='restrict')

    # Descomento cuando uprofe.alumno esté en main
    # alumno_id = fields.Many2one('uprofe.alumno', string='Alumno',
    #                             required=True, ondelete='restrict')

    # TASA se abona RECIBO. Descomento cuando exista uprofe.recibo
    # recibo_ids = fields.One2many('uprofe.recibo', 'tasa_id', string='Recibos')

    # constrains
    @api.constrains('snum_liquidacion')
    def _check_num_liquidacion(self):
        for record in self:
            num = (record.snum_liquidacion or '').strip()
            if not num:
                raise ValidationError("El número de liquidación no puede estar vacío.")
            if self.search_count([('id', '!=', record.id), ('snum_liquidacion', '=ilike', num)]):
                raise ValidationError("Ya existe una tasa con ese número de liquidación.")

    @api.constrains('fimporte')
    def _check_importe(self):
        for record in self:
            if record.fimporte < 0:
                raise ValidationError("El importe no puede ser negativo.")

    @api.constrains('icantidad_plazas')
    def _check_plazas(self):
        for record in self:
            if record.icantidad_plazas < 1:
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