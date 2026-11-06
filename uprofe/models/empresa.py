# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Empresa(models.Model):
    _name = 'uprofe.empresa'
    _description = 'Empresa colaboradora'
    _order = 'name asc'

    scif = fields.Char(string='CIF', size=9, required=True)
    name = fields.Char(string='Nombre', required=True)
    snombresector = fields.Char(string='Sector')
    semail = fields.Char(string='Correo electrónico')

    # Una empresa puede financiar muchas financiaciones (el Many2one está en uprofe.financiacion)
    financiacion_ids = fields.One2many('uprofe.financiacion', 'entidad_financiadora_id',
                                       string='Financiaciones')

    # lo decomento cuando existan los modelos relacionados:
    # oferta_ids = fields.One2many('uprofe.oferta_practica', 'empresa_id',
    #                              string='Ofertas de práctica')   # formaliza. Depende de #37
    # direccion_id = fields.Many2one('uprofe.direccion', string='Dirección',
    #                                required=True)               # tiene. Depende del issue de DIRECCION

    # Validaciones
    @api.constrains('scif')
    def _check_cif_unique(self):
        if self.search_count([('id', '!=', self.id), ('scif', '=ilike', self.scif.strip())]):
            raise ValidationError("Ya existe una empresa con este CIF.")

    @api.constrains('semail')
    def _check_email_format(self):
        if self.semail and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', self.semail.strip()):
            raise ValidationError("El correo electrónico de la empresa no es válido.")

    # onchange 
    @api.onchange('scif')
    def _onchange_cif(self):
        # Normaliza el CIF
        if self.scif:
            self.scif = self.scif.strip().upper()

    @api.onchange('semail')
    def _onchange_email(self):
        if self.semail and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', self.semail.strip()):
            return {
                'value': {'semail': False},
                'warning': {
                    'title': 'Correo no válido',
                    'message': 'El formato del correo electrónico no parece correcto.'
                }
            }