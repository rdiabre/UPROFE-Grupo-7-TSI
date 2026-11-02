from odoo import models, fields, api

class publicacion(models.Model):
    _name = 'uprofe.publicacion'
    _description = "Publicación científica"
    
    name = fields.Char(string="Código", required=True)
    titulo = fields.Char(string="Título", required=True)
    fecha_publicacion = fields.Datetime(string="Fecha de publicación", autodate=True, required=True)
    
    proyecto_investigacion_id = fields.Many2one('uprofe.proyecto_investigacion', string="Proyecto de investigacion")
    profesor_ids = fields.Many2many('uprofe.profesor', string="Profesores")
    investigador_ids = fields.Many2many('uprofe.investigador', string="Investigadores")