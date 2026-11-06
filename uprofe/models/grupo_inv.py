from odoo import models, fields, api
from odoo.exceptions import ValidationError

class grupo_inv(models.Model):
    _name = 'uprofe.grupo_inv'
    _description = 'Grupos de investigación'
    
    sName = fields.Char(string="Código del grupo de investigación", required=True)
    sNombre = fields.Char(string="Nombre del grupo", required=True)
    dFecha_creacion = fields.Datetime(string="Fecha de creación", autodate=True, readonly=True)
    
    iDepartamento_id = fields.Many2one('uprofe.departamento', string="Departamento", required=True)
    iLaboratorio_id = fields.Many2one('uprofe.laboratorio', string="Laboratorio", required=True)
    lProyecto_investigacion_ids = fields.One2many('uprofe.proyecto_investigacion', 'grupo_inv_id', 'Proyectos')
    lLinea_investigacion_ids = fields.One2many('uprofe.linea_investigacion', 'grupo_inv_id', 'Líneas de investigación')
    
    @api.constrains('name')
    def _check_codigo_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.sName.strip(), '=ilike', 'name')]):
                raise ValidationError("Ya existe un grupo con este código, debe ser único")
    
    @api.constrains('name')
    def _check_codigo_valido(self):
        for record in self:
            if len(record.sName.strip()) == 0:
                raise ValidationError("El código no puede estar vacío.")
            
    @api.constrains('nombre')
    def _check_nombre_valido(self):
        for record in self:
            if len(record.sNombre.strip()) == 0:
                raise ValidationError("El nombre del grupo no puede estar vacío.")
            
    # Valida que haya al menos una línea de investigación asociada
    @api.constrains('linea')
    def _check_linea_1N(self):
        for record in self:
            if not record.lLinea_investigacion_ids:
                raise ValidationError("Debe haber al menos una línea de investigación asociada al grupo.")
      