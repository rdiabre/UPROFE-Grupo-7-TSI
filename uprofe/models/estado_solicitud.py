# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class estado_solicitud(Models.models):
    _name= 'uprofe.estado_solicitud'
    _description = 'Estados de la solicitud'
    _order = 'name asc'

    name = fields.Char(string="Nombre", size=50, required=True)
    descripcion = fields.Text(string="Descripción")