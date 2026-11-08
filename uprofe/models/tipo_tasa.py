# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TipoTasa(models.Model):
    _name = 'uprofe.tipo_tasa'
    _description = 'Tipo de tasa'

    stipo = fields.Selection([
        ('matriculacion', 'Tasa de matriculación'),
        ('expedicion', 'Tasa de expedición de títulos o certificados'),
        ('servicios', 'Tasa por servicios complementarios'),
        ('pruebas', 'Tasa por pruebas o exámenes'),
    ], string='Tipo', required=True)  # PK

    tasa_ids = fields.One2many('uprofe.tasa', 'tipo_tasa_id', string='Tasas')

    @api.depends('stipo')
    def _compute_display_name(self):
        etiquetas = dict(self._fields['stipo'].selection)
        for record in self:
            record.display_name = etiquetas.get(record.stipo, '')

    @api.constrains('stipo')
    def _check_tipo_unico(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('stipo', '=', record.stipo)]):
                raise ValidationError("Ya existe ese tipo de tasa.")