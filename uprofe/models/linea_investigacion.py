from odoo import models, fields, api
from odoo.exceptions import ValidationError

class linea_investigacion(models.Model):
    _name = 'uprofe.linea_investigacion'
    _description = 'Lineas de investigación'
    
    sName = fields.Char(string="Código", required=True)
    sNombre = fields.Char(string="Nombre", required=True)
    sDescripcion = fields.Text(string="Descripción", required=True)
    
    grupo_inv_id = fields.Many2one('uprofe.grupo_inv', string="Grupo de investigación", required=True)
    profesor_ids = fields.Many2many('uprofe.profesor', string="PDIs")
    # Descomentar cuando exista Investigador
    # investigador_ids = fields.Many2many('uprofe.investigador', string="Investigadores")
    
    @api.constrains('sName')
    def _check_name_unico(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('sName', '=ilike', record.sName.strip())]):
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