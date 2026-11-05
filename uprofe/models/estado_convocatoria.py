# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class estado_convocatoria(models.Model):
    _name = 'uprofe.estado_convocatoria'
    _description = 'Estados de la convocatoria'
    _order = 'name asc'

    name = fields.Char(string="Nombre", size=50, required=True)
    descripcion = fields.Text(string="Descripción")