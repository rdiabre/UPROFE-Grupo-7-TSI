# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Idioma(models.Model):
    _name = 'uprofe.idioma'
    _description = 'Idioma'
    _rec_name = 'sName'

    sName = fields.Char(string="Nombre del idioma", size=50, required=True)

    # Descomentar cuando existan estos modelos
    # asignatura_destino_ids = fields.One2many('uprofe.asignatura_destino', 'idioma_id', string="Asignaturas")
    # plaza_erasmus_ids = fields.One2many('uprofe.plaza_erasmus', 'idioma_id', string="Plazas")

    _sql_constraints = [
        ('nombre_unico', 'UNIQUE("sName")', 'Ya existe un idioma con ese nombre.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'\.\-]+$"
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre del idioma solo puede contener letras, espacios y guiones."
                )

    @api.constrains('sName')
    def _check_nombre_unico_ci(self):
        for record in self:
            repetido = self.search_count([
                ('sName', '=ilike', (record.sName or '').strip()),
                ('id', '!=', record.id),
            ])
            if repetido:
                raise ValidationError("Ya existe un idioma con ese nombre.")
