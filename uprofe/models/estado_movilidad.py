# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EstadoMovilidad(models.Model):
    _name = 'uprofe.estado_movilidad'
    _description = 'Estado de una movilidad'

    sName = fields.Char(string="Nombre del estado", size=30, required=True)
    sDescripcion = fields.Text(string="Descripción")

    # Descomentar cuando exista Movilidad
    # movilidad_ids = fields.One2many('uprofe.movilidad', 'estado_id', string="Movilidades")

    _sql_constraints = [
        ('nombre_unico', 'UNIQUE("sName")', 'Ya existe un estado con ese nombre.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r'^[a-z]+(_[a-z]+)*$'
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre del estado va en minúsculas, sin tildes ni espacios "
                    "(usad guion bajo para separar palabras, por ejemplo 'en_curso')."
                )
