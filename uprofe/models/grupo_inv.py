from odoo import models, fields, api

class grupo_inv(models.Model):
    _name = 'uprofe.grupo_inv'
    _description = 'Grupos de investigación'
    
    name = fields.Char(string="Código del grupo de investigación", required=True)
    nombre = fields.Char(string="Nombre del grupo", required=True)
    fecha_creacion = fields.Datetime(string="Fecha de creación", autodate=True, readonly=True)