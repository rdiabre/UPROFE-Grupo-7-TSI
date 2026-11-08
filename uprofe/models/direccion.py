# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Direccion(models.Model):
    _name = 'uprofe.direccion'
    _description = 'Dirección postal'
    _order = 'sciudad asc, scalle asc'

    scod_direccion = fields.Char(string='Código', required=True) 
    name = fields.Char(string='Dirección', compute='_compute_name', store=True)
    scalle = fields.Char(string='Calle', required=True)
    snumero = fields.Char(string='Número', required=True)
    sciudad = fields.Char(string='Ciudad', required=True)
    scod_postal = fields.Char(string='Código postal', size=5, required=True)

    empresa_ids = fields.One2many('uprofe.empresa', 'direccion_id', string='Empresas')

    # descomento cuando uprofe.persona tenga direccion_id
    # persona_ids = fields.One2many('uprofe.persona', 'direccion_id', string='Personas')

    @api.depends('scalle', 'snumero', 'scod_postal', 'sciudad')
    def _compute_name(self):
        for record in self:
            record.name = "%s %s, %s %s" % (
                record.scalle or '', record.snumero or '',
                record.scod_postal or '', record.sciudad or '')

    # constrains
    @api.constrains('scod_direccion')
    def _check_cod_direccion(self):
        for record in self:
            cod = (record.scod_direccion or '').strip()
            if not cod:
                raise ValidationError("El código de la dirección no puede estar vacío.")
            if self.search_count([('id', '!=', record.id), ('scod_direccion', '=ilike', cod)]):
                raise ValidationError("Ya existe una dirección con ese código.")

    @api.constrains('scalle', 'snumero', 'sciudad')
    def _check_campos_no_vacios(self):
        for record in self:
            if not (record.scalle or '').strip() or not (record.snumero or '').strip() \
                    or not (record.sciudad or '').strip():
                raise ValidationError("La calle, el número y la ciudad no pueden estar vacíos.")

    @api.constrains('scod_postal')
    def _check_cod_postal(self):
        for record in self:
            if not re.match(r'^\d{5}$', (record.scod_postal or '').strip()):
                raise ValidationError("El código postal debe tener 5 dígitos.")