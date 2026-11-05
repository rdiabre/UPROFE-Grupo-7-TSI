# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError

class estado_acuerdo(models.Model):
    _name = 'uprofe.estado_acuerdo'
    _description = 'Estados del Acuerdo'
    _order='name asc'
    
    name = fields.Char(string="Nombre", size=50, required=True)
    descripcion = fields.Text(string="Descripción")
    