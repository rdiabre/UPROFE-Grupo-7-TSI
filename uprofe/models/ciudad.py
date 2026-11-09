# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Ciudad(models.Model):
    _name = 'uprofe.ciudad'
    _description = 'Ciudad'
    _rec_name = 'sName'

    sName = fields.Char(string="Nombre de la ciudad", size=50, required=True)
    sDescription = fields.Char(string="Descripción de la ciudad", size=150)
    
    pais_id = fields.Many2one(
       'uprofe.pais',
       string="País",
       required=True,
       ondelete='cascade',
    )

    _sql_constraints = [
       ('ciudad_unica_por_pais', 'UNIQUE("sName", pais_id)',
        'Ya existe una ciudad con ese nombre en ese país.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'\.\-]+$"
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre de la ciudad solo puede contener letras, espacios y guiones."
                )