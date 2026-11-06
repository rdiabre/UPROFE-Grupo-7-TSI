# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Pais(models.Model):
    _name = 'uprofe.pais'
    _description = 'País'

    sName = fields.Char(string="Nombre del país", size=50, required=True)
    sDescription = fields.Char(string="Descripción del país", size=150)

    # ciudad_ids = fields.One2many('uprofe.ciudad', 'pais_id', string="Ciudades")

    @api.constrains('sName')
    def _check_nombre_unico(self):
        for record in self:
            if record.sName:
                existe = self.search_count([
                    ('sName', '=ilike', record.sName.strip()),
                    ('id', '!=', record.id)
                ])
                if existe > 0:
                    raise ValidationError("Ya existe un país con ese nombre.")

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'\.\-]+$"
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre del país solo puede contener letras, espacios y guiones."
                )