# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Empresa(models.Model):
    _name = 'uprofe.empresa'
    _description = 'Empresa colaboradora'
    _order = 'name asc'

    sCif = fields.Char(string='CIF', size=9, required=True)
    name = fields.Char(string='Nombre', required=True)
    sNombre_sector = fields.Char(string='Sector')
    sEmail = fields.Char(string='Correo electrónico')

    financiacion_ids = fields.One2many('uprofe.financiacion', 'empresa_id', string='Financiaciones')
    oferta_ids = fields.One2many('uprofe.oferta_practica', 'empresa_id', string='Ofertas de práctica')   
    #direccion_id = fields.Many2one('uprofe.direccion', string='Dirección', required=True)               


    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            if record.name:
                if record.name.strip() == '':
                    raise ValidationError(
                        'El nombre de la empresa no puede contener solo espacios.'
                    )
    
    @api.constrains('sCif')
    def _check_cif(self):
        for record in self:
            if record.sCif:
                if len(record.sCif) != 9:
                    raise ValidationError(
                        'El CIF debe tener 9 caracteres.'
                    )

                if ' ' in record.sCif:
                    raise ValidationError(
                        'El CIF no puede contener espacios.'
                    ) 
                                   
    @api.constrains('sCif')
    def _check_cif_unique(self):
        for record in self:
            if record.sCif:
                lDominio = [
                    ('id', '!=', record.id),
                    ('sCif', '=ilike', record.sCif)
                ]

                if self.search_count(lDominio):
                    raise ValidationError(
                        'Ya existe una empresa con este CIF.'
                    )
                    
    @api.constrains('sEmail')
    def _check_email(self):
        for record in self:
            if record.sEmail:
                if '@' not in record.sEmail:
                    raise ValidationError(
                        'El correo electrónico debe contener una @.'
                    )

                if ' ' in record.sEmail:
                    raise ValidationError(
                        'El correo electrónico no puede contener espacios.'
                    )

    @api.onchange('sCif')
    def _onchange_cif(self):
        if self.sCif:
            return {
                'value': {
                    'sCif': self.sCif.strip().upper()
                }
            }
