from odoo import models, fields, api
from odoo.exceptions import ValidationError

class publicacion(models.Model):
    _name = 'uprofe.publicacion'
    _description = "Publicación científica"
    
    name = fields.Char(string="Código", required=True)
    titulo = fields.Char(string="Título", required=True)
    fecha_publicacion = fields.Datetime(string="Fecha de publicación", autodate=True, required=True)
    
    proyecto_investigacion_id = fields.Many2one('uprofe.proyecto_investigacion', string="Proyecto de investigacion")
    profesor_ids = fields.Many2many('uprofe.profesor', string="Profesores")
    investigador_ids = fields.Many2many('uprofe.investigador', string="Investigadores")
    
    @api.constrains('name')
    def _check_codigo_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.name, '=', 'name')]):
                raise ValidationError("El código de la publicación ya está utilizado, debe ser único.")
    
    @api.constrains('name')
    def _check_codigo_valido(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El código no puede estar vacío.")