from odoo import models, fields, api
from odoo.exceptions import ValidationError

class financiacion(models.Model):
    _name = 'uprofe.financiacion'
    _descripcion = 'Financiación de los proyectos de investigación'
    
    sName = fields.Char(string="Código de la financiación", required=True)
    fImporte = fields.Float(string="Importe", digits="Account", required=True)
    dFecha_concesion = fields.Datetime(string="Fecha de concesión", autodate=True, required=True)
    
    proyecto_investigacion_id = fields.Many2one('uprofe.proyecto_investigacion', string="Proyecto de investigación", required=True)
    empresa_id = fields.Many2one('uprofe.empresa', string="Empresa financiadora", required=True)
    persona_ids = fields.Many2many('uprofe.persona', string="Personas financiadas")
    
    @api.constrains('sName')
    def _check_codigo_unico(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('sName', '=ilike', record.sName.strip())]):
                raise ValidationError("Ya existe una financiación con este código, debe ser único.")
    
    @api.constrains('sName')
    def _check_codigo_valido(self):
        for record in self:
            if len(record.sName.strip()) == 0:
                raise ValidationError("El código no puede estar vacío.")
            
    @api.constrains('fImporte')
    def _check_importe_valido(self):
        for record in self:
            if record.fImporte <= 0:
                raise ValidationError("El importe no puede ser 0 o negativo")
            
    @api.onchange('fImporte')
    def _onchange_importe_valido(self):
        if self.fImporte <= 0:
            return {
                'value': {'fImporte': 1000},
                'warning': {
                    'title': "Importe no válido",
                    'message': "El importe no puede ser menor o igual a 0."
                }
            }
