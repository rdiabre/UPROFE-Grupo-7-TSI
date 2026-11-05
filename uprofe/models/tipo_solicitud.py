# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class tipo_solicitud(models.Model):
    _name="uprofe.tipo_solicitud"
    _description="Tipos de Solicitud"
    _order="name asc"
    
    name = fields.Char(string="Nombre", size=50, required=True)
    descripcion=fields.Text(string="Descripción")
                       
    
    