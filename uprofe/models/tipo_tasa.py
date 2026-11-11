# -*- coding: utf-8 -*-
# Autora: Sandra Megolla Fernández
from odoo import models, fields


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

    _sql_constraints = [
        ('tipo_tasa_nombre_unique', 'unique(name)', 'Ya existe ese tipo de tasa.'),
    ]

