from odoo import models, fields, api
from odoo.exceptions import ValidationError

class patente(models.Model):
    _name = 'uprofe.patente'
    _description = "Patente"
    _inherits = {'uprofe.publicacion': 'iPublicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete="cascade")