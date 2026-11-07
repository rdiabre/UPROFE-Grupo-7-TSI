from odoo import models, fields, api
from odoo.exceptions import ValidationError

class patente(models.Model):
    _name = 'uprofe.patente'
    _description = "Patente"
    _inherits = {'uprofe.publicacion': 'iPublicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete="cascade")
    
    sNumero_patente(string="Número de patente", required=True)
    dFecha_concesion(string="Fecha de concesión", autodate=True, required=True)