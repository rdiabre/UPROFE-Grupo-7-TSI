from odoo import models, fields, api

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