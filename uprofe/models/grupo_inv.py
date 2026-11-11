from odoo import models, fields, api
from odoo.exceptions import ValidationError

class grupo_inv(models.Model):
    _name = 'uprofe.grupo_inv'
    _description = 'Grupos de investigación'
    
    sName = fields.Char(string="Código del grupo de investigación", required=True)
    sNombre = fields.Char(string="Nombre del grupo", required=True)
    dFecha_creacion = fields.Datetime(string="Fecha de creación", autodate=True, readonly=True)
    
    # Descomentar cuando existan Departamento y Laboratorio
    departamento_id = fields.Many2one('uprofe.departamento', string="Departamento", required=True)
    # laboratorio_id = fields.Many2one('uprofe.laboratorio', string="Laboratorio", required=True)
    proyecto_investigacion_ids = fields.One2many('uprofe.proyecto_investigacion', 'grupo_inv_id', 'Proyectos')
    linea_investigacion_ids = fields.One2many('uprofe.linea_investigacion', 'grupo_inv_id', 'Líneas de investigación')
    
    @api.constrains('sName')
    def _check_codigo_unico(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('sName', '=ilike', (record.sName or '').strip())]):
                raise ValidationError("Ya existe un grupo con este código, debe ser único")
    
    @api.constrains('sName')
    def _check_codigo_valido(self):
        for record in self:
            if len((record.sName or '').strip()) == 0:
                raise ValidationError("El código no puede estar vacío.")
            
    @api.constrains('sNombre')
    def _check_nombre_valido(self):
        for record in self:
            if len((record.sNombre or '').strip()) == 0:
                raise ValidationError("El nombre del grupo no puede estar vacío.")
            
    # Valida que haya al menos una línea de investigación asociada
    @api.constrains('linea_investigacion_ids')
    def _check_linea_1N(self):
        for record in self:
            if not record.linea_investigacion_ids:
                raise ValidationError("Debe haber al menos una línea de investigación asociada al grupo.")
      