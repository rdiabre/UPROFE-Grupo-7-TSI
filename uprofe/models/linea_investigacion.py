from odoo import models, fields, api

class linea_investigacion(models.Model):
    _name = 'uprofe.linea_investigacion'
    _description = 'Lineas de investigación'
    
    name = fields.Char(string="Código", required=True)
    nombre = fields.Char(string="Nombre", required=True)
    descripcion = fields.Char(string="Descripción", required=True)
    
    grupo_inv_id = fields.Many2one('uprofe.grupo_inv', string="Grupo de investigación", required=True)
    profesor_ids = fields.One2many('uprofe.profesor', 'linea_investigacion_id', 'Profesor')
    investigador_ids = fields.One2many('uprofe.investigador', 'linea_investigacion_id', 'Investigador')