# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EstadoLearningAgreement(models.Model):
    _name = 'uprofe.estado_learning_agreement'
    _description = 'Estado de un learning agreement'

    sName = fields.Char(string="Nombre del estado", size=30, required=True)
    sDescripcion = fields.Text(string="Descripción")

    # Descomentar cuando exista LearningAgreement
    # learning_agreement_ids = fields.One2many('uprofe.learning_agreement', 'estado_id', string="Learning agreements")

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
                    "(usad guion bajo para separar palabras, por ejemplo 'pendiente_firma')."
                )
