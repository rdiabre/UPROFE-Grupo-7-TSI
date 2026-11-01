from odoo import models, fields, api
from odoo.exceptions import ValidationError

class grupo_inv(models.Model):
    _name = 'uprofe.grupo_inv'
    _description = 'Grupos de investigación'
    
    name = fields.Char(string="Código del grupo de investigación", required=True)
    nombre = fields.Char(string="Nombre del grupo", required=True)
    fecha_creacion = fields.Datetime(string="Fecha de creación", autodate=True, readonly=True)
    
    departamento_id = fields.Many2one('uprofe.departamento', string="Departamento", required=True)
    laboratorio_id = fields.Many2one('uprofe.laboratorio', string="Laboratorio", required=True)
    proyecto_investigacion_ids = fields.One2many('uprofe.proyecto_investigacion', 'grupo_inv_id', 'Proyectos')
    linea_investigacion_ids = fields.One2many('uprofe.linea_investigacion', 'grupo_inv_id', 'Líneas de investigación')
    
    @api.constrains('name')
    def _check_codigo_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.name.strip(), '=', 'name')]):
                raise ValidationError("Ya existe un grupo con este código, debe ser único")
    
    @api.constrains('name')
    def _check_codigo_valido(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El código no puede estar vacío.")
            
    @api.constrains('nombre')
    def _check_nombre_valido(self):
        for record in self:
            if len(record.nombre.strip()) == 0:
                raise ValidationError("El nombre del grupo no puede estar vacío.")
            
    # Valida que haya al menos una línea de investigación asociada
    @api.constrains('linea')
    def _check_linea_1N(self):
        for record in self:
            if not record.linea_investigacion_ids:
                raise ValidationError("Debe haber al menos una línea de investigación asociada al grupo.")
      
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._strip_string_values(vals)
        return super().create(vals_list)
      
    def write(self, vals):
        self._strip_string_values(vals)
        return super().write(vals)
          
    def _strip_string_values(self, vals):
        for field_name, val in vals.items():
            if isinstance(val, str):
                field = self._fields.get(field_name)
                if field and field.type in ('char', 'text'):
                    vals[field_name] = val.strip()
        return vals