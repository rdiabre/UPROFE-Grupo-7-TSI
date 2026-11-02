from odoo import models, fields, api

class publicacion(models.Model):
    _name = 'uprofe.publicacion'
    _description = "Publicación científica"
    
    name = fields.Char(string="Código", required=True)
    titulo = fields.Char(string="Título", required=True)
    fecha_publicacion = fields.Datetime(string="Fecha de publicación", autodate=True, required=True)