# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ConvenioEmpresa(models.Model):
    _name = 'uprofe.convenio_empresa'
    _description = 'Convenio de prácticas con empresa'
    _order = 'dFecha_firma desc'

    name = fields.Char(string='Nº de convenio de prácticas', required=True)
    dFecha_firma = fields.Date(string='Fecha de firma', required=True)
    dFecha_expiracion = fields.Date(string='Fecha de expiración', required=True)

    estado_convenio_id = fields.Many2one('uprofe.estado_convenio', string='Estado', required=True)
    oferta_ids = fields.One2many('uprofe.oferta_practica', 'convenio_id', string='Ofertas de práctica')

    @api.constrains('name')
    def _check_num_convenio(self):
        for record in self:
            if record.name:
                if record.name.strip() == '':
                    raise ValidationError(
                        'El número de convenio no puede contener solo espacios.'
                    )
    
    @api.constrains('name')
    def _check_num_convenio_unique(self):
        for record in self:
            if record.name:
                lDominio = [
                    ('id', '!=', record.id),
                    ('name', '=ilike', record.name.strip())
                ]

                if self.search_count(lDominio):
                    raise ValidationError(
                        'Ya existe un convenio con este número.'
                    )

    @api.constrains('dFecha_firma', 'dFecha_expiracion')
    def _check_fechas(self):
        for record in self:
            if record.dFecha_firma and record.dFecha_expiracion:
                if record.dFecha_expiracion <= record.dFecha_firma:
                    raise ValidationError(
                        'La fecha de expiración debe ser posterior a la fecha de firma.'
                    )

    @api.onchange('dFecha_firma', 'dFecha_expiracion')
    def _onchange_fechas(self):
        if self.dFecha_firma and self.dFecha_expiracion:
            if self.dFecha_expiracion <= self.dFecha_firma:
                return {
                    'value': {
                        'dFecha_expiracion': False
                    },
                    'warning': {
                        'title': 'Fechas incorrectas',
                        'message': (
                            'La fecha de expiración debe ser posterior '
                            'a la fecha de firma.'
                        )
                    }
                }