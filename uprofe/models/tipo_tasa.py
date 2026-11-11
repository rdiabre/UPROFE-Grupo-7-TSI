# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TipoTasa(models.Model):
    _name = 'uprofe.tipo_tasa'
    _description = 'Tipo de tasa'

    name = fields.Selection([
        ('matriculacion', 'Tasa de matriculación'),
        ('expedicion', 'Tasa de expedición de títulos o certificados'),
        ('servicios', 'Tasa por servicios complementarios'),
        ('pruebas', 'Tasa por pruebas o exámenes'),
    ], string='Tipo', required=True)

    tasa_ids = fields.One2many('uprofe.tasa', 'tipo_tasa_id', string='Tasas')

    # Refuerza la misma regla de unicidad ante altas simultáneas.
    # No es una regla de negocio adicional.
    _sql_constraints = [
        ('tipo_tasa_nombre_unique', 'unique(name)', 'Ya existe ese tipo de tasa.'),
    ]

    @api.constrains('name')
    def _check_tipo_unico(self):
        for record in self:
            if self.search_count([
                ('id', '!=', record.id),
                ('name', '=', record.name)
            ]):
                raise ValidationError("Ya existe ese tipo de tasa.")
