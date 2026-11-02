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
            
    @api.constrains('titulo')
    def _check_titulo_valido(self):
        for record in self:
            if len(record.titulo.strip()) == 0:
                raise ValidationError("El título no puede estar vacío.")

    def write(self, vals):
        self._strip_string_values(vals)
        return super().write(vals)
        
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._strip_string_values(vals)
        return super().create(vals_list)
        
    def _strip_string_values(self, vals):
        for field_name, val in vals.items():
            if isinstance(val, str):
                field = self._fields.get(field_name)
                if field and field.type in ('char', 'text'):
                    vals[field_name] = val.strip()
        return vals