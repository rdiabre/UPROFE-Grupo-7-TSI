from odoo import models, fields, api

class proyecto_investigacion(models.Model):
    _name = 'uprofe.proyecto_investigacion'
    _description = "Proyecto de investigación"
    
    name = fields.Char(string="Código", required=True)
    titulo = fields.Char(string="Título", required=True)
    # Pasar más adelante a valor autocalculado por la suma de la financiación asociada
    presupuesto = fields.Float(string="Presupuesto", digits="Account", required=True)
    fecha_inicio = fields.Datetime(string="Fecha de inicio", autodate=True, required=True)
    fecha_fin = fields.Datetime(string="Fecha de fin", required=True)
    
    grupo_inv_id = fields.Many2one('uprofe.grupo_inv', string="Grupo de investigación", required=True)
    financiacion_ids = fields.One2many('uprofe.financiacion', 'proyecto_investigacion_id', "Financiaciones")
    publicacion_ids = fields.One2many('uprofe.publicacion', 'proyecto_investigacion_id', "Publicaciones")