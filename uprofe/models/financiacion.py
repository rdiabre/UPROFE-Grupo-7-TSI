from odoo import models, fields, api
from odoo.exception import ValidationError

class financiacion(models.Model):
    _name = 'uprofe.financiacion'
    _descripcion = 'Financiación de los proyectos de investigación'
    
    name = fields.Char(string="Código de la financiación", required=True)
    entidad_financiadora = fields.Char(string="Entidad financiadora", required=True)
    # Mirar si se podría asociar financiación con empresa y que empresa tenga una divisa asignada, para poder poner importe de tipo fields.Monetary
    importe = fields.Float(string="Importe", digits="Account", required=True)
    fecha_concesion = fields.Datetime(string="Fecha de concesión", autodate=True, required=True)
    
    proyecto_investigacion_id = fields.Many2one('uprofe.proyecto_investigacion', string="Proyecto de investigación", required=True)
    investigador_ids = fields.Many2many('uprofe.investigador', string="Investigadores")
    
    @api.constrains('name')
    def _check_codigo_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.name, '=', 'name')]):
                raise ValidationError("Ya existe una financiación con este código, debe ser único.")
    
    @api.constrains('name')
    def _check_codigo_valido(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El código no puede estar vacío.")
            
    @api.constrains('entidad_financiadora')
    def _check_entidad_valida(self):
        for record in self:
            if len(record.entidad_financiadora.strip()) == 0:
                raise ValidationError("La entidad financiadora no puede estar vacía.")
            
    @api.constrains('importe')
    def _check_importe_valido(self):
        for record in self:
            if record.importe <= 0:
                raise ValidationError("El importe no puede ser 0 o negativo")
            
    @api.onchange('importe')
    def _onchange_importe_valido(self):
        if self.importe <= 0:
            return {
                'value': {'importe': 1000},
                'warning': {
                    'title': "Importe no válido",
                    'message': "El importe no puede ser menor o igual a 0."
                }
            }