from odoo import models, fields, api

class grupo_inv(models.Model):
    _name = 'uprofe.grupo_inv'
    _description = 'Grupos de investigación'
    
    name = fields.Char(string="Código del grupo de investigación", required=True)
    nombre = fields.Char(string="Nombre del grupo", required=True)
    fecha_creacion = fields.Datetime(string="Fecha de creación", autodate=True, readonly=True)
    
    departamento_id = fields.Many2one('uprofe.departamento', string="Departamento", required=True)
    laboratorio_id = fields.Many2one('uprofe.laboratorio', string="Laboratorio", required=True)
    proyecto_investigacion_ids = fields.One2many('gym.proyecto_investigacion', 'grupo_inv_id', 'Proyectos')
    linea_investigacion_ids = fields.One2many('gym.linea_investigacion', 'grupo_inv_id', 'Líneas de investigación')