from odoo import models, fields, api
from odoo.exceptions import ValidationError

class linea_investigacion(models.Model):
    _name = 'uprofe.linea_investigacion'
    _description = 'Lineas de investigación'
    
    name = fields.Char(string="Código", required=True)
    nombre = fields.Char(string="Nombre", required=True)
    descripcion = fields.Char(string="Descripción", required=True)
    
    grupo_inv_id = fields.Many2one('uprofe.grupo_inv', string="Grupo de investigación", required=True)
    profesor_ids = fields.One2many('uprofe.profesor', 'linea_investigacion_id', 'Profesor')
    investigador_ids = fields.One2many('uprofe.investigador', 'linea_investigacion_id', 'Investigador')
    
    @api.constrains('name')
    def _check_name_unico(self):
        for record in self:
            if record.search_count([(record.id, '!=', 'id'), (record.name.strip(), '=', 'name')]):
                raise ValidationError("Ya existe una línea con ese código, debe ser único.")
            
    @api.constrains('name')
    def _check_name_valido(self):
        for record in self:
            if len(record.name.strip() == 0):
                raise ValidationError("El código de la línea de investigación no puede estar vacío.")