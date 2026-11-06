from odoo import models, fields, api
from odoo.exceptions import ValidationError

class linea_investigacion(models.Model):
    _name = 'uprofe.linea_investigacion'
    _description = 'Lineas de investigación'
    
    sName = fields.Char(string="Código", required=True)
    sNombre = fields.Char(string="Nombre", required=True)
    sDescripcion = fields.Text(string="Descripción", required=True)
    
    iGrupo_inv_id = fields.Many2one('uprofe.grupo_inv', string="Grupo de investigación", required=True)
    lProfesor_ids = fields.One2many('uprofe.profesor', 'iLinea_investigacion_id', 'Profesor')
    lInvestigador_ids = fields.One2many('uprofe.investigador', 'iLinea_investigacion_id', 'Investigador')
    
    @api.constrains('sName')
    def _check_name_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.name.strip(), '=ilike', 'sName')]):
                raise ValidationError("Ya existe una línea con ese código, debe ser único.")
            
    @api.constrains('sName')
    def _check_name_valido(self):
        for record in self:
            if len(record.sName.strip() == 0):
                raise ValidationError("El código de la línea de investigación no puede estar vacío.")
    
    @api.constrains('sNombre')
    def _check_nombre_valido(self):
        for record in self:
            if len(record.sNombre.strip() == 0):
                raise ValidationError("El nombre de la línea de investigación no puede estar vacío.")
    
    @api.constrains('sDescripcion')
    def _check_nombre_valido(self):
        for record in self:
            if len(record.sDescripcion.strip() == 0):
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