# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Empresa(models.Model):
    _name = 'uprofe.empresa'
    _description = 'Empresa colaboradora'
    _order = 'name asc'

    sCif = fields.Char(string='CIF', required=True)
    name = fields.Char(string='Nombre', required=True)
    sNombre_sector = fields.Char(string='Sector')
    sEmail = fields.Char(string='Correo electrónico')

    financiacion_ids = fields.One2many('uprofe.financiacion', 'empresa_id', string='Financiaciones')
    oferta_ids = fields.One2many('uprofe.oferta_practica', 'empresa_id', string='Ofertas de práctica')
    direccion_id = fields.Many2one('uprofe.direccion', string='Dirección', required=True)


    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            if record.name:
                if record.name.strip() == '':
                    raise ValidationError('El nombre de la empresa no puede contener solo espacios.' )

    @api.constrains('sCif')
    def _check_cif(self):
        for record in self:
            if record.sCif:
                if len(record.sCif) != 9:
                    raise ValidationError('El CIF debe tener 9 caracteres.' )

                if ' ' in record.sCif:
                    raise ValidationError('El CIF no puede contener espacios.' )

    @api.constrains('sCif')
    def _check_cif_unique(self):
        for record in self:
            if record.sCif:
                lDominio = [
                    ('id', '!=', record.id),
                    ('sCif', '=ilike', record.sCif)
                ]

                if self.search_count(lDominio):
                    raise ValidationError('Ya existe una empresa con este CIF.')

    @api.constrains('sEmail')
    def _check_email(self):
        for record in self:
            if record.sEmail:
                correo = record.sEmail

                if ' ' in correo:
                    raise ValidationError('El correo electrónico no puede contener espacios.')

                if correo.count('@') != 1:
                    raise ValidationError('El correo electrónico debe contener una sola @.')

                usuario, dominio = correo.split('@')

                if not usuario or not dominio:
                    raise ValidationError('El correo electrónico debe tener texto antes y después de la @.' )

                if '.' not in dominio:
                    raise ValidationError('El dominio del correo electrónico debe contener un punto.')

                if dominio.startswith('.') or dominio.endswith('.'):
                    raise ValidationError('El dominio del correo electrónico no puede empezar ni terminar con un punto.')

    @api.onchange('sCif')
    def _onchange_cif(self):
        if self.sCif:
            return {
                'value': {
                    'sCif': self.sCif.strip().upper()
                }
            }
