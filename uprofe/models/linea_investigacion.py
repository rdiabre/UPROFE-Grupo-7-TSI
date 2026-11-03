from odoo import models, fields, api
from odoo.exceptions import ValidationError

class linea_investigacion(models.Model):
    _name = 'uprofe.linea_investigacion'
    _description = 'Lineas de investigación'
    
    name = fields.Char(string="Código", required=True)
    nombre = fields.Char(string="Nombre", required=True)
    descripcion = fields.Text(string="Descripción", required=True)
    
    grupo_inv_id = fields.Many2one('uprofe.grupo_inv', string="Grupo de investigación", required=True)
    profesor_ids = fields.One2many('uprofe.profesor', 'linea_investigacion_id', 'Profesor')
    investigador_ids = fields.One2many('uprofe.investigador', 'linea_investigacion_id', 'Investigador')
    
    @api.constrains('name')
    def _check_name_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.name.strip(), '=ilike', 'name')]):
                raise ValidationError("Ya existe una línea con ese código, debe ser único.")
            
    @api.constrains('name')
    def _check_name_valido(self):
        for record in self:
            if len(record.name.strip() == 0):
                raise ValidationError("El código de la línea de investigación no puede estar vacío.")
    
    @api.constrains('nombre')
    def _check_nombre_valido(self):
        for record in self:
            if len(record.nombre.strip() == 0):
                raise ValidationError("El nombre de la línea de investigación no puede estar vacío.")
    
    @api.constrains('descripcion')
    def _check_nombre_valido(self):
        for record in self:
            if len(record.descripcion.strip() == 0):
                raise ValidationError("La descripción de la línea de investigación no puede estar vacía.")
            
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