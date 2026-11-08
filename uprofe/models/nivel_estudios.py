# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NivelEstudios(models.Model):
    _name = 'uprofe.nivel_estudios'
    _description = 'Nivel de estudios'

    sName = fields.Char(string="Nombre del nivel", size=30, required=True)

    # Descomentar cuando exista PlazaErasmus
    # plaza_ids = fields.One2many('uprofe.plaza_erasmus', 'nivel_estudios_id', string="Plazas")

    _sql_constraints = [
        ('nombre_unico', 'UNIQUE(sName)', 'Ya existe un nivel de estudios con ese nombre.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r'^[a-z]+(_[a-z]+)*$'
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre va en minúsculas, sin tildes ni espacios "
                    "(por ejemplo 'grado', 'master' o 'doctorado')."
                )