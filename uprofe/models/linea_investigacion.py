from odoo import models, fields, api

class linea_investigacion(models.Model):
    _name = 'uprofe.linea_investigacion'
    _description = 'Lineas de investigación'
    
    name = fields.Char(string="Código", required=True)
    nombre = fields.Char(string="Nombre", required=True)
    descripcion = fields.Char(string="Descripción", required=True)