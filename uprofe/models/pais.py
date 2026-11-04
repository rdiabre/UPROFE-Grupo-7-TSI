# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Pais(models.Model):
    _sName = 'uprofe.pais'
    _sDescription = 'País'

    sName = fields.Char(string="Nombre del país", size=50, required=True)
    sDescription = fields.Char(string="Descripción del país", size=150)

    pais_id = fields.Many2one('uprofe.pais', string="País", required=True, ondelete='cascade')

    ciudad_ids = fields.One2many('uprofe.ciudad', 'pais_id', string="Ciudades")

    _sql_constraints = [
        ('ciudad_unica_por_pais', 'UNIQUE(name, pais_id)',
        'Ya existe una ciudad con ese nombre en ese país.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'\.\-]+$"
        for record in self:
            if not re.match(regex_nombre, (record.name or '').strip()):
                raise ValidationError(
                    "El nombre del país solo puede contener letras, espacios y guiones."
                )